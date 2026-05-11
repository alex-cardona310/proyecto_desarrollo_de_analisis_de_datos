from ingestion.data import Data


class Repository:
    def __init__(self) -> None:
        self.items: dict[str, Data] = {}

    def add(self, data: Data) -> None:
        if data.id in self.items:
            raise ValueError(f"A dataset with id '{data.id}' already exists.")
        self.items[data.id] = data

    def remove(self, data_id: str) -> None:
        if data_id not in self.items:
            raise KeyError(f"No dataset found with id: {data_id}")
        del self.items[data_id]

    def get(self, data_id: str) -> Data:
        if data_id not in self.items:
            raise KeyError(f"No dataset found with id: {data_id}")
        return self.items[data_id]

    def get_by_name(self, name: str) -> Data:
        for data in self.items.values():
            if data.name == name:
                return data
        raise KeyError(f"No dataset found with name: {name}")

    def exists(self, data_id: str) -> bool:
        return data_id in self.items

    def list_all(self) -> list[dict]:
        return [
            {
                "id": data.id,
                "name": data.name,
                "type": data.source_type,
                "loaded_at": data.loaded_at,
            }
            for data in self.items.values()
        ]

    def show_preview(self, data_id: str, n: int = 5):
        data = self.get(data_id)
        return data.preview(n)

    def show_preview_by_name(self, name: str, n: int = 5):
        data = self.get_by_name(name)
        return data.preview(n)

    def count(self) -> int:
        return len(self.items)