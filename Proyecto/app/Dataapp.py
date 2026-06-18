import os
import json
import io
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from model_manager import ModelManager

try:
    from cleaning.cleaner import Cleaner
except ImportError:
    Cleaner = None

try:
    from scraping.web_scraper import WebScraper
except ImportError:
    WebScraper = None

try:
    from sqlalchemy import create_engine, inspect
except Exception:
    create_engine = None
    inspect = None

from tkinter import Tk, filedialog

class DataApp:

    def __init__(self):
        self.dataset = None
        self.engine = None  
        self.source_type = None
        self.sql_tables = []
        self.save_directory = r"C:/Users/aleva/Desktop/ESCOM/DAPCD/data_analysis_app/data_analysis_app/adicionales/Datasetsmodelos"

    def run(self):
        print("==================================================")
        print("          DATA ANALYSIS                           ")
        print("==================================================")
        self.load_source()

        while True:
            self.show_menu()
            option = input("Choose an option (1-10): ").strip()

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
                if WebScraper is not None:
                    scraper = WebScraper()
                    self.dataset = scraper.scrape_data()
                    print("[SUCCESS] Web scraping ingestion completed successfully.")
                else:
                    print("[ERROR] WebScraper module not found in context.")
            elif option == "8":
                self.load_source()
            elif option == "9":
                self.modeling_menu()
            elif option == "10":
                print("Closing system core handles. Program terminated.")
                if self.engine:
                    self.engine.dispose()  
                break
            else:
                print("[ERROR] Invalid operational entry selection.")

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

    def manage_chart_flow(self, fig, filename):
        """
        Muestra la gráfica de forma bloqueante y aislada, garantizando que 
        ninguna otra ventana en memoria se abra al mismo tiempo.
        """
        if fig is None:
            print(f"[WARNING] No chart data available for {filename}")
            return

        print(f"\n[INFO] Opening visualization window for: {filename}")
        print("--> IMPORTANT: Close the graphical chart window manually to return to terminal options.")

        # --- SOLUCIÓN DE AISLAMIENTO TOTAL ---
        # 1. Creamos una nueva figura limpia temporal copia de la estructura original
        # Esto rompe el link con el buffer global acumulado en ModelManager
        fig_single = plt.figure(figsize=fig.get_size_inches())
        
        # 2. Clonamos el diseño de los ejes y el contenido al nuevo lienzo aislado
        for ax in fig.axes:
            # Re-localizamos los subplots en la nueva figura independiente
            pos = ax.get_position()
            ax_new = fig_single.add_axes(pos)
            
            # Transferimos los elementos gráficos (líneas, scatter, colecciones)
            for line in ax.lines:
                ax_new.add_line(plt.Line2D(line.get_xdata(), line.get_ydata(), **line.properties()))
            for collection in ax.collections:
                ax_new.add_collection(collection)
            for patch in ax.patches:
                ax_new.add_patch(patch)
            for text in ax.texts:
                ax_new.text(text.get_position()[0], text.get_position()[1], text.get_text(), **text.properties())
                
            # Clonamos títulos y etiquetas de los ejes
            ax_new.set_title(ax.get_title())
            ax_new.set_xlabel(ax.get_xlabel())
            ax_new.set_ylabel(ax.get_ylabel())
            ax_new.set_xlim(ax.get_xlim())
            ax_new.set_ylim(ax.get_ylim())
            
        # Clonamos el título general si existe
        if fig._suptitle:
            fig_single.suptitle(fig._suptitle.get_text(), fontsize=fig._suptitle.get_fontsize())

        fig_single.tight_layout()

        # 3. Mostramos ÚNICAMENTE esta figura temporal e independiente
        plt.show(block=True) 

        # La terminal se congela aquí. Al dar clic en la X de la ventana, continúa abajo:
        print(f"\n--- Chart Options: {filename} ---")
        print("1. Save chart to disk layout location")
        print("2. Close chart window and clear buffer memory")
        
        while True:
            opcion = input("Select operation (1-2): ").strip()
            if opcion == "1":
                fig_single.savefig(filename, bbox_inches='tight')
                print(f"[SUCCESS] Chart successfully saved to disk as '{filename}'.")
                break
            elif opcion == "2":
                print("Visualization context dismissed without updates.")
                break
            else:
                print("Invalid choice. Please select 1 or 2.")

        # 4. Destruimos por completo la figura de la memoria antes de pasar a la siguiente iteración
        plt.close(fig_single)
        plt.close(fig)

    def select_file(self, file_type):
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title=f"Select source {file_type.upper()} file",
            filetypes=[(f"{file_type.upper()} files", f"*.{file_type}")] if file_type != "notebook" else [("Jupyter Notebooks", "*.ipynb")]
        )
        root.destroy()
        return path

    def save_file_dialog(self, file_type):
        root = Tk()
        root.withdraw()
        path = filedialog.asksaveasfilename(
            title=f"Save clean dataset as {file_type.upper()}",
            defaultextension=f".{file_type}",
            filetypes=[(f"{file_type.upper()} files", f"*.{file_type}")]
        )
        root.destroy()
        return path

    def load_source(self):
        print("\nSelect target data source format:")
        print("1. Standard CSV File Structure")
        print("2. Tab-Separated Values (TSV)")
        print("3. Cloud-Mounted Remote SQL Database")

        option = input("Select input pipeline (1-3): ").strip()

        if option == "1":
            path = self.select_file("csv")
            if path: self.load_csv(path)
            else: print("Pipeline initialization canceled.")
        elif option == "2":
            path = self.select_file("tsv")
            if path: self.load_tsv(path)
            else: print("Pipeline initialization canceled.")
        elif option == "3":
            print("\n--- Cloud SQL Server Secure Gate Authentication ---")
            user_input = input("Username: ").strip()
            pass_input = input("Secure Key Phrase: ").strip()

            if user_input == "admin" and pass_input == "none":
                db_uri = input("Input cloud database connection URI string: ").strip()
                if db_uri: self.connect_sql(db_uri)
            else:
                print("Authorization Denied: Handshake rejection.")

    def load_csv(self, path):
        try:
            self.dataset = pd.read_csv(path)
            self.source_type = "csv"
            print("[SUCCESS] Data engine mapped file contents safely from CSV.")
        except Exception as e:
            print(f"[CRITICAL] Operational filesystem crash: {e}")

    def load_tsv(self, path):
        try:
            self.dataset = pd.read_csv(path, sep="\t")
            self.source_type = "tsv"
            print("[SUCCESS] Data engine mapped file contents safely from TSV.")
        except Exception as e:
            print(f"[CRITICAL] Operational filesystem crash: {e}")

    def connect_sql(self, db_uri):
        if create_engine is None:
            print("[ERROR] SQLAlchemy libraries missing from current machine environment.")
            return
        try:
            self.engine = create_engine(db_uri)
            self.source_type = "sql"
            print("[SUCCESS] Secure cryptographic pipe hooked up to Cloud Database.")

            inspector = inspect(self.engine)
            self.sql_tables = inspector.get_table_names()

            if not self.sql_tables:
                print("[WARNING] No data tables found within current catalog namespace.")
                return

            print("\nAvailable Database Catalog Tables:")
            for i, table in enumerate(self.sql_tables, start=1):
                print(f"{i}. {table}")

            choice = input("Target relational table index value: ").strip()
            if not choice.isdigit(): return
            
            idx = int(choice) - 1
            if 0 <= idx < len(self.sql_tables):
                t_name = self.sql_tables[idx]
                self.dataset = pd.read_sql_query(f"SELECT * FROM {t_name}", con=self.engine)
                print(f"[SUCCESS] Synchronized internal memory with table: '{t_name}'")
        except Exception as e:
            print(f"[CRITICAL] Remote connection interface pipe failed: {e}")

    def preview_dataset(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return
        print("\nTop Row Records Preview:")
        print(self.dataset.head())
        input("\nPress Enter to continue...")

    def dataset_info(self):
        if self.dataset is None:
            print("No dataset loaded.")
            return
        print(f"\n[METADATA] Pipeline Format Flag: {self.source_type}")
        print(f"[METADATA] Vector Matrix Shape Dimensions: {self.dataset.shape}")
        print(f"[METADATA] Features Registry List: {list(self.dataset.columns)}")
        print("\nStructural Primitive Data Types:")
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
                if Cleaner is not None:
                    before = len(self.dataset)
                    cleaner_obj = Cleaner(self.dataset)
                    self.dataset = cleaner_obj.eliminar_duplicados()
                    after = len(self.dataset)
                    print(f"Duplicates removed: {before - after}")
                else:
                    print("Error: Cleaner module not found.")

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
                if Cleaner is not None:
                    cleaner_obj = Cleaner(self.dataset)
                    try:
                        self.dataset = cleaner_obj.rellenar_espacios_vacios(column, value)
                        print("Empty values filled.")
                    except ValueError as e:
                        print(e)
                else:
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
                numeric_columns = self.dataset.select_dtypes(include=["number"]).columns.tolist()
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
                self.dataset = self.dataset[(self.dataset[column] >= lower_limit) & (self.dataset[column] <= upper_limit)].reset_index(drop=True)
                after = len(self.dataset)
                print(f"Outliers removed: {before - after}")

            elif option == "6":
                numeric_columns = self.dataset.select_dtypes(include=["number"]).columns.tolist()
                if not numeric_columns:
                    print("No numeric columns available.")
                    continue
                for column in numeric_columns:
                    min_value = self.dataset[column].min()
                    max_value = self.dataset[column].max()
                    if max_value != min_value:
                        self.dataset[column] = (self.dataset[column] - min_value) / (max_value - min_value)
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
            print("[INFO] No numerical attributes present within the current matrix dataframe.")
            return
        summary = pd.DataFrame({
            "mean": numeric.mean(), "median": numeric.median(), "std_dev": numeric.std()
        })
        print("\nStatistical Matrix Distribution Parameters Summary Evaluation:")
        print(summary.to_string())
        input("\nPress Enter to continue...")

    def modeling_menu(self):
        while True:
            print("\nModeling")
            print("=" * 60)
            print("0. Import/Extract data from Jupyter Notebook (.ipynb)")
            print("1. K-Nearest Neighbors (KNN Imputation)")
            print("2. K-Means Clustering (Multivariable Adaptive)")
            print("3. Back to main menu")
            
            option = input("Choose an ML algorithm: ").strip()

            if option == "0":
                path = self.select_file("notebook")
                if path:
                    print(f"Analyzing structure of: {path}")
                    extracted_df = ModelManager.extract_dataframe_from_notebook(path)
                    if extracted_df is not None:
                        self.dataset = extracted_df
                        self.source_type = "extracted_ipynb"
                        print("Dataset loaded successfully in the models module.")
                else:
                    print("No file selected.")

            elif option == "1":
                if self.dataset is None:
                    print("Error: No data loaded. Use option 0 first or load a file in the main menu.")
                    continue

                print("Running KNN classification imputation...")

                # Ask user for target column
                target_column = input(
                    "Enter the column to impute (column containing missing values): "
                ).strip()

                if target_column not in self.dataset.columns:
                    print("Error: Invalid column name.")
                    continue

                # Ask user for k values
                try:
                    k_input = input(
                        "Enter k values separated by commas (e.g. 3,5,7,9): "
                    ).strip()

                    k_values = [int(k.strip()) for k in k_input.split(",")]

                except ValueError:
                    print("Error: k values must be integers.")
                    continue

                imputed_df, best_k, metrics = ModelManager.run_knn_imputation(
                    self.dataset,
                    target_column=target_column,
                    k_values=k_values
                )

                print(f"Best k: {best_k}")
                print("\nMetrics:")
                print(metrics)

                self.dataset = imputed_df
                print("KNN imputation completed.")

            elif option == "2":
                if self.dataset is None:
                    print("Error: No data loaded. Use option 0 first or load a file in the main menu.")
                    continue
                print("\nRunning clustering analysis (K-Means)...")
                
                # Obtenemos los datos calculados
                cluster_data = ModelManager.run_kmeans_clustering(self.dataset)
                
                if cluster_data is not None:
                    self.dataset = cluster_data["df_output"]
                    print("\nColumn 'Cluster_Asignado' has been added to your current dataset.")
                    
                    # -------------------------------------------------------------
                    # GRÁFICA 1: METRICAS DE EVALUACIÓN
                    # -------------------------------------------------------------
                    print("\n--- Process Metrics Chart (Inertia/Silhouette/Calinski/Davies) ---")
                    fig1, axes = plt.subplots(2, 2, figsize=(13, 9))
                    sns.set_theme(style='whitegrid')
                    
                    sns.lineplot(data=cluster_data["results_df"], x='k', y='inercia_intra_cluster', marker='o', ax=axes[0, 0], color='royalblue')
                    axes[0, 0].set_title('Within-Cluster Inertia (Lower is better)')
                    axes[0, 0].set_ylabel('Inertia')

                    sns.lineplot(data=cluster_data["results_df"], x='k', y='silhouette_intra_inter', marker='o', ax=axes[0, 1], color='darkorange')
                    axes[0, 1].set_title('Silhouette Coefficient (Higher is better)')
                    axes[0, 1].set_ylabel('Silhouette Score')

                    sns.lineplot(data=cluster_data["results_df"], x='k', y='calinski_harabasz_inter_intra', marker='o', ax=axes[1, 0], color='forestgreen')
                    axes[1, 0].set_title('Calinski-Harabasz Index (Higher is better)')
                    axes[1, 0].set_ylabel('Calinski-Harabasz Score')

                    sns.lineplot(data=cluster_data["results_df"], x='k', y='davies_bouldin_intra_inter', marker='o', ax=axes[1, 1], color='crimson')
                    axes[1, 1].set_title('Davies-Bouldin Index (Lower is better)')
                    axes[1, 1].set_ylabel('Davies-Bouldin Score')

                    for ax in axes.flat:
                        ax.set_xlabel('Number of Clusters (k)')
                    fig1.tight_layout()
                    
                    # Se muestra, se gestiona y se destruye antes de crear la siguiente
                    self.manage_chart_flow(fig1, "Clustering_Validation_Criteria_Metrics.png")
                    
                    # -------------------------------------------------------------
                    # GRÁFICA 2: DISTRIBUCIÓN ESPACIAL DE CLUSTERS
                    # -------------------------------------------------------------
                    print("\n--- Process Cluster Distribution Chart ---")
                    fig2, ax_clusters = plt.subplots(figsize=(9, 6))
                    scatter = ax_clusters.scatter(
                        cluster_data["X_2d"][:, 0], 
                        cluster_data["X_2d"][:, 1], 
                        c=cluster_data["best_labels"], 
                        cmap='tab20', s=20, alpha=0.8
                    )
                    fig2.colorbar(scatter, ax=ax_clusters, label='Assigned Cluster ID')
                    ax_clusters.set_title(f'Spatial Clustering Representation (K-means partitions with k={cluster_data["best_k"]})')
                    ax_clusters.set_xlabel('Principal Component 1')
                    ax_clusters.set_ylabel('Principal Component 2')
                    fig2.tight_layout()
                    
                    # Se muestra, se gestiona y se destruye antes de crear la siguiente
                    self.manage_chart_flow(fig2, "Clustering_Spatial_Projections.png")
                    
                    # -------------------------------------------------------------
                    # GRÁFICA 3: HEATMAP DE CENTROIDES
                    # -------------------------------------------------------------
                    print("\n--- Process Centroids Architectural Topology Chart ---")
                    fig3, ax_centroids = plt.subplots(figsize=(11, 6))
                    centroids_df = pd.DataFrame(cluster_data["cluster_centers"])
                    sns.heatmap(centroids_df, cmap='viridis', cbar=True, ax=ax_centroids)
                    ax_centroids.set_title(f'Cluster Centroid Structural Heatmap Topology (k={cluster_data["best_k"]})')
                    ax_centroids.set_xlabel('Dimensional Feature Index')
                    ax_centroids.set_ylabel('Cluster ID')
                    fig3.tight_layout()
                    
                    # Se muestra, se gestiona y se destruye antes de crear la siguiente
                    self.manage_chart_flow(fig3, "Clustering_Structural_Centroids_Heatmap.png")
                    
                    # -------------------------------------------------------------
                    # GRÁFICA 4: CASO EXCEPCIONAL MNIST
                    # -------------------------------------------------------------
                    X_raw = cluster_data["X_values"]
                    if X_raw is not None and X_raw.ndim == 2 and X_raw.shape[1] == 784:
                        print("\n[MNIST DETECTED] Preparing representative digits grid...")
                        unique_clusters = np.unique(cluster_data["best_labels"])
                        n_rows = len(unique_clusters)
                        n_examples = 10
                        
                        fig4, axes = plt.subplots(n_rows, n_examples, figsize=(1.4 * n_examples, 1.6 * n_rows))
                        if n_rows == 1: axes = np.array([axes])
                            
                        for r_idx, c_id in enumerate(unique_clusters):
                            pool = np.where(cluster_data["best_labels"] == c_id)[0]
                            if len(pool) == 0: continue
                            selected_drawings = np.random.choice(pool, size=min(n_examples, len(pool)), replace=False)
                            
                            for c_idx in range(n_examples):
                                ax = axes[r_idx, c_idx]
                                if c_idx < len(selected_drawings):
                                    ax.imshow(X_raw[selected_drawings[c_idx]].reshape(28, 28), cmap='gray_r')
                                    ax.axis('off')
                                else:
                                    ax.axis('off')
                            axes[r_idx, 0].set_ylabel(f'Cluster {c_id}', rotation=0, labelpad=30, fontsize=10, va='center')
                            
                        fig4.suptitle('Algorithmic Cluster Representative Exemplars Output Grid', y=1.02, fontsize=12)
                        fig4.tight_layout()
                        
                        print("\n--- Process MNIST Representative Exemplars Chart ---")
                        self.manage_chart_flow(fig4, "Cluster_Representative_Image_Exemplars.png")

            elif option == "3":
                break
            else:             
                print("Invalid option.")

    def manage_chart_flow(self, fig, filename):
        """
        Muestra la figura de forma síncrona y bloqueante. 
        Al cerrarla, pregunta si guardar y limpia la memoria.
        """
        if fig is None:
            print(f"[WARNING] No chart figure structure captured for {filename}.")
            return

        print(f"\n[INFO] Opening visualization window for: {filename}")
        print("--> IMPORTANT: Close the graphical chart window manually to return to terminal options.")
        
        # Muestra la figura actual de forma exclusiva y congela la ejecución
        plt.show() 

        # El código se reanuda aquí tras dar clic en la 'X' de la gráfica
        print(f"\n--- Chart Options: {filename} ---")
        print("1. Save chart to disk layout location")
        print("2. Close chart window and clear buffer memory")
        
        while True:
            opcion = input("Select operation (1-2): ").strip()
            if opcion == "1":
                fig.savefig(filename, bbox_inches='tight')
                print(f"[SUCCESS] Chart saved as '{filename}'.")
                break
            elif opcion == "2":
                print("Visualization context dismissed without updates.")
                break
            else:
                print("Invalid choice. Please choose 1 or 2.")
        
        # Destruye la figura actual de la memoria interna de Matplotlib
        plt.close(fig)

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

            numeric_columns = self.dataset.select_dtypes(include=["number"]).columns.tolist()
            all_columns = self.dataset.columns.tolist()

            if option == "1":
                print("\nNumeric columns:")
                print(numeric_columns)
                column = input("Choose a numeric column: ").strip()
                if column in numeric_columns:
                    fig = plt.figure(figsize=(8, 5))
                    plt.hist(self.dataset[column].dropna(), bins=10, edgecolor="black")
                    plt.title(f"Histogram of {column}")
                    plt.xlabel(column)
                    plt.ylabel("Frequency")
                    self.manage_chart_flow(fig, f"Histogram_{column}.png")
                else:
                    print("Invalid numeric column.")

            elif option == "2":
                print("\nColumns:")
                print(all_columns)
                column = input("Choose a column: ").strip()
                if column in all_columns:
                    fig = plt.figure(figsize=(8, 5))
                    self.dataset[column].value_counts().head(10).plot(kind="bar")
                    plt.title(f"Bar chart of {column}")
                    plt.xlabel(column)
                    plt.ylabel("Frequency")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    self.manage_chart_flow(fig, f"BarChart_{column}.png")
                else:
                    print("Invalid column.")

            elif option == "3":
                print("\nColumns:")
                print(all_columns)
                column = input("Choose a column: ").strip()
                if column in all_columns:
                    fig = plt.figure(figsize=(8, 8))
                    self.dataset[column].value_counts().head(10).plot(kind="pie", autopct="%1.1f%%")
                    plt.title(f"Pie chart of {column}")
                    plt.ylabel("")
                    self.manage_chart_flow(fig, f"PieChart_{column}.png")
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
                    self.manage_chart_flow(fig, f"Scatter_{x_column}_vs_{y_column}.png")
                else:
                    print("Both columns must be numeric.")

            elif option == "5":
                print("\nNumeric columns:")
                print(numeric_columns)
                column = input("Choose a numeric column: ").strip()
                if column in numeric_columns:
                    fig = plt.figure(figsize=(8, 5))
                    self.dataset[column].reset_index(drop=True).plot(kind="line")
                    plt.title(f"Line chart of {column}")
                    plt.xlabel("Index")
                    plt.ylabel(column)
                    self.manage_chart_flow(fig, f"LineChart_{column}.png")
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
                    self.manage_chart_flow(fig, f"Boxplot_{column}.png")
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
                self.manage_chart_flow(fig, "Global_Correlation_Heatmap.png")

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