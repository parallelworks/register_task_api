import json, os
import pickle

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from xgboost import XGBRegressor

from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor

from sklearn.model_selection import train_test_split

def read_data(db_path, table_name, task_name, columns):
    columns = ', '.join(columns)
    engine = create_engine(db_path)
    # list all tables in the database
    #table_names = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)
    #print(table_names)
    query = f"SELECT {columns} FROM {table_name} WHERE name = '{task_name}'"
    return pd.read_sql(query, engine)

def inputs_dict_to_list(inputs: dict) -> list:
    args_list = []
    for arg_name, arg_val in inputs.items():
        # FIXME: Generalize treatment of different input types!
        if isinstance(arg_val, int) or isinstance(arg_val, float):
            args_list.append(arg_val)
    return args_list

def expand_inputs(df):
    df['inputs'] = df['inputs'].apply(json.loads)
    return df

def get_X_y(df, features, target):
    # FIXME: Generalize creation of X:
    df = expand_inputs(df)
    df['inputs'] = df['inputs'].apply(inputs_dict_to_list)
    X = np.array(df['inputs'].to_list())
    ##################################
    y = df[target]
    return X, y

def train_model(X_train, y_train):
    model = TransformedTargetRegressor(
        regressor = Pipeline(
            [
                ('scale',  MinMaxScaler()),
                ('xgb', XGBRegressor(objective = 'reg:squarederror'))
            ]
        ),
        transformer = MinMaxScaler()
    )
    model.fit(X_train, y_train)
    return model

def save_model(model, model_path):
    os.makedirs(os.path.dirname(model_path), exist_ok = True)
    with open(model_path, 'wb') as output:
        pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)

def create_model(db_path, table_name, task_name, features, target, model_path):
    columns = features + [target]
    df = read_data(db_path, table_name, task_name, columns)
    X, y = get_X_y(df, features, target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle = True)
    model = train_model(X_train, y_train)
    save_model(model, model_path)
    score = model.score(X_test, y_test)
    return score

if __name__ == '__main__':
    table_name = 'task'
    features = ['inputs']
    target = 'runtime'
    task_name = 'avidalto-sleep_geometric_mean'
    db_path = 'sqlite:////home/avidalto/projects/2023/register_task/task_server/tasks.db'
    model_path = 'models/predict-{target}-with-{features}-for-{task_name}.pkl'.format(
        target = target,
        features = '-'.join(features),
        task_name = task_name
    )

    score = create_model(db_path, table_name, task_name, features, target, model_path)
