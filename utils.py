import requests
import time
import json
import os
import inspect

TASKS_URL: str = "http://127.0.0.1:5000/tasks"
MODELS_URL: str = "http://127.0.0.1:5000/models"

def get_default_args(func):
    """
    Sample:
    f(fist,last,greeting = 'hello')
    >> {'greeting': 'hello'}
    """
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

def convert_arguments_to_dict(func, args, kwargs):
    """
    Sample:
    f(fist,last,greeting = 'hello')
    f(john, doe) 
    >> {first: john, last:doe, greeting = 'hello'}
    f(john, doe, greeting = 'hi') 
    >> {first: john, last:doe, greeting = 'hi'}
    """
    def_args = get_default_args(func)
    anames = func.__code__.co_varnames[:func.__code__.co_argcount]
    args_dict = dict(zip(anames, args))
    knames = [ aname for aname in anames if aname not in args_dict ]
    kvalues = [ kwargs[kname] if kname in kwargs else def_args[kname] for kname in knames]
    kwargs_dict = dict(zip(knames, kvalues))
    return {**args_dict, **kwargs_dict}

def register_function(func):
    def wrapper(*args, **kwargs):
        # Post task
        inputs = convert_arguments_to_dict(func, args, kwargs)
        if 'task_name' not in kwargs:
            task_name = os.environ['USER'] + '-' + func.__name__
        else:
            task_name = kwargs['task_name']

        post_info = {
            'name': task_name,
            'inputs': inputs
        }

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
        return result

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