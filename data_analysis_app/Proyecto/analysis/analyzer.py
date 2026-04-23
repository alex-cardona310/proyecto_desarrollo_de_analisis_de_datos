import pandas as pd

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