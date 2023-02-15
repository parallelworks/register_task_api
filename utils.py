import requests
import time
import json
import os


TASKS_URL: str = "http://127.0.0.1:5000/tasks"
MODELS_URL: str = "http://127.0.0.1:5000/models"


def register_function(func):
    def wrapper(*args, **kwargs):
        # Post task
        post_info = {
            'inputs': {
                'args': args,
                'kwargs': kwargs
            }
        }
        if 'task_name' not in kwargs:
            task_name = os.environ['USER'] + '-' + func.__name__
        else:
            task_name = kwargs['task_name']

        post_info['name'] = task_name

        post_response = requests.post(
            TASKS_URL, 
            json = post_info,
        )
        id = post_response.json()['id']
        
        # Measure function runtime
        start = time.time()
        result = func(*args, **kwargs)
        runtime = time.time()-start

        # Put task
        task_runtime = {
            'runtime': int(1000*runtime) 
        }
        task_url = TASKS_URL + '/' + str(id)
        put_response = requests.put(task_url, json = task_runtime)
        return func(*args, **kwargs)

    return wrapper


def train_runtime_prediction_model(task_name):
    model_json = {
        "model_name": task_name + '_inputs_runtime',
        "task_name": task_name,
        "features": ["inputs"],
        "target": "runtime"
    }
    response = requests.post(MODELS_URL, json = model_json)
    return response.json()['id']


def predict_runtime(model_id, X_list):
    model_prediction_url = MODELS_URL + '/' + str(model_id) +'/predict'
    model_X = {
        "X": X_list
    }
    get_response = requests.get(model_prediction_url, json = model_X)
    return get_response.json()['predictions'][0]


def get_model_info(model_id):
    model_url = MODELS_URL + '/' + str(model_id)
    response = requests.get(model_url)
    return response.json()