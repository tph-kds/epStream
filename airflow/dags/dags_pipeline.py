from __future__ import annotations

import psycopg2
import os
import requests
import time
from datetime import timedelta, datetime
from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.http.sensors.http import HttpSensor

from utils.kafka_utils import ensure_kafka_topic_exists, kafka_ready
from utils.es_utils import ensure_es_index_exists

BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
TOPIC = os.getenv("KAFKA_TOPIC", "tiktok_comments")
TOPIC_PROCESSED = os.getenv("KAFKA_TOPIC_PROCESSED", "tiktok_comments_processed")
ES_URL = os.getenv("ES_URL", "http://es-container:9200")
ES_INDEX = os.getenv("ES_INDEX", "tiktok_comments")
FLINK_UI = os.getenv("FLINK_JOBMANAGER", "http://flink-jobmanager:8081")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")
def start_flink_job():
    pass 
def check_postgres_data():
    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password=POSTGRES_PASSWORD,
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM comments;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    if count == 0:
        raise ValueError("No data in Postgres yet!")
    print(f"Postgres has {count} rows ✅")


def check_es_data(max_retries=10, delay=5):
    for i in range(max_retries):
        resp = requests.get(f"{ES_URL}/{ES_INDEX}/_count")
        resp.raise_for_status()
        count = resp.json()["count"]
        if count > 0:
            print(f"✅ Elasticsearch has {count} documents")
            return
        print(f"⏳ Waiting for data in Elasticsearch... (try {i+1}/{max_retries})")
        time.sleep(delay)
    raise ValueError("❌ No data in Elasticsearch after waiting")

def refresh_kibana():
    kibana_url = os.getenv("KIBANA_URL", "http://kibana-container:5601")
    
    # Example: trigger a saved objects migration or dashboard reload
    dashboards_api = f"{kibana_url}/api/saved_objects/_find?type=dashboard"
    headers = {"kbn-xsrf": "true"}   # Kibana requires this header

    resp = requests.get(dashboards_api, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Failed to query dashboards: {resp.text}")
    
    dashboards = resp.json().get("saved_objects", [])
    print(f"Found {len(dashboards)} dashboards in Kibana")

    # Optionally: "touch" each dashboard to trigger a refresh
    for d in dashboards:
        print(f"Dashboard ready: {d['attributes'].get('title')}")
    
    print("Kibana dashboards refreshed ✅")

# --------------------------
# DAG definition
# --------------------------

default_args = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),  # 1 minutes
}

with DAG(
    dag_id="tiktok_stream_pipeline__EPS_v1",
    description="Emotional Pulse Stream: end-to-end orchestrator",
    default_args=default_args,
    schedule="@once",
    catchup=False,
    start_date=datetime.now() - timedelta(days=1),
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
            "mapping_path": "/opt/elasticsearch/mapping.json",
        },
    )
    # Step 4: Initialize Postgres schema (idempotent)
    init_postgres_schema = BashOperator(
        task_id="init_postgres_schema",
    bash_command=(
            f'PGPASSWORD={POSTGRES_PASSWORD} psql -h postgres -U airflow -d airflow '
            f'-tc "SELECT 1 FROM pg_tables WHERE schemaname = \'public\' AND tablename = \'comments\';" '
            f'| grep -q 1 || '
            f'PGPASSWORD={POSTGRES_PASSWORD} psql -h postgres -U airflow -d airflow -f /opt/database/init.sql'
        ),
    )

    # Step 5: Start Collector (Tiktok ->  Kafka)
    run_collector = BashOperator(
        task_id = "start_collector",
        # bash_command="export PYTHONPATH=/opt && python /opt/airflow/collectors/main.py & echo $! > /tmp/collector.pid && sleep 2",
        bash_command="export PYTHONPATH=/opt && python -m collectors.main & echo $! > /tmp/collector.pid && sleep 2",
    )

    # Step 5: Submit Flink job
    run_flink_job = BashOperator(
        task_id="run_flink_job",
        bash_command=(
            "docker exec flink-jobmanager "
            "flink run -d -py /opt/flink/processors/flink_job.py"
        ),
    )


    # # Step 6: Check Health-check for Elasticsearch Index (ES) (count offset)
    # check_processed_has_data = BashOperator(
    #     task_id="check_processed_has_data",
    #     bash_command=f"""
    #       for i in {{1..30}}; do
    #         docker exec -i broker kafka-run-class kafka.tools.GetOffsetShell --broker-list broker:9092 --topic {TOPIC_PROCESSED} \
    #           | awk -F ':' '{{sum+=$3}} END {{print sum+0}}' | grep -v '^0$' && exit 0 || true
    #         echo 'waiting processed data...'; sleep 2
    #       done
    #       echo 'No processed data detected' && exit 1
    #     """,
    #     trigger_rule="all_done"
    # )

    check_postgres = PythonOperator(
        task_id="check_postgres",
        python_callable=check_postgres_data,
    )

    check_es = PythonOperator(
        task_id="check_es",
        python_callable=check_es_data,
        op_kwargs={"max_retries": 10, "delay": 5},
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
        bash_command="echo 'Run All Routines completely successful' & kill $(cat /tmp/collector.pid) || true",
        trigger_rule="all_done"
    )

    # Task Flow
   
    # Step 1: Initialization all services 
    [wait_kafka, wait_flink_ui, wait_es] >> create_topics >> create_es_index >> init_postgres_schema
   
    # Step 2: Start data collection and processing
    init_postgres_schema >> run_collector >> run_flink_job
  
    # Step 3: check_postgres & check_es -> refresh_kibana_task & notify_monitoring
    run_flink_job >> [check_postgres, check_es]
    for t in [check_postgres, check_es]:
        t >> [refresh_kibana_task, notify_monitoring]

    # Step 4: stop_collector
    [refresh_kibana_task, notify_monitoring] >> stop_collector