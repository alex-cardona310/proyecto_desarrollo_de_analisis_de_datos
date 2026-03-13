class Visualizer:
    def __init__(self, plotters=None, style=None):
        self._plotters = plotters if plotters is not None else []
        self._style = style if style is not None else {}

    def visualize(self):
        pass