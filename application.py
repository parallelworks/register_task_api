# Some information is known before launching the task: input parameters
# Other information is known after launching the task: pid, jobid
# --> Therefore app should be able to call the API when running 

# Bash workflows --> Currently all information can be obtained 
import json

from flask import Flask, request

app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Inputs may need to be a JSON with args and kwargs

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    inputs =  db.Column(db.String(800), nullable = False)
    #pid = db.Column(db.Integer, unique = True)
    #hosts = db.Column(db.String(800), nullable = True)
    #runtime = db.Column(db.Integer, nullable = True)


    def __repr__(self):
        return f"{self.id} - {self.inputs}"


@app.route('/')
def index():
    return 'Hello'

@app.route('/tasks', methods = ['POST'])
def add_task():
    """
    sample_inputs = { 
        "inputs": {
            "args": [1, 2, 3],
            "kwargs": {
                "input_1": 1,
                "input_2": 2
            }
        }
    }
    """
    task = Task(inputs = json.dumps(request.json['inputs']))
    db.session.add(task)
    db.session.commit()
    return {'id': task.id}
   
@app.route('/tasks')
def get_tasks():
    tasks = Task.query.all()
    tasks_data = []
    for task in tasks:
        tasks_data.append(
            {
                'id': task.id,
                'inputs': task.inputs
            }
        )
    return {'tasks': tasks_data}


@app.route('/tasks/<id>')
def get_task(id):
    task = Task.query.get_or_404(id)
    return {'inputs': task.inputs}