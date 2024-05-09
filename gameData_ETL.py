# imports
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import datetime as dt

# define dag arguments/instantiate dag
default_args = {
    'owner': 'dummy_owner',
    'start_date': dt.datetime(2024, 5, 7),
    'email': "dummy_email@example.com",
    'email_on_failure': 'True',
    'email_on_retry': 'True',
    'retries': 1,
    'retry_delay':dt.timedelta(minutes=5),
}

# create dag definitions
with DAG(
    dag_id = 'ETL_toll_data',
    schedule_interval = dt.timedelta(days=1),
    default_args = default_args,
    description = "Apache Airflow Final Assignment",
) as dag:
    
    # Task 1: Extract Data From Sales CSV
    
    # Task 2: Extract Data From IGDB
    extract_igdb_data = PythonOperator(
        task_id = 'igdb_extract',
        
    )
    
    # Task 3: Extract Data From IGN
    
    # Task 4: Extract Data From Metacritic
    
    # merge dataframes
    
    
    # pipeline, run extract tasks in parallell then on completion merge dataframes into one, then ouput a final csv