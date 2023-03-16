import json, os, pickle
from typing import List

from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

import pandas as pd

import numpy as np

import create_model, bp_utils

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
        return f"{self.id} - {self.model_name} - {self.task_name} - {self.path} - {self.score}"
    
    @classmethod
    def to_dataframe(self, ids: List[int] = None, columns: List[str] = None):
        return bp_utils.dbmodel_to_dataframe(db_models, self, ids = ids, columns = columns)


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


    features_str = bp_utils.json2str(request.json['features'])
    target_str = bp_utils.json2str(request.json['target'])
    # FIXME: We may also have many targets
    model = Model(
        model_name = request.json['model_name'],
        task_name = request.json['task_name'],
        features = features_str,
        target = target_str
    )
    db_models.session.add(model)
    db_models.session.commit()

    model.path = os.path.join(models_directory, str(model.id) + '.pkl')
    model.score = create_model.create_model(
        model.task_name, 
        request.json['features'], 
        request.json['target'], 
        model.path
    )
    db_models.session.add(model)
    db_models.session.commit()

    return {'id': model.id}
   
@models_bp.route('/models')
def get_models():
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


@models_bp.route('/models/<id>')
def get_model(id):
    model = Model.query.get_or_404(id)
    response = {
        'model_name': model.model_name,
        'task_name': model.task_name,
        'features': model.features,
        'target': model.target,
        'path': model.path,
        'score': model.score
    }
    return response


@models_bp.route('/models/<id>/predict')
def get_model_prediction(id):
    model = Model.query.get_or_404(id)
    model_features = []
    [ model_features.extend(columns) for table,columns in json.loads(model.features).items() ]
    # Needs to be a dataframe to be compatible with the machine learning model
    data = pd.read_json(request.json['X'])
    data_columns = data.columns
    # If features are missing in data it will complete them with NaN values
    data = data.reindex(columns = model_features, fill_value = None)

    # Check if there were any missing columns and print a warning if there were
    missing_features = set(model_features) - set(data_columns)
    if missing_features:
        print(f"Warning: The following features were missing in the data: {missing_features}")
        data[list(missing_features)] = None # fill_value = None does not seem to work well
    
    with open(model.path, 'rb') as file:
        model = pickle.load(file)

    prediction = model.predict(data)
    
    return {'predictions': prediction.tolist()}


    
@models_bp.route('/models/<id>', methods=['DELETE'])
def delete_model(id):
    model = Model.query.get_or_404(id)
    if os.path.isfile(model.path):
        os.remove(model.path)
    db_models.session.delete(model)
    db_models.session.commit()
    return {'message': 'Model deleted'}


@models_bp.route('/models/table', methods=['GET'])
def resources_table():
    return bp_utils.render_table(Model)