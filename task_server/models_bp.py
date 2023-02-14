import json
from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy


models_bp = Blueprint('models_bp', __name__, static_folder= "static") #, template_folder = "templates")

db_model = SQLAlchemy()

class Model(db_task.Model):
    id = db_task.Column(db_task.Integer, primary_key = True)
    name = db_task.Column(db_task.String(80), nullable = False)
    path =  db_task.Column(db_task.String(800), nullable = False)

    def __repr__(self):
        return f"{self.id} - {self.inputs} - {self.name}"
    

#class Model(db.Model):
#    id = db.Column(db.Integer, primary_key = True)
#    name = db.Column(db.String(80), nullable = False)
#    path =  db.Column(db.String(800), nullable = True)
#
#    def __repr__(self):
#        return f"{self.id} - {self.name} - {self.path}"
    

@models_bp.route('/models', methods = ['POST'])
def add_task():
    """
    
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
    db_task.session.add(task)
    db_task.session.commit()
    return {'id': task.id}
   
@models_bp.route('/tasks')
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


@models_bp.route('/tasks/<id>')
def get_task(id):
    task = Task.query.get_or_404(id)
    return {'inputs': task.inputs, 'runtime': task.runtime, 'name': task.name}


@models_bp.route('/tasks/<id>', methods=['PUT'])
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

    db_task.session.commit()
    return {'message': 'Task updated'}

@models_bp.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db_task.session.delete(task)
    db_task.session.commit()
    return {'message': 'Task deleted'}