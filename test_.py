import requests
import unittest

TASK_URL: str = "http://127.0.0.1:5000/tasks"
TASK_JSON: dict = {
    "inputs": {
        "args": [1, 2, 3],
        "kwargs": {
            "input_1": 1,
            "input_2": 2
        }
    }
}

class TestPostGetTaskRequest(unittest.TestCase):
    def setUp(self):
        """
        setUp is called for every test
        """
        self.post_response = requests.post(TASK_URL, json = TASK_JSON)
        self.get_response = requests.get(TASK_URL)

    def test_post_response_is_dict(self):
        self.assertIsInstance(self.post_response.json(), dict)
        
    def test_post_response_has_id(self):
        self.assertIn('id', self.post_response.json())

    def test_post_response_id_is_int(self):
        self.assertIsInstance(self.post_response.json()['id'], int)

    
    def test_get_response_is_dict(self):
        self.assertIsInstance(self.get_response.json(), dict)

    def test_get_response_has_tasks(self):
        self.assertIn('tasks', self.get_response.json())

    def test_get_response_id_is_list(self):
        self.assertIsInstance(self.get_response.json()['tasks'], list)


if __name__ == '__main__':
    unittest.main()