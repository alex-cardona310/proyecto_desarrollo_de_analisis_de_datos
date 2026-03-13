class DataRepository:
    def __init__(self, dataset=None, data_path="", logger=None):
        self.dataset = dataset if dataset is not None else {}
        self.dataPath = data_path
        self.logger = logger

    def save(self):
        pass

    def get(self):
        pass

    def remove(self):
        pass

    def list(self):
        pass