import pandas as pd
import sqlite3
import os
from cleaning.cleaner import Cleaner
from analysis.analyzer import Analyzer


class DataApp:
    def __init__(self):
        self.dataset = None
        self.dataset_name = None
        self.source_type = None
        self.connection = None
        self.sql_tables = []

    def run(self):
        print("=" * 60)
        print("Data Analysis App")
        print("=" * 60)

        self.load_source_at_start()

        while True:
            self.show_menu()
            option = input("Choose an option: ").strip()

            if option == "1":
                self.preview_dataset()
            elif option == "2":
                self.view_dataset_info()
            elif option == "3":
                self.run_cleaning()
            elif option == "4":
                self.run_eda()
            elif option == "5":
                self.show_sql_tables()
            elif option == "6":
                self.load_another_source()
            elif option == "7":
                print("Exiting program...")
                if self.connection:
                    self.connection.close()
                break
            else:
                print("Invalid option. Try again.")

            self.pause_and_clear()

    def load_source_at_start(self):
        print("\nChoose the type of data source:")
        print("1. CSV file")
        print("2. TSV file")
        print("3. SQL database")

        source_option = input("Option: ").strip()

        if source_option == "1":
            self.load_csv(input("Enter the path of the .csv file: ").strip())
        elif source_option == "2":
            self.load_tsv(input("Enter the path of the .tsv file: ").strip())
        elif source_option == "3":
            self.connect_sql(input("Enter the path of the SQL database (.db or .sqlite): ").strip())
        else:
            print("Invalid option.")
            self.load_source_at_start()

    def load_csv(self, file_path):
        self.dataset = pd.read_csv(file_path)
        self.dataset_name = file_path
        self.source_type = "csv"
        print("\nCSV file loaded successfully.")

    def load_tsv(self, file_path):
        self.dataset = pd.read_csv(file_path, sep="\t")
        self.dataset_name = file_path
        self.source_type = "tsv"
        print("\nTSV file loaded successfully.")

    def connect_sql(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.source_type = "sql"
        self.dataset_name = db_path
        print("\nSQL database connected successfully.")

        self.sql_tables = self.get_sql_tables()

        print("\nAvailable SQL tables:")
        for i, table in enumerate(self.sql_tables, start=1):
            print(f"{i}. {table}")

        table_index = int(input("Choose a table number to load: ").strip()) - 1
        selected_table = self.sql_tables[table_index]

        self.dataset = pd.read_sql_query(
            f"SELECT * FROM {selected_table}",
            self.connection
        )

        print(f"\nSQL table '{selected_table}' loaded successfully.")

    def get_sql_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables_df = pd.read_sql_query(query, self.connection)
        return tables_df["name"].tolist()

    def show_menu(self):
        print("Menu")
        print("=" * 60)
        print("1. Preview dataset")
        print("2. View dataset information")
        print("3. Data cleaning")
        print("4. Exploratory Data Analysis")
        print("5. Visualize SQL tables")
        print("6. Load another data source")
        print("7. Exit")

    def pause_and_clear(self):
        input("\nPress Enter to continue...")
        os.system("cls" if os.name == "nt" else "clear")

    def show_menu2(self):
        print("≽^-⩊-^≼ + Data cleaning + ≽^-⩊-^≼")
        print("=" * 60)
        print("1. Remove duplicates")
        print("2. Remove rows with nulls")
        print("3. Fill empty spaces")
        print("4. Convert data types")
        print("5. Remove outliers")
        print("6. Validate data range")
        print("7. Normalize")
        print("8. Save clean dataset")
        print("9. Go back to main menu")

    def preview_dataset(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        print("\nDataset preview:")
        print(self.dataset.head())

    def view_dataset_info(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        print("\nDataset information:")
        print(f"Source type: {self.source_type}")
        print(f"Source name/path: {self.dataset_name}")
        print(f"Shape: {self.dataset.shape}")
        print("\nColumns:")
        print(list(self.dataset.columns))
        print("\nData types:")
        print(self.dataset.dtypes)

    def run_eda(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        analyzer = Analyzer(self.dataset)
        analyzer.add_module(analyzer.SummaryStatistics)
        results = analyzer.analyze()

        print("\nSummary statistics:")
        print(results["SummaryStatistics"])

    def run_cleaning(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        cleaner = Cleaner(self.dataset)

        self.show_menu2()
        option = input("Choose a cleaning option: ").strip()

        if option == "1":
            self.dataset = cleaner.eliminar_duplicados()
        elif option == "2":
            self.dataset = cleaner.eliminar_filas_nulas()
        elif option == "3":
            columna = input("Column name: ").strip()
            self.dataset = cleaner.rellenar_espacios_vacios(columna)
        elif option == "4":
            columna = input("Column name: ").strip()
            self.dataset = cleaner.convertir_tipo_columna(columna)
        elif option == "5":
            columna = input("Column name: ").strip()
            self.dataset = cleaner.eliminar_outliers(columna)
        elif option == "6":
            columna = input("Column name: ").strip()
            self.dataset = cleaner.validar_rango_columna(columna)
        elif option == "7":
            self.dataset = cleaner.normalizar_dataframe()
        elif option == "8":
            self.dataset = cleaner.guardar_limpio()
        elif option == "9":
            return
        else:
            print("Invalid cleaning option.")
            return

        print("\nCleaning applied successfully.")

    def show_sql_tables(self):
        if self.source_type != "sql":
            print("The current source is not an SQL database.")
            return

        print("\nSQL tables:")
        for i, table in enumerate(self.sql_tables, start=1):
            print(f"{i}. {table}")

    def load_another_source(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.sql_tables = []

        self.dataset = None
        self.dataset_name = None
        self.source_type = None

        print("\nLoad another source")
        self.load_source_at_start()