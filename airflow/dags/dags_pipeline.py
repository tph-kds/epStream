from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import requests

def start_flink_job():
    pass 

# --------------------------
# DAG definition
# --------------------------

default_args = {
    "owner": "data-eng",
    "retries": 1
}

with DAG(
    dag_id="tiktok_stream_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    start_date=days_ago(1),
    tags=["tiktok"]
) as dag:

    # Step 1: Start Collector (Tiktok ->  Kafka)
    run_collector = BashOperator(
        task_id = "run_collector",
        bash_command="python /opt/airflow/dags/collector.py",
    )

    # Step 2: Submit Flink job
    run_flink_job = PythonOperator(
        task_id="run_flink_job",
        python_callable=start_flink_job
    )

    # Step 3: Load Data into PostgreSQL (ETL / SQL scripts)
    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command="psql -h postgres -U user -d mydb -f /opt/database/schema.sql",
    )

    # Step 4: Refresh Kibana dashboards
    refresh_kibana_task = PythonOperator(
        task_id="refresh_kibana",
        python_callable=refresh_kibana,
    )

    # Step 5: (Optional) Notify monitoring system (Grafana/Slack)
    notify_monitoring = BashOperator(
        task_id="notify_monitoring",
        bash_command="echo 'Pipeline completed!'",
    )

    # Task Flow
    run_collector >> run_flink_job >> load_postgres >> refresh_kibana_task >> notify_monitoring