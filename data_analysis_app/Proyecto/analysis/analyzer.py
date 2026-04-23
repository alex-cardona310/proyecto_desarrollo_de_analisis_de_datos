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
            raise ValueError("No DataFrame was provided to Analyzer.")

        numeric_df = self.df.select_dtypes(include=["number"])

        summary = pd.DataFrame({
            "mean": numeric_df.mean(),
            "median": numeric_df.median(),
            "std_dev": numeric_df.std(),
            "q1": numeric_df.quantile(0.25),
            "q2": numeric_df.quantile(0.50),
            "q3": numeric_df.quantile(0.75)
        })

        return summary.round(2)

    def CorrelationMatrix(self):
        if self.df is None:
            raise ValueError("No DataFrame was provided to Analyzer.")

        numeric_df = self.df.select_dtypes(include=["number"])
        return numeric_df.corr().round(2)