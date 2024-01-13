"""
import logging
import os
import random
from datetime import datetime, timedelta
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
import json

#skipping:
FOLDER_C = 'data/folder_C/'

def get_data_from_folder_C(**kwargs):
    logging.info('Task 1: Get data from Folder C')
    dir_C = os.listdir(FOLDER_C)
    file = open("airflow/dags/predicted_files.txt", "r") 
    predicted_files_str = file.read()
    file.close()
    
    if predicted_files_str:
        predicted_files = predicted_files_str.split(" ")[:-1]
    else:
        predicted_files = []

    dir_C_set = set(dir_C)
    predicted_files_set = set(predicted_files)

    unpredicted_files = list(dir_C_set.difference(predicted_files_set))

    if unpredicted_files:
        file_name = random.choice(unpredicted_files)
        predicted_files.append(file_name)
    else:
        logging.info("No new file found in folder C.")
        return None

    file = open('airflow/dags/predicted_files.txt', 'w')
    file.writelines(entry + " " for entry in predicted_files)
    file.close()
    
    logging.info(file_name)
    logging.info("--------------------------------")
    logging.info(predicted_files)
    logging.info("--------------------------------")
    
    file_path = os.path.join(FOLDER_C, file_name)
    return file_path

def make_prediction(**kwargs):
    ti = kwargs['ti']
    file_path = ti.xcom_pull(task_ids='get_data_from_folder_C_task')
    
    if not file_path:
        logging.info("No new file found. Skipping prediction.")
        return None

    logging.info('Task 2: Start prediction job')
    logging.info(f"Predicting file {file_path}")
    
    csv_content = open(file_path, 'r').read()
    logging.info(csv_content)
    
    rows = [list(map(int, r.split(','))) for r in csv_content.split('\n') if r != '']
    data = {"file": rows, "prediction_source": "scheduled"}
    logging.info(data)
    
    response = requests.post("http://localhost:8000/predict", json=data)
    logging.info(response)
    logging.info(f"Response: {response.text}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='prediction_job',
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(n=0,hour=1),
    catchup=False,
    tags=['example'],
    default_args=default_args,
) as dag:

    get_data_from_folder_C_task = PythonOperator(
        task_id='get_data_from_folder_C_task',
        python_callable=get_data_from_folder_C,
        provide_context=True,
    )

    make_prediction_task = PythonOperator(
        task_id='make_prediction_task',
        python_callable=make_prediction,
        provide_context=True,
    )

    branch_task = BranchPythonOperator(
        task_id='branch_task',
        python_callable=lambda **kwargs: 'make_prediction_task' if kwargs['ti'].xcom_pull(task_ids='get_data_from_folder_C_task') else 'skip_task',
        provide_context=True,
    )

    skip_task = PythonOperator(
        task_id='skip_task',
        python_callable=lambda **kwargs: None,
        provide_context=True,
    )

    get_data_from_folder_C_task >> branch_task
    branch_task >> [make_prediction_task, skip_task]


#failing:
"""
import logging
import os,random
import pandas as pd
from datetime import datetime, timedelta
import requests

from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
import json


FOLDER_A = 'data/folder_A/'
FOLDER_B = 'data/folder_B/'
FOLDER_C = 'data/folder_C/'

with DAG(
    dag_id='prediction_job',
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(n=0,hour=0),
    catchup=False,
    tags=['example'],
) as dag:

    predicted_files = []

    @task
    def get_data_from_folder_C():
        logging.info('Task 1: Get data from Folder C')
        dir_C = os.listdir(FOLDER_C)
        file = open("airflow/dags/predicted_files.txt", "r") 
        predicted_files_str = file.read()
        file.close()
        if predicted_files_str:
            predicted_files = predicted_files_str.split(" ")
        else:
            predicted_files = []
        
        dir_C_set = set(dir_C)
        predicted_files_set = set(predicted_files)
        
        logging.info(f"dir C set {dir_C_set}")
        logging.info(f"predicted files set {predicted_files_set}")
        unpredicted_files = list(dir_C_set.difference(predicted_files_set))
        logging.info(f"unpredicted files {unpredicted_files}")
        
        if not unpredicted_files:
            logging.info("No new file found in folder C.")
            return None 
        else:
            files_to_predict = []
            predicted_files.extend(unpredicted_files)
            for file_name in unpredicted_files:
                files_to_predict.append(os.path.join(FOLDER_C, file_name))
            
        file = open('airflow/dags/predicted_files.txt','w')
        file.writelines(entry+" " for entry in predicted_files)
        file.close()
        

        logging.info("--------------------------------")
        logging.info("Files to predict:")
        logging.info(unpredicted_files)
        logging.info("--------------------------------")
            
        return files_to_predict #return every unpredicted file in a list

    @task
    def make_prediction(files):
        if files:
            logging.info('Task 2: Start prediction job')
            for file_path in files: #predict all provided files
                logging.info(f"Predicting file {file_path}")
                csv_content = open(file_path, 'r').read()
                logging.info(csv_content)
                rows = []
                for r in csv_content.split('\n'):
                    if r != '': # in case of even number of lines
                        rows.append(list(map(int, r.split(','))))
                # rows = [list(map(int, rows.split(','))) for row in csv_content.split('\n')]
                data = {"file": rows, "prediction_source": "scheduled"}
                logging.info(data)
                response = requests.post("http://localhost:8000/predict", json=data)
                #response = requests.post("http://localhost:8000/test")
                logging.info(response)
                #logging.info(json.dumps(response.json(), indent=4))
                logging.info(f"Response: {response.text}")
        else:
            logging.info("Skipped prediction, because no new files are available.")

    filename = get_data_from_folder_C()
    if filename:
        make_prediction(filename)
        
#launch database "psql postgres", db testdb, user postgres
#workingdir \app\ !!

#commit laurids, pull working, merge laurids, merge working, push working
