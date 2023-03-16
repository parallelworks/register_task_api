import json
from typing import List

from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Only required to display the data 
import pandas as pd


import bp_utils

tasks_bp = Blueprint('tasks_bp', __name__, static_folder= "static")

db_tasks = SQLAlchemy()

db_tasks_path = 'sqlite:///tasks.db'
TASKS_TABLE_NAME: str = 'task' 
INPUTS_TABLE_NAME: str = 'input'
RESOURCES_TABLE_NAME: str = 'resource'

class Task(db_tasks.Model):
    __tablename__ = TASKS_TABLE_NAME
    id = db_tasks.Column(db_tasks.Integer, primary_key = True)
    name = db_tasks.Column(db_tasks.String(80), nullable = False)
    runtime = db_tasks.Column(db_tasks.Integer, nullable = True)
    input_id = db_tasks.Column(db_tasks.Integer, db_tasks.ForeignKey('input.id'), nullable=True)
    input = db_tasks.relationship('Input', backref='tasks')
    resource_id = db_tasks.Column(db_tasks.Integer, db_tasks.ForeignKey('resource.id'), nullable=True)
    resource = db_tasks.relationship('Resource', backref='tasks')

    def __repr__(self):
        return f"{self.id} - {self.name} - {self.runtime} - {self.input_id}"

    @classmethod
    def to_dataframe(self, ids: List[int] = None, columns: List[str] = None):
        return bp_utils.dbmodel_to_dataframe(db_tasks, self, ids = ids, columns = columns)

class Input(db_tasks.Model):
    __tablename__ = INPUTS_TABLE_NAME
    id = db_tasks.Column(db_tasks.Integer, primary_key = True)
    inputs =  db_tasks.Column(db_tasks.String(800), nullable = False, unique = True)

    def __repr__(self):
        return f"{self.id} - {self.inputs}"
    
    @classmethod
    def to_dataframe(cls, ids: List[int] = None, columns: List[str] = None):
        df = bp_utils.dbmodel_to_dataframe(db_tasks, cls, ids=ids)
        df = pd.json_normalize(df['inputs'].apply(json.loads)).rename_axis('id')
        if columns:
            return df[columns]
        return df


class Resource(db_tasks.Model):
    __tablename__ = RESOURCES_TABLE_NAME
    id = db_tasks.Column(db_tasks.Integer, primary_key = True)
    name =  db_tasks.Column(db_tasks.String(80), nullable = False)
    session =  db_tasks.Column(db_tasks.Integer, nullable = False)
    # Controller or name of partition
    node = db_tasks.Column(db_tasks.String(80), nullable = False)


    def __repr__(self):
        return f"{self.id} - {self.name} - {self.session} - {self.node}"

    @classmethod
    def to_dataframe(self, ids: List[int] = None, columns: List[str] = None):
        return bp_utils.dbmodel_to_dataframe(db_tasks, self, ids = ids, columns = columns)


TASKS_TABLE_RELATIONSHIP = [Input, Resource]


@tasks_bp.route('/tasks', methods = ['POST'])
def add_task():
    """
    sample_inputs = { 
        "inputs": {
            "input_1": 1,
            "input_2": 2
        },
        "name": "test-task-name"
    }
    - A task may be registered before completion so the runtime is not required
    """
    if 'runtime' in request.json:
        runtime = int(request.json['runtime'])
    else:
        runtime = None

    inputs = bp_utils.json2str(request.json['inputs'])
    input_obj = bp_utils.add_if_new(db_tasks, Input, {'inputs': inputs})

    if 'resource' in request.json:
        resource_obj = bp_utils.add_if_new(db_tasks, Resource, request.json['resource'])
        resource_id = resource_obj.id
    else:
        # Can still register a task with no defined resource
        resource_id = None

    task = Task(
        input_id = input_obj.id,
        resource_id = resource_id,
        runtime = runtime,
        name = request.json['name'] 
    )

    db_tasks.session.add(task)
    db_tasks.session.commit()
    return {'id': task.id}


# FIXME: Inpues should be transformed to a common format
@tasks_bp.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    '''
    Any of the attributes of a task can be updated on its own
    '''
    task = Task.query.get_or_404(id)
    # Some information is known after the task is posted and runs
    if 'runtime' in request.json:
        task.runtime = int(request.json['runtime'])
    # May want to rename tasks
    if 'name' in request.json:
        task.name = str(request.json['name'])

    db_tasks.session.commit()
    return {'message': 'Task updated'}

@tasks_bp.route('/tasks')
def get_tasks():
    tasks = Task.query.all()
    tasks_data = []
    for task in tasks:
        tasks_data.append(
            {
                'id': task.id,
                'input_id': task.input_id,
                'runtime': task.runtime,
                'name': task.name
            }
        )
    return {'tasks': tasks_data}


@tasks_bp.route('/tasks/<id>')
def get_task(id):
    task = Task.query.get_or_404(id)
    return {'input_id': task.input_id, 'runtime': task.runtime, 'name': task.name}

@tasks_bp.route('/inputs')
def get_inputs():
    inputs = Input.query.all()
    inputs_data = []
    for inp in inputs:
        inputs_data.append(
            {
                'id': inp.id,
                'inputs': inp.inputs
            }
        )
    return {'inputs': inputs_data}


@tasks_bp.route('/input/<id>')
def get_input(id):
    inp = Input.query.get_or_404(id)
    return {'inputs': inp.inputs}


@tasks_bp.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db_tasks.session.delete(task)
    db_tasks.session.commit()
    return {'message': 'Task deleted'}


@tasks_bp.route('/inputs/<id>', methods=['DELETE'])
def delete_input(id):
    # Check if the input is referenced by any task
    task = Task.query.filter(Task.input_id == id).first()
    if task is not None:
        return {'message': 'Cannot delete input. It is referenced by a task.'}, 400
    
    # Delete the input if no task references it
    input_to_delete = Input.query.get_or_404(id)
    db_tasks.session.delete(input_to_delete)
    db_tasks.session.commit()
    return {'message': 'Input deleted'}


@tasks_bp.route('/tasks/table', methods=['GET'])
def tasks_table():
    return bp_utils.render_table(Task)

@tasks_bp.route('/inputs/table', methods=['GET'])
def inputs_table():
    return bp_utils.render_table(Input)

@tasks_bp.route('/resources/table', methods=['GET'])
def resources_table():
    return bp_utils.render_table(Resource)