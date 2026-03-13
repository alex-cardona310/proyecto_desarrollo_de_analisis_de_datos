class DataSource:
    def __init__(self, source_id, data_type, meta=None):
        self.id = source_id
        self.type = data_type
        self.meta = meta if meta is not None else {}

    def read(self):
        pass