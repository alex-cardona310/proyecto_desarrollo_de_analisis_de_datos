import pandas as pd
import sqlite3


class Analyzer:
    def __init__(self, df=None, pipeline=None):
        self.df = df
        self.pipeline = pipeline if pipeline is not None else []

    def add_module(self, module):
        self.pipeline.append(module)

    def analyze(self):
        results = {}
        for module in self.pipeline:
            results[module.__name__] = module()
        return results

    def SummaryStatistics(self):
        if self.df is None:
            return "No dataset loaded."

        numeric_df = self.df.select_dtypes(include=["number"])

        if numeric_df.empty:
            return "This dataset has no numeric columns for EDA."

        summary = pd.DataFrame({
            "mean": numeric_df.mean(),
            "median": numeric_df.median(),
            "std_dev": numeric_df.std(),
            "q1": numeric_df.quantile(0.25),
            "q2": numeric_df.quantile(0.50),
            "q3": numeric_df.quantile(0.75)
        })

        return summary.round(2)


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
                self.run_eda()

            elif option == "4":
                self.show_sql_tables()

            elif option == "5":
                self.load_another_source()

            elif option == "6":
                print("Exiting program...")
                if self.connection:
                    self.connection.close()
                break

            else:
                print("Invalid option. Try again.")

    def load_source_at_start(self):
        print("\nChoose the type of data source:")
        print("1. CSV file")
        print("2. TSV file")
        print("3. SQL database")

        source_option = input("Option: ").strip()

        if source_option == "1":
            file_path = input("Enter the path of the .csv file: ").strip()
            self.load_csv(file_path)

        elif source_option == "2":
            file_path = input("Enter the path of the .tsv file: ").strip()
            self.load_tsv(file_path)

        elif source_option == "3":
            db_path = input("Enter the path of the SQL database (.db or .sqlite): ").strip()
            self.connect_sql(db_path)

        else:
            print("Invalid option.")
            self.load_source_at_start()

    def load_csv(self, file_path):
        try:
            self.dataset = pd.read_csv(file_path)
            self.dataset_name = file_path
            self.source_type = "csv"
            print("\nCSV file loaded successfully.")
        except Exception as e:
            print(f"\nError loading CSV file: {e}")

    def load_tsv(self, file_path):
        try:
            self.dataset = pd.read_csv(file_path, sep="\t")
            self.dataset_name = file_path
            self.source_type = "tsv"
            print("\nTSV file loaded successfully.")
        except Exception as e:
            print(f"\nError loading TSV file: {e}")

    def connect_sql(self, db_path):
        try:
            self.connection = sqlite3.connect(db_path)
            self.source_type = "sql"
            self.dataset_name = db_path
            print("\nSQL database connected successfully.")

            self.sql_tables = self.get_sql_tables()

            if not self.sql_tables:
                print("No tables were found in the database.")
                return

            print("\nAvailable SQL tables:")
            for i, table in enumerate(self.sql_tables, start=1):
                print(f"{i}. {table}")

            table_option = input("Choose a table number to load: ").strip()

            if not table_option.isdigit():
                print("Invalid option.")
                return

            table_index = int(table_option) - 1

            if table_index < 0 or table_index >= len(self.sql_tables):
                print("Invalid table number.")
                return

            selected_table = self.sql_tables[table_index]
            self.dataset = pd.read_sql_query(f"SELECT * FROM {selected_table}", self.connection)
            print(f"\nSQL table '{selected_table}' loaded successfully.")

        except Exception as e:
            print(f"\nError connecting to SQL database: {e}")

    def get_sql_tables(self):
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            tables_df = pd.read_sql_query(query, self.connection)
            return tables_df["name"].tolist()
        except Exception as e:
            print(f"Error retrieving SQL tables: {e}")
            return []

    def show_menu(self):
        print("Menu")
        print("=" * 60)
        print("1. Preview dataset")
        print("2. View dataset information")
        print("3. Exploratory Data Analysis")
        print("4. Visualize SQL tables")
        print("5. Load another data source")
        print("6. Exit")

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

        print("\nExploratory Data Analysis:")
        analyzer = Analyzer(self.dataset)
        analyzer.add_module(analyzer.SummaryStatistics)
        results = analyzer.analyze()

        print("\nSummary statistics:")
        print(results["SummaryStatistics"])

    def show_sql_tables(self):
        if self.source_type != "sql":
            print("The current source is not an SQL database.")
            return

        if not self.sql_tables:
            print("No SQL tables available.")
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


def main():
    app = DataApp()
    app.run()


if __name__ == "__main__":
    main()