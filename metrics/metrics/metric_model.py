from metrics.metrics.feature_extractor import FeatureExtractor
from metrics.metrics.readout_model import ReadoutModel

class MetricModel(object):
    """
    Fits and evaluates readout_model on features to predict labels using metric_fn
    """
    def __init__(self,
            feature_extractor,
            readout_model,
            metric_fn):
        assert isinstance(feature_extractor, FeatureExtractor)

        self._feature_extractor = feature_extractor
        self._readout_model = readout_model
        self._metric_fn = metric_fn


    def fit(self,
            data,
            labels):
        features = self._feature_extractor(data)
        self._readout_model.fit(features, labels)


    def predict(self,
            data):
        features = self._feature_extractor(data)
        predictions = self._readout_model.predict(features)
        return predictions


    def score(self,
            data,
            labels):
        predictions = self.predict(data)
        metric = self._metric_fn(predictions, labels)
        return metric



class BatchMetricModel(MetricModel):
    def __init__(self,
            feature_extractor,
            readout_model,
            metric_fn,
            label_fn = lambda x: x):
        super(BatchMetricModel, self).__init__(feature_extractor, readout_model, metric_fn)
        self._label_fn = label_fn


    def extract_features_labels(self,
            data,
            num_steps = 2**10000):
        features = []
        labels = []
        for _ in range(num_steps):
            try:
                batch = next(data)
                features.append(self._feature_extractor(batch))
                labels.append(self._label_fn(batch))
            except StopIteration:
                break
        return features, labels


    def fit(self,
            data,
            num_steps = 2**10000):
        features, labels = self.extract_features_labels(data, num_steps)
        self._readout_model.fit(features, labels)


    def predict(self,
            data,
            num_steps = 2**10000):
        features, _ = self.extract_features_labels(data, num_steps)
        predictions = self._readout_model.predict(features)
        return predictions


    def score(self,
            data,
            num_steps = 2**10000):
        features, labels = self.extract_features_labels(data, num_steps)
        predictions = self._readout_model.predict(features)
        metric = self._metric_fn(predictions, labels)
        return metric
