from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
import uuid
import sqlite3

import pandas as pd


@dataclass
class Data:
    name: str
    source_path: str
    source_type: str
    content: Optional[Union[pd.DataFrame, dict[str, pd.DataFrame]]] = None
    metadata: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    loaded_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def load(self) -> None:
        path = Path(self.source_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {self.source_path}")

        source_type = self.source_type.lower()

        if source_type == "csv":
            self.content = pd.read_csv(path)

        elif source_type == "tsv":
            self.content = pd.read_csv(path, sep="\t")

        elif source_type == "excel":
            self.content = pd.read_excel(path, sheet_name=None)

        elif source_type == "db":
            self.content = self._load_sqlite_database(path)

        else:
            raise ValueError(f"Unsupported source type: {self.source_type}")

        self.metadata = self._build_metadata()

    def _load_sqlite_database(self, db_path: Path) -> dict[str, pd.DataFrame]:
        tables_dict: dict[str, pd.DataFrame] = {}

        conn = sqlite3.connect(db_path)
        try:
            tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
            tables_df = pd.read_sql_query(tables_query, conn)
            table_names = tables_df["name"].tolist()

            for table_name in table_names:
                query = f'SELECT * FROM "{table_name}"'
                tables_dict[table_name] = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        return tables_dict

    def _build_metadata(self) -> dict:
        if isinstance(self.content, pd.DataFrame):
            return {
                "kind": "single_table",
                "rows": int(self.content.shape[0]),
                "columns": int(self.content.shape[1]),
                "column_names": list(self.content.columns),
            }

        if isinstance(self.content, dict):
            detail = {}
            for name, df in self.content.items():
                detail[name] = {
                    "rows": int(df.shape[0]),
                    "columns": int(df.shape[1]),
                    "column_names": list(df.columns),
                }

            return {
                "kind": "multiple_tables",
                "count": len(self.content),
                "items": detail,
            }

        return {}

    def preview(self, n: int = 5):
        if self.content is None:
            raise ValueError("Data has not been loaded yet.")

        if isinstance(self.content, pd.DataFrame):
            return self.content.head(n)

        if isinstance(self.content, dict):
            return {name: df.head(n) for name, df in self.content.items()}

        raise TypeError("Unsupported content type.")

    def preview_item(self, item_name: str, n: int = 5) -> pd.DataFrame:
        if self.content is None:
            raise ValueError("Data has not been loaded yet.")

        if isinstance(self.content, pd.DataFrame):
            raise ValueError("This dataset contains only one table. Use preview().")

        if item_name not in self.content:
            raise KeyError(f"Item '{item_name}' not found.")

        return self.content[item_name].head(n)

    def get_full_item(self, item_name: str) -> pd.DataFrame:
        if self.content is None:
            raise ValueError("Data has not been loaded yet.")

        if isinstance(self.content, pd.DataFrame):
            raise ValueError("This dataset contains only one table.")

        if item_name not in self.content:
            raise KeyError(f"Item '{item_name}' not found.")

        return self.content[item_name]

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "source_path": self.source_path,
            "source_type": self.source_type,
            "loaded_at": self.loaded_at,
            "metadata": self.metadata,
        }

    def reload(self) -> None:
        self.load()

    def __str__(self) -> str:
        return f"Data(id='{self.id}', name='{self.name}', type='{self.source_type}')"