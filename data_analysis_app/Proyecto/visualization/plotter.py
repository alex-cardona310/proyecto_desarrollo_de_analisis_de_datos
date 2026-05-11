import matplotlib.pyplot as plt
import seaborn as sns


class Plotter:
    def __init__(self, df=None, kind="", options=None):
        self.df = df
        self.kind = kind
        self.options = options if options is not None else {}

    def set_data(self, df):
        self.df = df

    def _check_data(self):
        if self.df is None or self.df.empty:
            print("No hay datos disponibles para graficar.")
            return False
        return True

    def _configure_plot(self, title, xlabel="", ylabel=""):
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()

    def plot_line(self, x_column, y_column):
        if not self._check_data():
            return

        plt.figure(figsize=(10, 6))
        sns.lineplot(data=self.df, x=x_column, y=y_column)
        self._configure_plot(
            title=f"Tendencia: {y_column} respecto a {x_column}",
            xlabel=x_column,
            ylabel=y_column
        )
        self.show()

    def plot_scatter(self, x_column, y_column):
        if not self._check_data():
            return

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=self.df, x=x_column, y=y_column)
        self._configure_plot(
            title=f"Dispersión: {x_column} vs {y_column}",
            xlabel=x_column,
            ylabel=y_column
        )
        self.show()

    def plot_bar(self, column):
        if not self._check_data():
            return

        counts = self.df[column].value_counts().head(10)

        plt.figure(figsize=(10, 6))
        sns.barplot(x=counts.index, y=counts.values)
        self._configure_plot(
            title=f"Gráfica de barras: {column}",
            xlabel=column,
            ylabel="Frecuencia"
        )
        plt.xticks(rotation=45)
        self.show()

    def plot_histogram(self, column):
        if not self._check_data():
            return

        plt.figure(figsize=(10, 6))
        sns.histplot(self.df[column].dropna(), kde=True)
        self._configure_plot(
            title=f"Distribución de {column}",
            xlabel=column,
            ylabel="Frecuencia"
        )
        self.show()

    def plot_box(self, column):
        if not self._check_data():
            return

        plt.figure(figsize=(8, 6))
        sns.boxplot(y=self.df[column])
        self._configure_plot(
            title=f"Boxplot de {column}",
            ylabel=column
        )
        self.show()

    def plot_pie(self, column):
        if not self._check_data():
            return

        counts = self.df[column].value_counts().head(10)

        plt.figure(figsize=(8, 8))
        counts.plot(kind="pie", autopct="%1.1f%%")
        plt.title(f"Gráfica de pastel: {column}")
        plt.ylabel("")
        self.show()

    def plot_correlation_matrix(self):
        if not self._check_data():
            return

        numeric_df = self.df.select_dtypes(include=["number"])

        if numeric_df.empty:
            print("No hay columnas numéricas para calcular correlaciones.")
            return

        plt.figure(figsize=(10, 8))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Mapa de correlaciones")
        self.show()

    def save_plot(self, path):
        plt.savefig(path)
        print(f"Gráfica guardada en: {path}")

    def show(self):
        plt.show() 