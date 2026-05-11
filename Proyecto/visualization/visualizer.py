import matplotlib.pyplot as plt
import seaborn as sns


class Visualizer:
    def __init__(self, plotters=None, style=None):
        self._plotters = plotters if plotters is not None else []
        self._style = style if style is not None else {}

    def visualize(self, df):
        if df is None or df.empty:
            print("No hay datos disponibles para graficar.")
            return

        while True:
            print("\nTipos de gráficas disponibles:")
            print("1. Histograma")
            print("2. Gráfica de barras")
            print("3. Gráfica de pastel")
            print("4. Gráfica de dispersión")
            print("5. Gráfica de línea")
            print("6. Mapa de correlaciones")
            print("7. Salir")

            option = input("Elige una opción: ")

            if option == "1":
                self.plot_histogram(df)

            elif option == "2":
                self.plot_bar(df)

            elif option == "3":
                self.plot_pie(df)

            elif option == "4":
                self.plot_scatter(df)

            elif option == "5":
                self.plot_line(df)

            elif option == "6":
                self.visualize_correlation_heatmap(df)

            elif option == "7":
                break

            else:
                print("Opción inválida.")

    def show_columns(self, df):
        print("\nColumnas disponibles:")
        for column in df.columns:
            print(f"- {column}")

    def plot_histogram(self, df):
        numeric_columns = df.select_dtypes(include=["number"]).columns

        if len(numeric_columns) == 0:
            print("No hay columnas numéricas para hacer un histograma.")
            return

        print("\nColumnas numéricas:")
        for column in numeric_columns:
            print(f"- {column}")

        column = input("Elige la columna numérica: ")

        if column not in numeric_columns:
            print("Columna inválida o no numérica.")
            return

        plt.figure(figsize=(8, 5))
        plt.hist(df[column].dropna(), bins=10, edgecolor="black")
        plt.title(f"Histograma de {column}")
        plt.xlabel(column)
        plt.ylabel("Frecuencia")
        plt.show()

    def plot_bar(self, df):
        self.show_columns(df)
        column = input("Elige la columna categórica: ")

        if column not in df.columns:
            print("Columna inválida.")
            return

        counts = df[column].value_counts().head(10)

        plt.figure(figsize=(8, 5))
        counts.plot(kind="bar")
        plt.title(f"Gráfica de barras de {column}")
        plt.xlabel(column)
        plt.ylabel("Frecuencia")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_pie(self, df):
        self.show_columns(df)
        column = input("Elige la columna categórica: ")

        if column not in df.columns:
            print("Columna inválida.")
            return

        counts = df[column].value_counts().head(10)

        plt.figure(figsize=(7, 7))
        counts.plot(kind="pie", autopct="%1.1f%%")
        plt.title(f"Gráfica de pastel de {column}")
        plt.ylabel("")
        plt.show()

    def plot_scatter(self, df):
        numeric_columns = df.select_dtypes(include=["number"]).columns

        if len(numeric_columns) < 2:
            print("Se necesitan al menos dos columnas numéricas.")
            return

        print("\nColumnas numéricas:")
        for column in numeric_columns:
            print(f"- {column}")

        x_column = input("Elige la columna para X: ")
        y_column = input("Elige la columna para Y: ")

        if x_column not in numeric_columns or y_column not in numeric_columns:
            print("Ambas columnas deben ser numéricas.")
            return

        plt.figure(figsize=(8, 5))
        plt.scatter(df[x_column], df[y_column])
        plt.title(f"Dispersión: {x_column} vs {y_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.show()

    def plot_line(self, df):
        numeric_columns = df.select_dtypes(include=["number"]).columns

        if len(numeric_columns) < 1:
            print("No hay columnas numéricas para graficar.")
            return

        print("\nColumnas numéricas:")
        for column in numeric_columns:
            print(f"- {column}")

        y_column = input("Elige la columna numérica a graficar: ")

        if y_column not in numeric_columns:
            print("Columna inválida o no numérica.")
            return

        plt.figure(figsize=(8, 5))
        plt.plot(df[y_column].reset_index(drop=True))
        plt.title(f"Gráfica de línea de {y_column}")
        plt.xlabel("Índice")
        plt.ylabel(y_column)
        plt.show()

    def visualize_correlation_heatmap(self, df, title="Mapa de Correlaciones"):
        if df is None or df.empty:
            print("No hay datos disponibles para graficar correlaciones.")
            return

        numeric_df = df.select_dtypes(include=["number"])

        if numeric_df.empty:
            print("No hay columnas numéricas para calcular correlaciones.")
            return

        plt.figure(figsize=(10, 8))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title(title)
        plt.show()