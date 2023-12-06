import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago

from utils.validate import validate, filter_expectations_result, move_dirs, save_df_to_folder
from utils.data_errors import save_data_errors 


FOLDER_A = 'data/folder_A/'
FOLDER_B = 'data/folder_B/'
FOLDER_C = 'data/folder_C/'
TMP_FOLDER = 'data/_tmp/'

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
        filename = ''
        if files:
            filename = files[0]
            move_dirs(FOLDER_A, TMP_FOLDER, filename)
        return filename 

    @task
    def validate_data_quality(filename):
        logging.info('Validating data quality')
        if filename == '':
            return []

        file_path = os.path.join(TMP_FOLDER, filename)
        df = pd.read_csv(file_path)
        df_rows = list(df['Id'].values)

        validation_result = validate(df)
        failed_rows, desc = filter_expectations_result(validation_result.to_json_dict()) 

        logging.info(f'Data Validated -> failed rows = {failed_rows}')
        
        desc = desc.replace('_FILENAME_',filename)

        if set(failed_rows) == set(df_rows): # all rows with data problems 
            save_df_to_folder(df, FOLDER_B, f'failed_{filename}')
            save_data_errors(filename, desc)     
        elif failed_rows == []: # no data problems found
            save_df_to_folder(df, FOLDER_C, f'workig_{filename}')
        elif failed_rows != []: # some rows have problems
            failed_df = df[df['Id'].isin(failed_rows)]
            working_df = df[~df['Id'].isin(failed_rows)]
            save_df_to_folder(working_df, FOLDER_C, f'working_{filename}')
            save_df_to_folder(failed_df,FOLDER_B, f'failed_{filename}')
            save_data_errors(filename, desc) 

        return failed_rows
    
    filename = get_data_from_folder_A()
    validate_data_quality(filename)
    
