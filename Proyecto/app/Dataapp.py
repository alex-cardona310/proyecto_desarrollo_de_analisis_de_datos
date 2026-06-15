import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scraping.web_scraper import WebScraper

# Optional import for SQL support. If SQLAlchemy is not installed, SQL features will be disabled
try:
    from sqlalchemy import create_engine, inspect
except Exception:
    create_engine = None
    inspect = None
from tkinter import Tk, filedialog


class DataApp:

    def __init__(self):
        self.dataset = None
        self.engine = None  # Reemplaza self.connection de sqlite3
        self.source_type = None
        self.sql_tables = []

    def run(self):
        print("=" * 60)
        print("Data Analysis App")
        print("=" * 60)

        self.load_source()

        while True:
            self.show_menu()
            option = input("Choose an option: ").strip()

            if option == "1":
                self.preview_dataset()

            elif option == "2":
                self.dataset_info()

            elif option == "3":
                self.clean_data()

            elif option == "4":
                self.run_eda()

            elif option == "5":
                self.visualize_data()

            elif option == "6":
                self.show_sql_tables()

            elif option == "7":
                scraper = WebScraper()
                self.dataset = scraper.scrape_data()
                print("Web scraping completed successfully.")

            elif option == "8":
                self.load_source()

            elif option == "9":
                pass

            elif option == "10":
                print("Exiting program...")
                if self.engine:
                    self.engine.dispose()  # Cierra el pool de conexiones a la nube
                break

            else:
                print("Invalid option.")

    def show_menu(self):
        print("\nMenu")
        print("=" * 60)
        print("1. Preview dataset")
        print("2. View dataset information")
        print("3. Data cleaning")
        print("4. Exploratory Data Analysis")
        print("5. Data Visualization")
        print("6. Visualize SQL tables")
        print("7. Web Scraping")
        print("8. Load another data source")
        print("9. Models")
        print("10. Exit")

    def select_file(self, file_type):
        root = Tk()
        root.withdraw()

        if file_type == "csv":
            path = filedialog.askopenfilename(
                title="Selecciona un archivo CSV",
                filetypes=[("CSV files", "*.csv")],
            )

        elif file_type == "tsv":
            path = filedialog.askopenfilename(
                title="Selecciona un archivo TSV",
                filetypes=[("TSV files", "*.tsv")],
            )
        else:
            path = ""

        root.destroy()
        return path

    def save_file_dialog(self, file_type):
        root = Tk()
        root.withdraw()

        if file_type == "csv":
            path = filedialog.asksaveasfilename(
                title="Guardar archivo CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
            )

        elif file_type == "tsv":
            path = filedialog.asksaveasfilename(
                title="Guardar archivo TSV",
                defaultextension=".tsv",
                filetypes=[("TSV files", "*.tsv")],
            )

        else:
            path = ""

        root.destroy()
        return path

    def save_plot_dialog(self):
        root = Tk()
        root.withdraw()

        path = filedialog.asksaveasfilename(
            title="Guardar gráfica",
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("JPG image", "*.jpg"),
                ("PDF file", "*.pdf"),
            ],
        )

        root.destroy()
        return path

    def ask_save_plot_after_close(self, figure):
        while True:
            print("\nWhat do you want to do with this chart?")
            print("1. Save chart")
            print("2. Close without saving")

            option = input("Choose an option: ").strip()

            if option == "1":
                path = self.save_plot_dialog()

                if path:
                    figure.savefig(path, bbox_inches="tight")
                    print(f"Chart saved successfully at: {path}")
                else:
                    print("Save cancelled.")
                break

            elif option == "2":
                print("Chart closed without saving.")
                break

            else:
                print("Invalid option.")

    def load_source(self):
        print("\nSelect data source:")
        print("1. CSV")
        print("2. TSV")
        print("3. Cloud SQL Database")

        option = input("Option: ").strip()

        if option == "1":
            path = self.select_file("csv")
            if path:
                self.load_csv(path)
            else:
                print("No file selected.")

        elif option == "2":
            path = self.select_file("tsv")
            if path:
                self.load_tsv(path)
            else:
                print("No file selected.")

        elif option == "3":
            print("\n--- SQL Authentication ---")
            user_input = input("User: ").strip()
            pass_input = input("Password: ").strip()

            if user_input == "admin" and pass_input == "none":
                # Solicita directamente el URI de conexión de tu proveedor en la nube
                print("\nEjemplo de URI: postgresql://user:password@host:5432/dbname")
                db_uri = input("Introduce la URI de la base de datos en la nube: ").strip()
                
                if db_uri:
                    self.connect_sql(db_uri)
                else:
                    print("No URI provided.")
            else:
                print("Access Denied: Invalid user or password.")

    def load_csv(self, path):
        try:
            self.dataset = pd.read_csv(path)
            self.source_type = "csv"
            print("CSV file loaded successfully.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")

    def load_tsv(self, path):
        try:
            self.dataset = pd.read_csv(path, sep="\t")
            self.source_type = "tsv"
            print("TSV file loaded successfully.")
        except Exception as e:
            print(f"Error loading TSV file: {e}")

    def connect_sql(self, db_uri):
        try:
            if create_engine is None or inspect is None:
                print("SQLAlchemy is not installed. SQL features are unavailable.")
                return
            # Crea el motor de conexión global compatible con bases de datos en la nube
            self.engine = create_engine(db_uri)
            self.source_type = "sql"
            print("Connected to Cloud SQL database successfully.")

            # Utiliza el inspector de SQLAlchemy para extraer los nombres de las tablas en la nube
            inspector = inspect(self.engine)
            self.sql_tables = inspector.get_table_names()

            if not self.sql_tables:
                print("No tables found in cloud database.")
                return

            print("\nAvailable tables:")
            for i, table in enumerate(self.sql_tables, start=1):
                print(f"{i}. {table}")

            choice = input("Choose table number: ").strip()

            if not choice.isdigit():
                print("Invalid table option.")
                return

            choice = int(choice) - 1

            if choice < 0 or choice >= len(self.sql_tables):
                print("Invalid table number.")
                return

            table_name = self.sql_tables[choice]
            
            # Lee la tabla directamente usando el Engine de SQLAlchemy
            self.dataset = pd.read_sql_query(
                f"SELECT * FROM {table_name}", 
                con=self.engine
            )

            print(f"Table '{table_name}' loaded successfully from cloud.")

        except Exception as e:
            print(f"Error connecting to Cloud SQL database: {e}")

    def preview_dataset(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        print("\nDataset preview:")
        print(self.dataset.head())
        input("\nPress Enter to continue...")

    def dataset_info(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        print("\nDataset information:")
        print(f"Source type: {self.source_type}")
        print(f"Rows and columns: {self.dataset.shape}")

        print("\nColumns:")
        print(list(self.dataset.columns))

        print("\nData types:")
        print(self.dataset.dtypes)
        input("\nPress Enter to continue...")

    def clean_data(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        while True:
            print("\nData Cleaning")
            print("=" * 60)
            print("1. Remove duplicates")
            print("2. Remove rows with null values")
            print("3. Fill empty values")
            print("4. Convert column type")
            print("5. Remove outliers")
            print("6. Normalize numeric columns")
            print("7. Save clean dataset")
            print("8. Back to main menu")

            option = input("Choose a cleaning option: ").strip()

            if option == "1":
                before = len(self.dataset)
                self.dataset = self.dataset.drop_duplicates().reset_index(drop=True)
                after = len(self.dataset)
                print(f"Duplicates removed: {before - after}")

            elif option == "2":
                before = len(self.dataset)
                self.dataset = self.dataset.dropna().reset_index(drop=True)
                after = len(self.dataset)
                print(f"Rows removed: {before - after}")

            elif option == "3":
                print("\nColumns:")
                print(list(self.dataset.columns))

                column = input("Choose column: ").strip()

                if column not in self.dataset.columns:
                    print("Invalid column.")
                    continue

                value = input("Value to fill empty cells: ").strip()

                self.dataset[column] = self.dataset[column].replace(
                    r"^\s*$", pd.NA, regex=True
                )
                self.dataset[column] = self.dataset[column].fillna(value)
                print("Empty values filled.")

            elif option == "4":
                print("\nColumns:")
                print(list(self.dataset.columns))

                column = input("Choose column: ").strip()

                if column not in self.dataset.columns:
                    print("Invalid column.")
                    continue

                print("Available types: int, float, str")
                new_type = input("Choose type: ").strip().lower()

                try:
                    if new_type == "int":
                        self.dataset[column] = self.dataset[column].astype(int)
                    elif new_type == "float":
                        self.dataset[column] = self.dataset[column].astype(float)
                    elif new_type == "str":
                        self.dataset[column] = self.dataset[column].astype(str)
                    else:
                        print("Invalid type.")
                        continue
                    print("Column type converted successfully.")
                except Exception as e:
                    print(f"Error converting column: {e}")

            elif option == "5":
                numeric_columns = self.dataset.select_dtypes(
                    include=["number"]
                ).columns.tolist()

                if not numeric_columns:
                    print("No numeric columns available.")
                    continue

                print("\nNumeric columns:")
                print(numeric_columns)

                column = input("Choose numeric column: ").strip()

                if column not in numeric_columns:
                    print("Invalid numeric column.")
                    continue

                q1 = self.dataset[column].quantile(0.25)
                q3 = self.dataset[column].quantile(0.75)
                iqr = q3 - q1

                lower_limit = q1 - 1.5 * iqr
                upper_limit = q3 + 1.5 * iqr

                before = len(self.dataset)
                self.dataset = self.dataset[
                    (self.dataset[column] >= lower_limit) &
                    (self.dataset[column] <= upper_limit)
                ].reset_index(drop=True)
                after = len(self.dataset)

                print(f"Outliers removed: {before - after}")

            elif option == "6":
                numeric_columns = self.dataset.select_dtypes(
                    include=["number"]
                ).columns.tolist()

                if not numeric_columns:
                    print("No numeric columns available.")
                    continue

                for column in numeric_columns:
                    min_value = self.dataset[column].min()
                    max_value = self.dataset[column].max()

                    if max_value != min_value:
                        self.dataset[column] = (
                            (self.dataset[column] - min_value) /
                            (max_value - min_value)
                        )
                print("Numeric columns normalized.")

            elif option == "7":
                print("\nAvailable formats:")
                print("1. CSV")
                print("2. TSV")

                format_option = input("Choose format: ").strip()

                if format_option == "1":
                    path = self.save_file_dialog("csv")
                    if path:
                        self.dataset.to_csv(path, index=False)
                        print(f"Dataset saved at: {path}")
                    else:
                        print("Save cancelled.")

                elif format_option == "2":
                    path = self.save_file_dialog("tsv")
                    if path:
                        self.dataset.to_csv(path, sep="\t", index=False)
                        print(f"Dataset saved at: {path}")
                    else:
                        print("Save cancelled.")
                else:
                    print("Invalid format.")

            elif option == "8":
                break
            else:
                print("Invalid option.")

    def run_eda(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        numeric = self.dataset.select_dtypes(include=["number"])

        if numeric.empty:
            print("No numeric columns available.")
            return

        summary = pd.DataFrame({
            "mean": numeric.mean(),
            "median": numeric.median(),
            "std_dev": numeric.std(),
            "q1": numeric.quantile(0.25),
            "q2": numeric.quantile(0.50),
            "q3": numeric.quantile(0.75),
        })

        print("\nSummary statistics:\n")
        formatted_summary = summary.map(lambda x: f"{x:,.2f}")
        print(formatted_summary.to_string())

        print("\nCorrelation matrix:\n")
        corr = numeric.corr()
        formatted_corr = corr.map(lambda x: f"{x:,.2f}")
        print(formatted_corr.to_string())

        input("\nPress Enter to continue...")

    def visualize_data(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return

        while True:
            print("\nData Visualization")
            print("=" * 60)
            print("1. Histogram")
            print("2. Bar chart")
            print("3. Pie chart")
            print("4. Scatter plot")
            print("5. Line chart")
            print("6. Boxplot")
            print("7. Correlation heatmap")
            print("8. Back to main menu")

            option = input("Choose a chart type: ").strip()

            numeric_columns = self.dataset.select_dtypes(
                include=["number"]
            ).columns.tolist()
            all_columns = self.dataset.columns.tolist()

            if option == "1":
                print("\nNumeric columns:")
                print(numeric_columns)

                column = input("Choose a numeric column: ").strip()

                if column in numeric_columns:
                    fig = plt.figure(figsize=(8, 5))
                    plt.hist(
                        self.dataset[column].dropna(),
                        bins=10,
                        edgecolor="black",
                    )
                    plt.title(f"Histogram of {column}")
                    plt.xlabel(column)
                    plt.ylabel("Frequency")

                    plt.show()
                    self.ask_save_plot_after_close(fig)
                    plt.close(fig)
                else:
                    print("Invalid numeric column.")

            elif option == "2":
                print("\nColumns:")
                print(all_columns)

                column = input("Choose a column: ").strip()

                if column in all_columns:
                    fig = plt.figure(figsize=(8, 5))
                    self.dataset[column].value_counts().head(10).plot(
                        kind="bar"
                    )
                    plt.title(f"Bar chart of {column}")
                    plt.xlabel(column)
                    plt.ylabel("Frequency")
                    plt.xticks(rotation=45)
                    plt.tight_layout()

                    plt.show()
                    self.ask_save_plot_after_close(fig)
                    plt.close(fig)
                else:
                    print("Invalid column.")

            elif option == "3":
                print("\nColumns:")
                print(all_columns)

                column = input("Choose a column: ").strip()

                if column in all_columns:
                    fig = plt.figure(figsize=(8, 8))
                    self.dataset[column].value_counts().head(10).plot(
                        kind="pie", autopct="%1.1f%%"
                    )
                    plt.title(f"Pie chart of {column}")
                    plt.ylabel("")

                    plt.show()
                    self.ask_save_plot_after_close(fig)
                    plt.close(fig)
                else:
                    print("Invalid column.")

            elif option == "4":
                if len(numeric_columns) < 2:
                    print("At least two numeric columns are required.")
                    continue

                print("\nNumeric columns:")
                print(numeric_columns)

                x_column = input("Choose X column: ").strip()
                y_column = input("Choose Y column: ").strip()

                if x_column in numeric_columns and y_column in numeric_columns:
                    fig = plt.figure(figsize=(8, 5))
                    plt.scatter(self.dataset[x_column], self.dataset[y_column])
                    plt.title(f"Scatter plot: {x_column} vs {y_column}")
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)

                    plt.show()
                    self.ask_save_plot_after_close(fig)
                    plt.close(fig)
                else:
                    print("Both columns must be numeric.")

            elif option == "5":
                print("\nNumeric columns:")
                print(numeric_columns)

                column = input("Choose a numeric column: ").strip()

                if column in numeric_columns:
                    fig = plt.figure(figsize=(8, 5))
                    self.dataset[column].reset_index(drop=True).plot(
                        kind="line"
                    )
                    plt.title(f"Line chart of {column}")
                    plt.xlabel("Index")
                    plt.ylabel(column)

                    plt.show()
                    self.ask_save_plot_after_close(fig)
                    plt.close(fig)
                else:
                    print("Invalid numeric column.")

            elif option == "6":
                print("\nNumeric columns:")
                print(numeric_columns)

                column = input("Choose a numeric column: ").strip()

                if column in numeric_columns:
                    fig = plt.figure(figsize=(8, 5))
                    sns.boxplot(y=self.dataset[column])
                    plt.title(f"Boxplot of {column}")
                    plt.ylabel(column)

                    plt.show()
                    self.ask_save_plot_after_close(fig)
                    plt.close(fig)
                else:
                    print("Invalid numeric column.")

            elif option == "7":
                if len(numeric_columns) < 2:
                    print("At least two numeric columns are required.")
                    continue

                corr = self.dataset[numeric_columns].corr()

                fig = plt.figure(figsize=(10, 8))
                sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
                plt.title("Correlation Heatmap")

                plt.show()
                self.ask_save_plot_after_close(fig)
                plt.close(fig)

            elif option == "8":
                break
            else:
                print("Invalid option.")

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

        input("\nPress Enter to continue...")