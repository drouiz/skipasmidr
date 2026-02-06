"""
Ejemplo de DAG para Airflow.
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


def print_hello():
    print("Hello from Airflow!")
    return "Hello!"


with DAG(
    dag_id="example_hello",
    description="DAG de ejemplo",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["example"],
) as dag:

    task_hello = PythonOperator(
        task_id="print_hello",
        python_callable=print_hello,
    )

    task_date = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    task_hello >> task_date
