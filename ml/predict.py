import pickle
import numpy as np

def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

def predict(model_path, X):
    X = np.array(X).reshape(1, -1)
    model = load_model(model_path)
    return model.predict(X)

if __name__ == '__main__':
    import numpy as np

    MODEL_X: dict = {
    "X": [1,2,3]
    }
    model_path = 'models/5.pkl'
    prediction = predict(model_path, MODEL_X['X'])
    print(prediction.tolist())

