import pickle
import pandas as pd
import numpy as np
model_path = 'models/18.pkl'

# Check if there were any missing columns and print a warning if there were
with open(model_path, 'rb') as file:
    model = pickle.load(file)


inputs = {'input_1': [1], 'input_2': [1], 'input_3': [1], 'input_str': ['a']}
inputs = {'input_1': [1], 'input_2': [1], 'input_3': [1], 'input_str': [None]}

# FAILS
# inputs = {'input_1': [1], 'input_2': [1], 'input_3': [1], 'input_str': [np.nan]}

inputs = {'input_1': [1], 'input_2': [1], 'input_3': [1]}

data = pd.DataFrame(inputs)
data_columns = data.columns
print(data)

columns = ['input_1', 'input_2', 'input_3', 'input_str', 'input_str_2']
data = data.reindex(columns = columns, fill_value = None)

missing_features = set(columns) - set(data_columns)

print(missing_features)


data[list(missing_features)] = None
print(data)



#inputs = {'input_1': [1], 'input_2': [1], 'input_3': [1], 'input_str': [np.nan]}





prediction = model.predict(data)

print(prediction)