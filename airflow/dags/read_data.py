import logging
import os
import random
import pandas as pd
from datetime import timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from utils.validate import validate, filter_expectations_result, copy_dirs, save_df_to_folder
from utils.data_errors import save_data_errors

FOLDER_A = 'data/folder_A/'
FOLDER_B = 'data/folder_B/'
FOLDER_C = 'data/folder_C/'
TMP_FOLDER = 'data/_tmp/'

with DAG(
    dag_id='read_data',
    schedule_interval=timedelta(minutes=1),
    start_date=days_ago(n=0, hour=1),
    catchup=False,
    tags=['example'],
) as read_dag:

    @task
    def get_data_from_folder_A():
        logging.info('First task')
        file = random.choice(os.listdir(FOLDER_A))
        logging.info(file)
        # if file:
        #     copy_dirs(FOLDER_A, TMP_FOLDER, file)
        return file

    @task
    def validate_data_quality(filename):
        logging.info('Validating data quality')
        file_path = os.path.join(FOLDER_A, filename)

        validation_result = validate(file_path)
        failed_rows, desc = filter_expectations_result(
            validation_result.to_json_dict())

        logging.info(f'Data Validated -> failed rows = {failed_rows}')

        desc = desc.replace('_FILENAME_', filename)

        df = pd.read_csv(file_path)
        if set(failed_rows) == set(list(df['Id'].values)):
            # all rows with data problems
            save_df_to_folder(df, FOLDER_B, f'failed_{filename}')
            save_data_errors(filename, desc)
        elif failed_rows == []:  # no data problems found
            df = df[df.columns[1:]].astype(int)
            save_df_to_folder(df, FOLDER_C, f'working_{filename}')
        elif failed_rows != []:  # some rows have problems
            failed_df = df[df['Id'].isin(failed_rows)]
            working_df = df[~df['Id'].isin(failed_rows)]
            working_df = working_df[working_df.columns[1:]].astype(int)
            # final_df['TotRmsAbvGrd'] = final_df['TotRmsAbvGrd'].astype(int)
            save_df_to_folder(working_df, FOLDER_C, f'working_{filename}')
            save_df_to_folder(failed_df, FOLDER_B, f'failed_{filename}')
            save_data_errors(filename, desc)

    filename = get_data_from_folder_A()
    if filename:
        validate_data_quality(filename)
