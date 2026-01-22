import pandas as pd


class DataExplorer:
    """Lightweight helper for common DataFrame exploration operations."""

    def __init__(self, df: pd.DataFrame, limit: int = 100):
        """
        Initialize explorer with a full DataFrame and an initial preview slice.

        Args:
            df: Full dataset.
            limit: Number of rows to keep in the current view.
        """
        self._df_full = df
        self._df = df.head(limit)

    @property
    def df(self) -> pd.DataFrame:
        """Return the current view DataFrame."""
        return self._df

    def stats(self) -> "DataExplorer":
        """Replace current view with descriptive statistics for numeric columns."""
        self._df = self._df_full.describe().drop(["count"]).T.reset_index()
        return self

    def sample(self, sample_size: int = 10) -> "DataExplorer":
        """Replace current view with a random sample of rows."""
        self._df = self._df_full.sample(sample_size)
        return self
