import pandas as pd
import streamlit as st


@st.cache_data
def load_training_data(path: str) -> pd.DataFrame:
    """
    Load training data from CSV.
    Cached to avoid repeated disk reads on Streamlit reruns.
    """
    return pd.read_csv(path)
