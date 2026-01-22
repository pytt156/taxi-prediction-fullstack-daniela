import pandas as pd
import streamlit as st


@st.cache_data
def load_training_data(path: str) -> pd.DataFrame:
    """Load a CSV dataset from disk (cached across Streamlit reruns)."""
    return pd.read_csv(path)
