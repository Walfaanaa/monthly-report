import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Monthly Member Report",
    layout="wide"
)

st.title("Monthly Member Report")

# -------------------------
# GitHub Data Source
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

    # Clean only essentials (no math changes)
    df.columns = df.columns.str.strip()

    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")

    # Remove invalid dates only
    df = df.dropna(subset=["business_date"])

    # Remove garbage rows only
    df = df[~df["id"].astype(str).str.contains("GRAND|\\*|***", na=False)]

    return df


df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()


# -------------------------
# Month Filter (view only)
# -------------------------
df["month"] = df["business_date"].dt.strftime("%Y-%m")

months = sorted(df["month"].dropna().unique(), reverse=True)

selected_month = st.sidebar.selectbox("Select Month", months)

report = df[df["month"] == selected_month]

if report.empty:
    st.warning("No data for selected month.")
    st.stop()


# -------------------------
# Display raw report (NO metrics)
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
# Download (raw filtered data only)
# -------------------------
csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Data (CSV)",
    data=csv,
    file_name=f"monthly_report_{selected_month}.csv",
    mime="text/csv"
)
