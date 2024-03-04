# Imports
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import XCom
import datetime as dt
from igdb_module import TwitchAPIClient as TC

# Define a function to save fetched data to XCom
def save_data_to_xcom(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_push(key='igdb_data', value=TC.fetch_data_from_igdb())
    return data

# Define dag arguments
default_args = {
    'owner': 'Walker Martin',
    'depends_on_past': 'False',
    'start_date': dt.datetime(2024,3,4),
    'email': 'walker.educs@gmail.com',
    'email_on_failure': 'False',
    'email_on_retry': 'False',
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}
# Create dag definitions
with DAG(
    dag_id='GameData_ETL',
    schedule_interval = None,
    default_args = default_args,
    description = "Airflow Pipeline: Video Game Review Data for game data search app.",
)as dag:
    # extract data from igdb api
    extract_data_from_igdb = PythonOperator(
        task_id = 'extract_data_from_igdb',
        python_callable = TC.fetch_data_from_igdb
    )
    
    save_to_xcom = PythonOperator(
        task_id = 'save_to_xcom',
        python_callable = save_data_to_xcom,
        provided_context=True
    )
    
extract_data_from_igdb >> save_to_xcom