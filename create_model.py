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

from tasks_bp import db_tasks_path, TASKS_TABLE_NAME, TASKS_TABLE_RELATIONSHIP


def get_numerical_and_categorical(data):
    features = list(data.columns) #.remove(target)

    categorical_features = list(
        set(data.columns) - set(data._get_numeric_data().columns)
    )

    numerical_features = deepcopy(features)
    [ numerical_features.remove(cf) for cf in categorical_features]

    return numerical_features, categorical_features

def get_X(df, features):
    X = df[features]
    numerical, categorical = get_numerical_and_categorical(X)
    return X, numerical, categorical

def train_model(X_train, y_train, numerical, categorical, hyperparameter_optimization = False):
    
    numeric_transformer = Pipeline(
        steps = [
            ('imputer', SimpleImputer(strategy = 'median')),
            ('scaler', MinMaxScaler())
        ]
    )

    categorical_transformer = Pipeline(
        steps = [
            ('imputer', SimpleImputer(strategy = 'most_frequent')),
            ('ohe', OneHotEncoder(handle_unknown = 'ignore'))
        ]
    )

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


def get_data_df(task_name, columns):
    '''
    Merges all the tables referenced by the task table into a single dataframe
    '''
    engine = create_engine(db_tasks_path)
    # list all tables in the database````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    #table_names = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)
    #print(table_names)
    task_query = f"SELECT * FROM {TASKS_TABLE_NAME} WHERE name = '{task_name}'"
    task_df = pd.read_sql(task_query, engine, index_col = 'id')
    for table in TASKS_TABLE_RELATIONSHIP:
        if table.__tablename__ not in columns:
            continue

        id_col = table.__tablename__ + '_id'
        id_list = task_df[id_col].unique().tolist()
        df = table.to_dataframe(ids = id_list, columns = columns[table.__tablename__])
        task_df = pd.merge(task_df, df, how = 'left', left_on = id_col, right_index = True).drop(columns = [id_col])

    return task_df

def merge_features_and_target(features, target):
    """
    Merges the features and target dictionaries:
    { table_name: [table_columns] }
    """
    columns = deepcopy(features)
    for table, column in target.items():
        if table in columns:
            columns[table].append(column)
        else:
            columns[table] = [column]
    return columns

def get_data(task_name, features, target):
    columns = merge_features_and_target(features, target)
    df = get_data_df(task_name, columns)
    # Remove rows with non-numeric values on the target column
    target_columns = [column for table,column in target.items()]
    # FIXME: Need to change to generalize to multiple targets
    # - Removes rows with non-numeric values
    df = df[pd.to_numeric(df[target_columns[0]], errors='coerce').notna()]
    X = df[features['input']]
    numerical, categorical = get_numerical_and_categorical(df[features['input']])
    y = df[target_columns[0]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle = True)
    return X_train, X_test, y_train, y_test, numerical, categorical

def create_model(task_name, features, target, model_path):
    X_train, X_test, y_train, y_test, numerical, categorical = get_data(task_name, features, target)
    model = train_model(X_train, y_train, numerical, categorical)
    save_model(model, model_path)
    score = model.score(X_test, y_test)
    return score
