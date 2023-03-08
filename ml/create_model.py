import json, os
import pickle
from copy import deepcopy

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from xgboost import XGBRegressor

from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor, ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

from skopt import BayesSearchCV


def read_data(db_path, table_name, task_name, columns):
    columns = ', '.join(columns)
    engine = create_engine(db_path)
    # list all tables in the database
    #table_names = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)
    #print(table_names)
    query = f"SELECT {columns} FROM {table_name} WHERE name = '{task_name}'"
    return pd.read_sql(query, engine)

def expand_inputs(df):
    df['inputs'] = df['inputs'].apply(json.loads)
    return df

def get_numerical_and_categorical(data):
    features = list(data.columns) #.remove(target)

    categorical_features = list(
        set(data.columns) - set(data._get_numeric_data().columns)
    )

    numerical_features = deepcopy(features)
    [ numerical_features.remove(cf) for cf in categorical_features]

    return numerical_features, categorical_features

def get_X_y(df, features, target):
    df = expand_inputs(df)
    X = pd.DataFrame(df['inputs'].to_list())
    numerical, categorical = get_numerical_and_categorical(X)
    y = df[target]
    return X, y, numerical, categorical

def train_model(X_train, y_train, numerical, categorical, hyperparameter_optimization = False):
    
    numeric_transformer = Pipeline(
        steps = [
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', MinMaxScaler())
        ]
    )

    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers = [
            ('num', numeric_transformer, numerical),
            ('cat', categorical_transformer, categorical)
        ]
    )

    model = TransformedTargetRegressor(
        regressor = Pipeline(
            steps =
            [
                ('preprocess', preprocessor),
                ('xgb', XGBRegressor(objective = 'reg:squarederror'))
            ]
        ),
        transformer = MinMaxScaler()
    )
    if not hyperparameter_optimization:
        return model.fit(X_train, y_train)
    
    model_hopt = BayesSearchCV(
        model,
        {
            "regressor__xgb__n_estimators": (100, 10000),
            "regressor__xgb__learning_rate": (10**-4, 0.99, 'log-uniform'),
            "regressor__xgb__max_depth": [2, 3, 4, 5, 6, 7, 8]
        },
        n_iter = 10,
        cv = 5
    )
    return model_hopt.fit(X_train, y_train)

def save_model(model, model_path):
    os.makedirs(os.path.dirname(model_path), exist_ok = True)
    with open(model_path, 'wb') as output:
        pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)

def create_model(db_path, table_name, task_name, features, target, model_path):
    columns = features + [target]
    df = read_data(db_path, table_name, task_name, columns)
    X, y, numerical, categorical = get_X_y(df, features, target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle = True)
    model = train_model(X_train, y_train, numerical, categorical)
    save_model(model, model_path)
    score = model.score(X_test, y_test)
    return score

if __name__ == '__main__':
    table_name = 'task'
    features = ['inputs']
    target = 'runtime'
    task_name = 'sleep_geometric_mean_123'
    db_path = 'sqlite:////home/avidalto/projects/2023/register_task/tasks.db'
    model_path = 'models/predict-{target}-with-{features}-for-{task_name}.pkl'.format(
        target = target,
        features = '-'.join(features),
        task_name = task_name
    )

    score = create_model(db_path, table_name, task_name, features, target, model_path)
    print(score)