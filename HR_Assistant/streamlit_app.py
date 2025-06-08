import streamlit as st
import json
import pandas as pd

st.title("User Tech Stack Details")

try:
    with open("user_tech_stack.json", "r") as f:
        data = json.load(f)
    items = data.get("items", [])
    if not items:
        st.warning("No tech stack details found in the JSON file.")
    else:
        df = pd.DataFrame(items)
        st.dataframe(df)
except FileNotFoundError:
    st.error("user_tech_stack.json file not found.")
except Exception as e:
    st.error(f"Error reading JSON: {e}")