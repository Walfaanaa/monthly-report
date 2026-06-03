import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# -------------------------
# Page setup
# -------------------------
st.set_page_config(
    page_title="Monthly Member Report",
    layout="wide"
)

st.title("Monthly Member Report")

# -------------------------
# Data source
# -------------------------
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"


# -------------------------
# Load data (NO CALCULATION)
# -------------------------
@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")

    # Clean columns
    df.columns = df.columns.str.strip()

    # Convert date
    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")

    # Remove invalid rows only
    df = df.dropna(subset=["business_date", "id"])

    # Remove garbage rows
    df["id"] = df["id"].astype(str)
    df = df[~df["id"].str.contains("GRAND", na=False)]
    df = df[~df["id"].str.contains(r"\*", regex=True, na=False)]

    return df


df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()


# -------------------------
# ONLY REQUIRED FILTER
# -------------------------
df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]


# -------------------------
# SHOW ALL DATA (NO MONTH FILTER)
# -------------------------
st.subheader("All Filtered Data (From 2026-05-25)")

st.dataframe(
    df[
        [
            "business_date",
            "id",
            "Name",
            "monthly_payment",
            "total_payment",
            "member_rank"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# -------------------------
# DOWNLOAD FULL FILTERED DATA
# -------------------------
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Full Data",
    data=csv,
    file_name="filtered_report_from_2026-05-25.csv",
    mime="text/csv"
)
