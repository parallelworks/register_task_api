import requests
import time
import json



TASKS_URL: str = "http://127.0.0.1:5000/tasks"

def register_function(func):
    def wrapper(*args, **kwargs):
        # Post task
        inputs = {
            'inputs': {
                'args': args,
                'kwargs': kwargs
            }
        }
        post_response = requests.post(
            TASKS_URL, 
            json = inputs
        )
        id = post_response.json()['id']
        
        # Measure function runtime
        start = time.time()
        result = func(*args, **kwargs)
        runtime = time.time()-start

        # Put task
        task_runtime = {
            'runtime': runtime 
        }
        task_url = TASKS_URL + '/' + str(id)
        put_response = requests.put(task_url, json = task_runtime)
        return func(*args, **kwargs)

    return wrapper