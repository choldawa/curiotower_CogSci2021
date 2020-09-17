import numpy as np
from metrics.readout_model import ReadoutModel
from sklearn.linear_model import LinearRegression, LogisticRegression



class LinearRegressionReadoutModel(ReadoutModel):
    def __init__(self):
        self._model = LinearRegression()


    def fit(self, data, labels, **kwargs):
        data = np.stack(data) if isinstance(data, list) else data
        labels = np.stack(labels) if isinstance(labels, list) else labels

        model_data = data[np.where(data[..., 14] > 0)][..., 0:10]
        labels = labels[np.where(data[..., 14] > 0)][..., 0:3]

        self._model.fit(model_data, labels)


    def predict(self, data, **kwargs):
        data = np.stack(data) if isinstance(data, list) else data
        model_data = data[np.where(data[..., 14] > 0)][..., 0:10]

        predictions = self._model.predict(model_data)
        data[np.where(data[..., 14] > 0)] = np.concatenate([
            predictions, data[np.where(data[..., 14] > 0)][:, 3:]], axis = -1)

        predictions = np.split(data, data.shape[0], axis = 0)
        predictions = [p[0] for p in predictions]

        return predictions



class LogisticRegressionReadoutModel(ReadoutModel):
    def __init__(self):
        self._model = LogisticRegression()


    def fit(self, data, labels, **kwargs):
        data = np.stack(data) if isinstance(data, list) else data
        labels = np.stack(labels) if isinstance(labels, list) else labels

        model_data = data[np.where(data[..., 14] > 0)][..., 0:10]
        labels = labels[np.where(data[..., 14] > 0)]

        # TODO FIX HACK: assert that at least one example of each class in data
        labels[-1] = 1

        self._model.fit(model_data, labels)


    def predict(self, data, **kwargs):
        data = np.stack(data) if isinstance(data, list) else data
        model_data = data[np.where(data[..., 14] > 0)][..., 0:10]

        predictions = self._model.predict(model_data)

        predictions = np.split(predictions, predictions.shape[0], axis = 0)

        return predictions
