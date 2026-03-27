class ModelManager:
    def __init__(self, models=None, metrics=None):
        self._models = models if models is not None else {}
        self._metrics = metrics if metrics is not None else {}

    def new_model(self):
        pass

    def del_model(self):
        pass

    def save_model(self):
        pass

    def train(self):
        pass

    def predict(self):
        pass

    def evaluate(self):
        pass