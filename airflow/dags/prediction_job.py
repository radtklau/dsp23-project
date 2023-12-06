import logging
import os
import pandas as pd
from datetime import datetime, timedelta
import requests

from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
import json


FOLDER_A = '../data/folder_A/'
FOLDER_B = '../data/folder_B/'
FOLDER_C = '../data/folder_C/'

with DAG(
    dag_id='prediction_job',
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(n=0,hour=1),
    catchup=False,
    tags=['example'],
) as dag:

    @task
    def get_data_from_folder_C():
        logging.info('Task 1: Get data from Folder C')
        files = sorted(os.listdir(FOLDER_C), key=len)
        logging.info(files)
        filename = ""
        if files:
            filename = files[0]
            file_path = os.path.join(FOLDER_C, filename)
        return file_path

    @task
    def make_prediction(file_path):
        logging.info('Task 2: Start prediction job')
        csv_content = open(file_path, 'r').read()
        logging.info(csv_content)
        rows = [list(map(int, row.split(','))) for row in csv_content.split('\n')]
        data = {"file": rows, "prediction_source": "scheduled"}
        logging.info(data)
        response = requests.post("http://localhost:8000/predict", json=data)
        #response = requests.post("http://localhost:8000/test")
        logging.info(response)
        #logging.info(json.dumps(response.json(), indent=4))
        logging.info(f"Response: {response.text}")

    filename = get_data_from_folder_C()
    if filename:
        make_prediction(filename)
        
#launch database "psql postgres", db testdb, user postgres
#workingdir \app\ !!