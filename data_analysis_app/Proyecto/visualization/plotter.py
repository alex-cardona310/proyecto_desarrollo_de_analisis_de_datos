import matplotlib.pyplot as plt
import seaborn as sns

class Plotter:
    def __init__(self, plot=None, kind="", options=None):
        self.plot = plot
        self.kind = kind
        self.options = options if options is not None else {}

    def plot_line(self):
        pass

    def plot_scatter(self):
        pass

    def plot_bar(self):
        pass

    def plot_histogram(self):
        pass

    def plot_box(self):
        pass

    def save_plot(self):
        pass

    def show(self):
        pass

    def _configure_plot(self):
        pass

    # --- NUEVOS MÉTODOS ---
    def plot_trends(self, df, x, y, title="Tendencia"):
        """
        Crear un gráfico de línea para observar tendencias.
        df: DataFrame limpio y ordenado (self.dataset en DataApp)
        x: columna en el eje X
        y: columna en el eje Y
        """
        if df is None or df.empty:
            print("No hay datos disponibles para graficar tendencias.")
            return
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x=x, y=y)
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.show()

    def plot_distribution(self, df, column, title="Distribución"):
        """
        Crear un histograma para observar la distribución de una variable.
        df: DataFrame limpio y ordenado (self.dataset en DataApp)
        column: columna a graficar
        """
        if df is None or df.empty:
            print("No hay datos disponibles para graficar distribuciones.")
            return
        plt.figure(figsize=(8, 6))
        sns.histplot(df[column], kde=True)
        plt.title(title)
        plt.xlabel(column)
        plt.ylabel("Frecuencia")
        plt.show()
