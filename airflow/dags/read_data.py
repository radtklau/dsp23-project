import logging
import os
import pandas as pd
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago


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
        files = os.listdir(FOLDER_A)
        logging.info(files)
        filename=''
        if files:
            filename = files[0]
            file_path = os.path.join(FOLDER_A, filename)
        return filename

    @task
    def validate_data_quality(filename):
        logging.info('Second task')
        # TODO: data quality validation ...
        if not os.path.exists(FOLDER_C):
            os.makedirs(FOLDER_C)

        logging.info(f'Saving file {filename} in folder C')
        src_path = os.path.join(FOLDER_A, filename)
        dst_path = os.path.join(FOLDER_C, filename)
        os.rename(src_path,dst_path)
    
    filename = get_data_from_folder_A()
    validate_data_quality(filename)
