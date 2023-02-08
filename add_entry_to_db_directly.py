import json
from application import db, Task

sample_inputs = {
    "inputs": {
        "args": [1, 2, 3],
        "kwargs": {
            "input_1": 1,
            "input_2": 2
        }
    }
}

task = Task(inputs = "test")
print(task)
db.session.add(task)
db.session.commit()

Task.query.all()