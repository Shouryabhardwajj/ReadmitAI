import os
import streamlit as st

def get_secret(name: str, default: str | None = None) -> str | None:
    if hasattr(st, "secrets") and name in st.secrets:
        return st.secrets[name]
    return os.getenv(name, default)