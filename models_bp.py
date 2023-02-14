import json, os
from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

import ml
from tasks_bp import db_tasks_path, tasks_table_name

models_bp = Blueprint('models_bp', __name__, static_folder= "static") #, template_folder = "templates")

db_models = SQLAlchemy()
db_models_path = 'sqlite:///models.db'
models_directory = 'models' # Where ML models are saved

class Model(db_models.Model):
    id = db_models.Column(db_models.Integer, primary_key = True)
    model_name = db_models.Column(db_models.String(80), nullable = False)
    task_name = db_models.Column(db_models.String(80), nullable = False)
    features = db_models.Column(db_models.String(800), nullable = False)
    target = db_models.Column(db_models.String(80), nullable = False)
    path =  db_models.Column(db_models.String(800), nullable = True, unique = True)
    score = db_models.Column(db_models.Float, nullable = True)
    
    def __repr__(self):
        return f"{self.id} - {self.name} - {self.path} - {self.score}"
    

@models_bp.route('/models', methods = ['POST'])
def add_model():
    """
    sample_inputs = {
        "name": "my-model",
        "task_name": "task-123",
        "features": ["inputs"],
        "target": "runtime"
    }
    """
    features = request.json['features']
    if not isinstance(features, str):
        features_str = json.dumps(features)
    else:
        features_str = features

    # FIXME: We may also have many targets

    model = Model(
        model_name = request.json['name'],
        task_name = request.json['task_name'],
        features = features_str,
        target = request.json['target']
    )
    db_models.session.add(model)
    db_models.session.commit()

    model.path = os.path.join(models_directory, str(model.id) + '.pkl')

    model.score = ml.create_model.create_model(
        db_tasks_path, 
        tasks_table_name, 
        model.task_name, 
        features, 
        model.target, 
        model.path
    )
    db_models.session.add(model)
    db_models.session.commit()

    return {'id': model.id}
   
@models_bp.route('/models')
def get_tasks():
    models = Model.query.all()
    models_data = []
    for model in models:
        models_data.append(
            {
                'id': model.id,
                'model_name': model.model_name,
                'task_name': model.task_name,
                'features': model.features,
                'target': model.target,
                'path': model.path,
                'score': model.score
            }
        )

    return {'models': models_data}
