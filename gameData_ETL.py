# imports
from airflow.decorators import dag, task
from airflow.operators.python_operator import task_group
from airflow.utils.dates import days_ago
from game_data import GameData 

default_args = {
    'owner': 'Walker Martin',
}
@dag(default_args=default_args, schedule_interval=None, start_date=days_ago(2))
def game_data_ETL():
    """
    This is a game data ETL aggregator pipieline using taskflow.
    It facilitates the execution of multiple extraction functions,
    uses paralell processing then merges the dataframes together and exports as a csv.
    """
    
    # Extract Sales
    @task()
    def extractSales():
        gd = GameData()
        gd.get_sales_data()
        return gd.get_sales_df()
    
    # Extract IGDB
    @task()
    def extractIGDB():
        gd = GameData()
        gd.get_igdb_data()
        return gd.get_igdb_df()
    
    # Extract IGN
    @task()
    def extractIGN():
        gd = GameData()
        gd.get_ign_data()
        return gd.get_ign_df()
    
    # Extract Metacritic
    @task()
    def extractMeta():
        gd = GameData()
        gd.get_metacritic_data()
        return gd.get_metacritic_df()

        
    @task()
    def transform(sales_df, igdb_df, ign_df, meta_df):
        # call the merge functions using the object passed from xcom
        gd = GameData()
        
        # Set df values
        gd.set_sales_df(sales_df)
        gd.set_igdb_df(igdb_df)
        gd.set_ign_df(ign_df)
        gd.set_metacritic_df(meta_df)
        
        # call merge function
        gd.merge_data()
        
        # this leaves us with the finished dataframe
        return gd.get_main_df()
    
    @task()
    def load(main_df):
        # pass the datafrme and load it to an export csv
        main_df.to_csv('transformed_game_data.csv', index=False)
        
    # Define the task dependencies
    with task_group("extraction_tasks") as extract_tasks:
        sales_df = extractSales()
        igdb_df = extractIGDB()
        ign_df = extractIGN()
        meta_df = extractMeta()
        
    merged_df = transform(sales_df, igdb_df, ign_df, meta_df)
    load(merged_df)
