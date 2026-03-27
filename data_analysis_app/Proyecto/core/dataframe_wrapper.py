class DataFrameWrapper:
    def __init__(self, df=None, schema=None):
        self._df = df
        self._schema = schema if schema is not None else {}

    def to_pandas(self):
        pass

    def from_raw(self):
        pass

    def _get_columns(self):
        pass

    def schema(self):
        pass