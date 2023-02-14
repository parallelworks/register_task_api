import sys,json, os
import pandas as pd

sys.path.append(os.environ['PATH_TO_TASK_CLIENT'])

from xgboost import XGBRegressor

from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor

from sklearn.model_selection import train_test_split

import task_client

def args_to_pandas_dict(args: list) -> dict:
    # FIXME: What if input_1 is also in kwargs?
    input_dict_for_pandas = {}
    for i,arg in enumerate(args):
        input_name = 'input_' + str(i+1)
        input_dict_for_pandas[input_name] = arg
    return input_dict_for_pandas

def train_xgboost_model(X_train, y_train):
    model = TransformedTargetRegressor(
        regressor = Pipeline(
            [
                ('scale',  MinMaxScaler()),
                ('xgb', XGBRegressor(objective = 'reg:squarederror'))
            ]
        ),
        transformer = MinMaxScaler()
    )
    print(X_train, y_train)
    model.fit(X_train, y_train)
    return model


tasks = task_client.get.get_tasks_by_name('avidalto-sleep_geometric_mean')

data_for_pandas: list = []

for task in tasks:
    data_dict = json.loads(task['inputs'])
    # FIXME: What if runtime in kwargs?
    data_dict_for_pandas = {'runtime': task['runtime']}
    if 'args' in data_dict:
        data_dict_for_pandas.update(args_to_pandas_dict(data_dict['args']))

    if 'kwargs' in data_dict:
        data_dict_for_pandas.update(data_dict['kwargs'])

    data_for_pandas.append(data_dict_for_pandas)


data_pd = pd.DataFrame.from_dict(data_for_pandas)
print(data_pd.head())

features = list(data_pd.keys())
features.remove('runtime')
target = ['runtime']

X = data_pd[features].values
y = data_pd[target].values

X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle = True)

model = train_xgboost_model(X_train, y_train)

score = model.score(X_test, y_test)
print(score)



