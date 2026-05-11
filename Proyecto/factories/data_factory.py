from pathlib import Path
from ingestion.data import Data


class DataFactory:
    SUPPORTED_EXTENSIONS = {
        ".csv": "csv",
        ".tsv": "tsv",
        ".xlsx": "excel",
        ".xls": "excel",
        ".db": "db",
        ".sqlite": "db",
        ".sqlite3": "db",
    }

    @staticmethod
    def create(source_path: str) -> Data:
        path = Path(source_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {source_path}")

        suffix = path.suffix.lower()

        if suffix not in DataFactory.SUPPORTED_EXTENSIONS:
            supported = ", ".join(DataFactory.SUPPORTED_EXTENSIONS.keys())
            raise ValueError(
                f"Unsupported file extension: {suffix}. Supported: {supported}"
            )

        source_type = DataFactory.SUPPORTED_EXTENSIONS[suffix]

        data = Data(
            name=path.stem,
            source_path=str(path),
            source_type=source_type,
        )
        data.load()
        return data