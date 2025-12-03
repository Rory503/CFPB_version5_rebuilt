import streamlit as st, pandas as pd

st.set_page_config(page_title="CFPB Explorer", layout="wide")
st.title("CFPB Explorer")

st.write("Upload a CFPB CSV or use the sample bundled in the repo.")

sample = st.checkbox("Load bundled sample.csv if no upload")
up = st.file_uploader("Upload CFPB CSV", type=["csv"])

def load_df():
    if up: return pd.read_csv(up)
    if sample:
        return pd.read_csv("sample.csv")  # put a small sample.csv in repo root
    return None

df = load_df()
if df is not None:
    st.dataframe(df.head(50))
    if "Company" in df.columns:
        st.subheader("Top companies")
        st.bar_chart(df["Company"].value_counts().head(10))
else:
    st.info("Upload a CSV or tick the sample.")
