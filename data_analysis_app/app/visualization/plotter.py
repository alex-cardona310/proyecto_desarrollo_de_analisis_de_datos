class Plotter:
    def __init__(self, plot=None, kind="", options=None):
        self.plot = plot
        self.Kind = kind
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