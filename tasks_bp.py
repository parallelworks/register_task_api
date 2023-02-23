import json
from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy


tasks_bp = Blueprint('tasks_bp', __name__, static_folder= "static") #, template_folder = "templates")

db_tasks = SQLAlchemy()
db_tasks_path = 'sqlite:///tasks.db'
tasks_table_name = 'task' 

class Task(db_tasks.Model):
    id = db_tasks.Column(db_tasks.Integer, primary_key = True)
    name = db_tasks.Column(db_tasks.String(80), nullable = False)
    inputs =  db_tasks.Column(db_tasks.String(800), nullable = False)
    #pid = db.Column(db.Integer, unique = True)
    #hosts = db.Column(db.String(800), nullable = True)
    runtime = db_tasks.Column(db_tasks.Integer, nullable = True)

    def __repr__(self):
        return f"{self.id} - {self.inputs} - {self.name}"

@tasks_bp.route('/tasks', methods = ['POST'])
def add_task():
    """
    sample_inputs = { 
        "inputs": {
            "args": [1, 2, 3],
            "kwargs": {
                "input_1": 1,
                "input_2": 2
            }
        },
        "name": "test-task-name"
    }
    - A task may be registered before completion so the runtime is not required
    """
    if 'runtime' in request.json:
        runtime = int(request.json['runtime'])
    else:
        runtime = None
    
    if type(request.json['inputs']) != str:
        inputs = json.dumps(request.json['inputs'])
    else:
        inputs = request.json['inputs']

    task = Task(
        inputs = inputs,
        runtime = runtime,
        name = request.json['name'] 
    )
    db_tasks.session.add(task)
    db_tasks.session.commit()
    return {'id': task.id}
   
@tasks_bp.route('/tasks')
def get_tasks():
    tasks = Task.query.all()
    tasks_data = []
    for task in tasks:
        tasks_data.append(
            {
                'id': task.id,
                'inputs': task.inputs,
                'runtime': task.runtime,
                'name': task.name
            }
        )
    return {'tasks': tasks_data}


@tasks_bp.route('/tasks/<id>')
def get_task(id):
    task = Task.query.get_or_404(id)
    return {'inputs': task.inputs, 'runtime': task.runtime, 'name': task.name}


# FIXME: Inpues should be transformed to a common format
@tasks_bp.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    '''
    Any of the attributes of a task can be updated on its own
    '''
    task = Task.query.get_or_404(id)
    if 'inputs' in request.json:
        inputs = request.json['inputs']
        if type(inputs) == str:
            task.inputs = inputs
        else:
            task.inputs = json.dumps(request.json['inputs'])
            
    if 'runtime' in request.json:
        task.runtime = int(request.json['runtime'])
    if 'name' in request.json:
        task.runtime = str(request.json['name'])

    db_tasks.session.commit()
    return {'message': 'Task updated'}

@tasks_bp.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db_tasks.session.delete(task)
    db_tasks.session.commit()
    return {'message': 'Task deleted'}