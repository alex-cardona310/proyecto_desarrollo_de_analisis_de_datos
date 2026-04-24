import matplotlib.pyplot as plt
import seaborn as sns
class Visualizer:
    def __init__(self, plotters=None, style=None):
        self._plotters = plotters if plotters is not None else []
        self._style = style if style is not None else {}

    def visualize(self):
        pass
# NUEVO MÉTODO
    def visualize_correlation_heatmap(self, df, title="Mapa de Correlaciones"):
        if df is None or df.empty:
            print("No hay datos disponibles para graficar correlaciones.")
            return
        plt.figure(figsize=(10, 8))
        corr = df.corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title(title)
        plt.show()