class ReadoutModel(object):
    """
    Fits model on data to predict labels
    """
    def __init__(self, model=None):
        self._model = model


    def fit(self, data, labels, **kwargs):
        assert hasattr(self._model, "fit"), \
                ("model does not have 'fit' method!")
        self._model.fit(data, labels, **kwargs)


    def predict(self, data, **kwargs):
        assert hasattr(self._model, "predict"), \
                ("model does not have 'predict' method!")
        return self._model.predict(data, **kwargs)



class IdentityModel(ReadoutModel):
    """
    Predicts labels to be identical to data
    """
    def fit(self, data, labels, **kwargs):
        pass

    def predict(self, data, **kwargs):
        return data
