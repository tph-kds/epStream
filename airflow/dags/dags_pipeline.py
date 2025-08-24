import os
import requests


from __future__ import annotations
from datetime import timedelta, datetime
from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.utils.dates import days_ago
from airflow.sensors.http_sensor import HttpSensor

from utils.kafka_utils import ensure_kafka_topic_exists, kafka_ready
from utils.es_utils import ensure_es_index_exists

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "tiktok_comments")
TOPIC_PROCESSED = os.getenv("KAFKA_TOPIC_PROCESSED", "tiktok_comments_processed")
ES_URL = os.getenv("ES_URL", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX", "tiktok_comments")
FLINK_UI = os.getenv("FLINK_JOBMANAGER", "http://flink-jobmanager:8081")

def start_flink_job():
    pass 

# --------------------------
# DAG definition
# --------------------------

default_args = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),  # 1 minutes
}

with DAG(
    dag_id="tiktok_stream_pipeline - EPS_v1",
    description="Emotional Pulse Stream: end-to-end orchestrator",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
    start_date=days_ago(1),
    max_active_runs=1,
    tags=["tiktok", "etl", "streaming", "data-pipeline"],
) as dag:

    # Step 1: Ensure Kafka & Flink UI & Elasticsearch are ready
    wait_kafka = PythonOperator(
        task_id="wait_kafka",
        python_callable=kafka_ready,
        op_kwargs={"broker": BROKER, "topic": TOPIC},
    )

    wait_flink_ui = BashOperator(
        task_id="wait_flink_ui",
        bash_command=f"""
            for i in {{1..60}}; do
                curl -fsS {FLINK_UI}/taskmanagers && exit 0 || true
                echo 'waiting flink...'; sleep 2
            done
            echo 'Flink UI not ready' && exit 1
        """
    )

    wait_es = BashOperator(
        task_id="wait_eslasticsearch",
        bash_command=f"""
            for i in {{1..60}}; do
                curl -fsS {ES_URL} && exit 0 || true
                echo 'waiting elasticsearch...'; sleep 2
            done
            echo 'Elasticsearch not ready' && exit 1
        """
    )
    # Step 2:  Ensure Kafka topic exists (if not, create it)
    create_topics = PythonOperator(
        task_id="create_kafka_topics",
        python_callable=ensure_kafka_topic_exists,
        op_kwargs={
            "broker": BROKER,
            "topics": [{
                "name" : TOPIC, "partitions": 3, "replication_factor": 1
            },
            {
                "name": TOPIC_PROCESSED, "partitions": 3, "replication_factor": 1
            }],
        },
    )
    # Step 3: Create ES index & mapping (idempotent)
    create_es_index = PythonOperator(
        task_id="create_es_index",
        python_callable= ensure_es_index_exists,
        op_kwargs={
            "es_url": ES_URL,
            "index": ES_INDEX,
            "mapping_path": "/opt/airflow/mapping.json",
        },
    )
    # Step 4: Start Collector (Tiktok ->  Kafka)
    run_collector = BashOperator(
        task_id = "start_collector",
        bash_command="python /opt/airflow/dags/collector.py & sleep 2",
    )

    # Step 5: Submit Flink job
    run_flink_job = PythonOperator(
        task_id="run_flink_job",
        python_callable="""
            docker exec -i flink-jobmanager bash -lc '
                flink run -d -py /opt/processor/flink_job.py
            '
        """
    )

    # Step 6: Check Health-check for Elasticsearch Index (ES) (count offset)
    check_processed_has_data = BashOperator(
        task_id="check_processed_has_data",
        bash_command=f"""
          for i in {{1..30}}; do
            docker exec -i broker kafka-run-class kafka.tools.GetOffsetShell --broker-list broker:9092 --topic {TOPIC_PROCESSED} \
              | awk -F ':' '{{sum+=$3}} END {{print sum+0}}' | grep -v '^0$' && exit 0 || true
            echo 'waiting processed data...'; sleep 2
          done
          echo 'No processed data detected' && exit 1
        """,
        trigger_rule="all_done"
    )

    # Step 7: Load Data into PostgreSQL (ETL / SQL scripts)
    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command="psql -h postgres -U user -d mydb -f /opt/database/schema.sql",
    )

    # Step 8: Refresh Kibana dashboards
    refresh_kibana_task = PythonOperator(
        task_id="refresh_kibana",
        python_callable=refresh_kibana,
    )

    # Step 9: (Optional) Notify monitoring system (Grafana/Slack)
    notify_monitoring = BashOperator(
        task_id="notify_monitoring",
        bash_command="echo 'Pipeline completed!'",
    )

    # Step 10: Stop collector after processing
    stop_collector = BashOperator(
        task_id="stop_collector",        
        bash_command="kill $(cat /tmp/collector.pid) || true",
        trigger_rule="all_done"
    )

    # Task Flow
    wait_kafka >> [wait_flink_ui, wait_es]
    [wait_kafka, wait_flink_ui, wait_es] >> create_topics >> create_es_index >> run_collector >> run_flink_job >> load_postgres >> check_processed_has_data >> refresh_kibana_task >> notify_monitoring >> stop_collector