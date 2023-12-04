import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from utils.validate import validate, log_failed_expectations


FOLDER_A = 'data/folder_A/'
FOLDER_B = 'data/folder_B/'
FOLDER_C = 'data/folder_C/'

with DAG(
    dag_id='read_data',
    schedule_interval=timedelta(minutes=1),
    start_date=days_ago(n=0,hour=1),
    catchup=False,
    tags=['example'],
) as read_dag:

    @task
    def get_data_from_folder_A():
        logging.info('First task')
        df = []
        files = sorted(os.listdir(FOLDER_A), key=len)
        logging.info(files)
        if files:
            filename = files[0]
            file_path = os.path.join(FOLDER_A, filename)
            df = pd.read_csv(file_path)
        return df

    @task
    def validate_data_quality(df : pd.DataFrame):
        df['TotRmsAbvGrd'][0] = None
        df['TotRmsAbvGrd'][1] = None
        logging.info('Validating data quality')
        validation_result = validate(df)
        info = log_failed_expectations(validation_result.to_json_dict()) 
    
    df = get_data_from_folder_A()
    validate_data_quality(df)




# if not os.path.exists(FOLDER_C):
#     os.makedirs(FOLDER_C)
# logging.info(f'Saving file {filename} in folder C')
# src_path = os.path.join(FOLDER_A, filename)
# dst_path = os.path.join(FOLDER_C, filename)
# os.rename(src_path,dst_path)
