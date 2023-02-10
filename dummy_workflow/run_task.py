import random
import requests

# FIXME: Add python decorator to handle requests!
def run_task(input_1, input_2, input_3):
    """
    This task is meant to be a fake task that runs for [runtime] seconds.
    The runtime is random but depends on the input parameters. 
    """
    runtime = 100*(1+0.1*random.random())*(abs(input_1*input_2*input_3))**(1/3)
    return int(runtime)

TASKS_URL: str = "http://127.0.0.1:5000/tasks"

if __name__ == '__main__':

    for x in range(10):
        for y in range(10):
            for z in range(10):
                task_inputs = {
                    'inputs': {
                        'x': x,
                        'y': y,
                        'z': z
                    }
                }
                # Post task
                post_response = requests.post(
                    TASKS_URL, 
                    json = task_inputs
                )
                id = post_response.json()['id']

                runtime = run_task(x, y, z)
                print('runtime', runtime)

                # Put task
                task_runtime = {
                    'runtime': runtime 
                }
                task_url = TASKS_URL + '/' + str(id)
                put_response = requests.put(task_url, json = task_runtime)


