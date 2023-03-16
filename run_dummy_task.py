import sys,os, json

import random
import time

import utils

TASK_NAME: str = 'sleep_geometric_mean_123'
RESOURCE: dict = {
    'name': 'awsv2',
    'session': '00004',
    'node': 'compute',
}

# Register the task name and resource
utils.task_info['sleep_geometric_mean'] = {
    'name': TASK_NAME,
    'resource': RESOURCE,
}

utils.task_info['sleep_geometric_mean_missing'] = {
    'name': TASK_NAME,
    'resource': RESOURCE
}


@utils.register_function
def sleep_geometric_mean(input_1, input_2, input_3, input_str):
    """
    This task is meant to be a fake task that runs for [runtime] miliseconds.
    The runtime is random but depends on the input parameters. 
    """
    start = time.time()
    geom_mean = abs(input_1*input_2*input_3)**(1/3)
    runtime_ms = len(input_str)*10*(1+0.1*random.random())*(geom_mean + 1)
    time.sleep(runtime_ms/1000)
    return int(1000*(time.time()-start))

@utils.register_function
def sleep_geometric_mean_missing(input_1, input_2, input_3):
    """
    Same as sleep_geometric_mean but with a missing feature to test missing features
    """
    start = time.time()
    geom_mean = abs(input_1*input_2*input_3)**(1/3)
    runtime_ms = 10*(1+0.1*random.random())*(geom_mean + 1)
    time.sleep(runtime_ms/1000)
    return int(1000*(time.time()-start))

def train_model():
    # Train model to predict runtime of this task:
    print(f'Training model for task {TASK_NAME}')
    model_id = utils.train_runtime_prediction_model(
        TASK_NAME,
        features = {
            'input': ['input_1', 'input_2', 'input_3', 'input_str']
        },
        target = {'task': 'runtime'}
    )
    print(f'\nModel id: {model_id}')
    model_info = utils.get_model_info(model_id)
    print('\nModel information: {}'. format(
        json.dumps(model_info, indent=4)
    ))
    return model_id


def register_tasks():
    # Run many tasks to gather data:
    for x in range(0,11,4):
        for y in range(0,11,4):
            for z in range(0,11,4):
                for string in ['a', 'aa']:
                    runtime = sleep_geometric_mean(x, y, z, string)
                    print('Runtime [ms]', runtime)    


def validate_predictions(model_id):
    for x in range(1,11,4):
        for y in range(1,11,4):
            for z in range(1,11,4):
                for string in ['b', 'bb']:
                    inputs = {'input_1': x, 'input_2': y, 'input_3': z, 'input_str': string}
                    runtime_pred = utils.predict_runtime(model_id, inputs)
                    runtime = sleep_geometric_mean(x, y, z, string)
                    print('Runtime [ms]', runtime, 'Predicted [ms]', runtime_pred)
    

def validate_predictions_with_missing_features(model_id):
    for x in range(1,11,4):
        for y in range(1,11,4):
            for z in range(1,11,4):
                inputs = {'input_1': x, 'input_2': y, 'input_3': z}
                runtime_pred = utils.predict_runtime(model_id, inputs)
                runtime = sleep_geometric_mean_missing(x, y, z)
                print('Runtime [ms]', runtime, 'Predicted [ms]', runtime_pred)

def main():
    print('\nRegistering tasks')
    register_tasks()
    print('\nTraining model')
    model_id = train_model()
    print('\nValidating predictions')
    validate_predictions(model_id)
    print('\nValidating predictions with missing features')
    validate_predictions_with_missing_features(model_id)
    # Clean data
    #utils.delete_tasks_by_name(TASK_NAME)
    #utils.delete_model_by_id(model_id)

if __name__ == '__main__':
    main()