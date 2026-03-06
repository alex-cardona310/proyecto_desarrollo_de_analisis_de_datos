from typing import Any, Dict, List, Protocol

class DataSource:
    def __init__(self, id: str, dtype: str, meta: Dict[str,Any]):
        self._id = id
        self._type = dtype
        self._meta = meta
    def read(self) -> Any:
        raise NotImplementedError

class DataIngestor:
    def __init__(self, config: Dict[str,Any]):
        self._config = config
        self._sources: List[DataSource] = []
    def register(self, src: DataSource):
        self._sources.append(src)
    def load(self, path: str) -> Any:
        # detectar tipo y delegar a DataSource concreto
        pass

class DataFrameWrapper:
    def __init__(self, df):
        self._df = df
    def to_pandas(self):
        return self._df

class DataRepository:
    def __init__(self):
        self._storage: Dict[str, DataFrameWrapper] = {}
    def save(self, id: str, data: DataFrameWrapper):
        self._storage[id] = data
    def get(self, id: str) -> DataFrameWrapper:
        return self._storage[id]

class CleanerStrategy(Protocol):
    def apply(self, data: DataFrameWrapper) -> DataFrameWrapper: ...

class DataCleaner:
    def __init__(self):
        self._rules: List[CleanerStrategy] = []
    def add_rule(self, r: CleanerStrategy):
        self._rules.append(r)
    def clean(self, data: DataFrameWrapper) -> DataFrameWrapper:
        for r in self._rules:
            data = r.apply(data)
        return data

class AnalysisModule(Protocol):
    def run(self, data: DataFrameWrapper) -> Dict[str,Any]: ...

class Analyzer:
    def __init__(self):
        self._pipeline: List[AnalysisModule] = []
    def add_module(self, m: AnalysisModule):
        self._pipeline.append(m)
    def analyze(self, data: DataFrameWrapper, mode: str) -> Dict[str,Any]:
        result = {}
        for m in self._pipeline:
            result.update(m.run(data))
        return result

class Plotter(Protocol):
    def plot(self, data, kind: str, options: Dict[str,Any]): ...

class Visualizer:
    def __init__(self):
        self._plotters: List[Plotter] = []
    def visualize(self, result: Dict[str,Any], kind: str):
        for p in self._plotters:
            p.plot(result, kind, {})
            