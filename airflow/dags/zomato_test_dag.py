from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="zomato_dbt_test",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["zomato", "dbt", "learning"],
) as dag:

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command="cd /opt/airflow/dbt && dbt debug",
    )
