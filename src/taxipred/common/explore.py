import pandas as pd


class DataExplorer:
    def __init__(self, df: pd.DataFrame, limit: int = 100):
        self._df_full = df
        self._df = df.head(limit)

    @property
    def df(self):
        return self._df

    def stats(self):
        self._df = self._df_full.describe().drop(["count"]).T.reset_index()
        return self

    def sample(self, sample_size: int = 10):
        self._df = self._df_full.sample(sample_size)
        return self
