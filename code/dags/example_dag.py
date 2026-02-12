"""Example Airflow DAG."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def hello_world():
    print("Hello from Airflow!")


with DAG(
    'example_dag',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:
    task = PythonOperator(
        task_id='hello_task',
        python_callable=hello_world,
    )
