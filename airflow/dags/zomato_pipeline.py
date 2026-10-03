from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="zomato_dbt_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["zomato", "dbt", "ai", "pipeline"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run",
    )

    enrich_reviews = BashOperator(
        task_id="enrich_reviews",
        bash_command="cd /opt/airflow && python /opt/airflow/ai/enrich_reviews.py",
    )

    dbt_build_ai = BashOperator(
        task_id="dbt_build_ai",
        bash_command="cd /opt/airflow/dbt && dbt build --select tag:ai",
    )

    dbt_run >> enrich_reviews >> dbt_build_ai