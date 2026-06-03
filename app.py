import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(
    page_title="Monthly Member Report",
    layout="wide"
)

st.title("Monthly Member Report")

# -------------------------
# GitHub Excel Source
# -------------------------
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"


# -------------------------
# Load Data (NO CALCULATION)
# -------------------------
@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert date safely
    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")

    # Remove invalid rows only
    df = df.dropna(subset=["business_date", "id"])

    # Remove summary / garbage rows
    df["id"] = df["id"].astype(str)
    df = df[~df["id"].str.contains("GRAND", na=False)]
    df = df[~df["id"].str.contains(r"\*", regex=True, na=False)]

    return df


df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()


# -------------------------
# REQUIRED FILTER RULE
# -------------------------
df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]


if df.empty:
    st.warning("No records found after 2026-05-25.")
    st.stop()


# -------------------------
# Month Filter (view only)
# -------------------------
df["month"] = df["business_date"].dt.strftime("%Y-%m")

months = sorted(df["month"].unique(), reverse=True)

selected_month = st.sidebar.selectbox("Select Month", months)

report = df[df["month"] == selected_month]

if report.empty:
    st.warning("No data for selected month.")
    st.stop()


# -------------------------
# RAW DATA DISPLAY ONLY
# -------------------------
st.subheader(f"Raw Data View: {selected_month}")

st.dataframe(
    report[
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
# DOWNLOAD RAW DATA
# -------------------------
csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"monthly_report_{selected_month}.csv",
    mime="text/csv"
)
