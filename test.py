import requests
import unittest
import json, os 

import pandas as pd

import run_dummy_task, utils

from application import TASKS_URL, MODELS_URL

TASK_JSON: dict = {
    'inputs': {
        'input_1': 1,
        'input_2': 2
    },
    'name': 'test-task-name'
}


MODEL_INPUTS: dict = {
    'input_1': 1,
    'input_2': 2,
    'input_3': 3,
    'input_str': 'aa'
}

MODEL_JSON: dict = {
    "model_name": "my-model",
    "task_name":run_dummy_task.TASK_NAME,
    "features": {'input': ['input_1', 'input_2', 'input_3', 'input_str']},
    "target": {'task': "runtime"}
}


MODEL_X: dict = {
    "X": pd.DataFrame([MODEL_INPUTS], columns = MODEL_INPUTS.keys()).to_json()
}

MODEL_DIR: str = 'models/'


class TestTaskEndPoint(unittest.TestCase):

    def setUp(self):
        post_response = requests.post(TASKS_URL, json = TASK_JSON)
        self.assertIn(post_response.status_code, [200,201])
        self.assertIsInstance(post_response.json(), dict)
        self.id = post_response.json()['id']
        self.assertIsInstance(self.id, int)

    def test_get_all(self):
        get_all_response = requests.get(TASKS_URL)
        self.assertEqual(get_all_response.status_code, 200)
        self.assertIsInstance(get_all_response.json(), dict)
        self.assertIn('tasks', get_all_response.json())
        self.assertIsInstance(get_all_response.json()['tasks'], list)
    
    def test_get_inputs(self):
        task_url = TASKS_URL + '/' + str(self.id)
        get_response = requests.get(task_url)
        self.assertEqual(get_response.status_code, 200)

    def test_get_name(self):
        task_url = TASKS_URL + '/' + str(self.id)
        get_response = requests.get(task_url)
        self.assertEqual(get_response.status_code, 200)
        response_task_json = get_response.json()
        self.assertEqual(TASK_JSON['name'], response_task_json['name'])

    def test_put_inputs(self):
        # Put task
        new_inputs = {
            'inputs': {
                'input_1': 3,
                'input_2': 4
            }
        }
        task_url = TASKS_URL + '/' + str(self.id)
        put_response = requests.put(task_url, json = new_inputs)
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual({'message': 'Task updated'}, put_response.json())

    def test_put_runtime(self):
        # Put task
        new_runtime = {
            'runtime': 1234 
        }
        task_url = TASKS_URL + '/' + str(self.id)
        put_response = requests.put(task_url, json = new_runtime)
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual({'message': 'Task updated'}, put_response.json())

        get_response = requests.get(task_url)
        response_task_json = get_response.json()
        self.assertEqual(new_runtime['runtime'], response_task_json['runtime'])

    def tearDown(self):
        # Delete task
        task_url = TASKS_URL + '/' + str(self.id)
        delete_response = requests.delete(task_url)
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual({'message': 'Task deleted'}, delete_response.json())


class TestModelEndPoint(unittest.TestCase):

    def setUp(self):
        run_dummy_task.register_tasks()
        post_response = requests.post(MODELS_URL, json = MODEL_JSON)
        self.assertIn(post_response.status_code, [200,201])
        self.assertIsInstance(post_response.json(), dict)
        self.id = post_response.json()['id']
        self.assertIsInstance(self.id, int)

    def test_get_all(self):
        get_all_response = requests.get(MODELS_URL)
        self.assertEqual(get_all_response.status_code, 200)
        self.assertIsInstance(get_all_response.json(), dict)
        self.assertIn('models', get_all_response.json())
        self.assertIsInstance(get_all_response.json()['models'], list)

    def test_get_model_prediction(self):
        model_prediction_url = MODELS_URL + '/' + str(self.id) +'/predict'
        get_response = requests.get(model_prediction_url, json = MODEL_X)
        get_response_json = get_response.json()
        self.assertIsInstance(get_response_json, dict)
        self.assertIn('predictions', get_response_json)
        self.assertIsInstance(get_response_json['predictions'], list)

    def tearDown(self):
        # Delete model
        model_url = MODELS_URL + '/' + str(self.id)
        model_path = os.path.join(MODEL_DIR, str(self.id) + '.pkl')
        delete_response = requests.delete(model_url)
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual({'message': 'Model deleted'}, delete_response.json())
        self.assertFalse(os.path.isfile(model_path), f"Model {model_path} was not deleted")
        utils.delete_tasks_by_name(run_dummy_task.TASK_NAME)

    
if __name__ == '__main__':
    unittest.main(exit = False)
