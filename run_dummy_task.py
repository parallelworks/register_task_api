import sys,os, json

import random
import time

from utils import register_function, train_runtime_prediction_model, predict_runtime, get_model_info, delete_tasks_by_name

TASK_NAME: str = 'sleep_geometric_mean_123'

@register_function
def sleep_geometric_mean(input_1, input_2, input_3, task_name = None):
    """
    This task is meant to be a fake task that runs for [runtime] miliseconds.
    The runtime is random but depends on the input parameters. 
    """
    start = time.time()
    geom_mean = abs(input_1*input_2*input_3)**(1/3)
    runtime_ms = 25*(1+0.1*random.random())*(geom_mean + 1)
    time.sleep(runtime_ms/1000)
    return int(1000*(time.time()-start))

def main():
    # Run many tasks to gather data:
    for x in range(0,11,2):
        for y in range(0,11,2):
            for z in range(0,11,2):
                runtime = sleep_geometric_mean(x, y, z, task_name = TASK_NAME)
                print('Runtime [ms]', runtime)

    # Train model to predict runtime of this task:
    print(f'Training model for task {TASK_NAME}')
    model_id = train_runtime_prediction_model(TASK_NAME)
    print(f'\nModel id: {model_id}')
    model_info = get_model_info(model_id)
    print('\nModel information: {}'. format(
        json.dumps(model_info, indent=4)
    ))

    # Run many tasks to gather more data and validate predictions
    for x in range(1,11,4):
        for y in range(1,11,4):
            for z in range(1,11,4):
                runtime_pred = predict_runtime(model_id, [x, y, z])
                runtime = sleep_geometric_mean(x, y, z, task_name = TASK_NAME)
                print('Runtime [ms]', runtime, 'Predicted [ms]', runtime_pred)


def clean():
    delete_tasks_by_name(TASK_NAME)

if __name__ == '__main__':
    main()
    clean()
