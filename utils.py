import requests
import time
import json
import os


TASKS_URL: str = "http://127.0.0.1:5000/tasks"

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