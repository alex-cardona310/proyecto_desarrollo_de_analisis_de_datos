import pandas as pd

from repository.repository import Repository
from factories.data_factory import DataFactory


class DataApp:
    def __init__(self) -> None:
        self.repository = Repository()

    def run(self) -> None:
        while True:
            print("\n" + "=" * 60)
            print("Data Analysis App")
            print("=" * 60)
            print("1. Load a file")
            print("2. List loaded datasets")
            print("3. View dataset info")
            print("4. Preview a dataset")
            print("5. Preview a specific sheet/table")
            print("6. Remove a dataset")
            print("7. Exit")

            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    self.load_file_flow()
                elif choice == "2":
                    self.list_datasets_flow()
                elif choice == "3":
                    self.view_dataset_info_flow()
                elif choice == "4":
                    self.preview_dataset_flow()
                elif choice == "5":
                    self.preview_specific_item_flow()
                elif choice == "6":
                    self.remove_dataset_flow()
                elif choice == "7":
                    print("Goodbye.")
                    break
                else:
                    print("Invalid option. Please choose a number from 1 to 7.")

            except Exception as exc:
                print(f"Error: {exc}")

    def load_file_flow(self) -> None:
        file_path = input("Enter the file path: ").strip()

        data = DataFactory.create(file_path)
        self.repository.add(data)

        print("\nDataset loaded successfully.")
        print(f"ID: {data.id}")
        print(f"Name: {data.name}")
        print(f"Type: {data.source_type}")

    def list_datasets_flow(self) -> None:
        datasets = self.repository.list_all()

        if not datasets:
            print("No datasets loaded.")
            return

        print("\nLoaded datasets:")
        for index, item in enumerate(datasets, start=1):
            print(
                f"{index}. "
                f"ID={item['id']} | "
                f"Name={item['name']} | "
                f"Type={item['type']} | "
                f"Loaded At={item['loaded_at']}"
            )

    def view_dataset_info_flow(self) -> None:
        data_id = input("Enter dataset ID: ").strip()
        data = self.repository.get(data_id)
        info = data.get_info()

        print("\nDataset info:")
        print(f"ID: {info['id']}")
        print(f"Name: {info['name']}")
        print(f"Path: {info['source_path']}")
        print(f"Type: {info['source_type']}")
        print(f"Loaded At: {info['loaded_at']}")
        print("Metadata:")
        print(info["metadata"])

    def preview_dataset_flow(self) -> None:
        data_id = input("Enter dataset ID: ").strip()
        n = input("How many rows to preview? (default 5): ").strip()

        n_rows = int(n) if n else 5
        preview = self.repository.show_preview(data_id, n_rows)

        print("\nPreview:")
        if isinstance(preview, pd.DataFrame):
            print(preview)
        elif isinstance(preview, dict):
            for name, df in preview.items():
                print(f"\n--- {name} ---")
                print(df)
        else:
            print(preview)

    def preview_specific_item_flow(self) -> None:
        data_id = input("Enter dataset ID: ").strip()
        data = self.repository.get(data_id)

        if isinstance(data.content, pd.DataFrame):
            print("This dataset only contains one table. Use the normal preview option.")
            return

        print("\nAvailable items:")
        for item_name in data.content.keys():
            print(f"- {item_name}")

        item_name = input("Enter sheet/table name: ").strip()
        n = input("How many rows to preview? (default 5): ").strip()
        n_rows = int(n) if n else 5

        preview = data.preview_item(item_name, n_rows)

        print(f"\nPreview of '{item_name}':")
        print(preview)

    def remove_dataset_flow(self) -> None:
        data_id = input("Enter dataset ID to remove: ").strip()
        self.repository.remove(data_id)
        print("Dataset removed successfully.")