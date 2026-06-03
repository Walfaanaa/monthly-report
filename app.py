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

DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"


# -------------------------
# Load data
# -------------------------
@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")

    df.columns = df.columns.str.strip()

    # DO NOT DROP NULL DATES
    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")

    df["id"] = df["id"].astype(str)

    # Remove only garbage rows
    df = df[~df["id"].str.contains("GRAND", na=False)]
    df = df[~df["id"].str.contains(r"\*", regex=True, na=False)]

    return df


df = load_data()

# -------------------------
# Base filter
# -------------------------
df = df[df["business_date"].isna() | (df["business_date"] >= pd.Timestamp("2026-05-25"))]


# -------------------------
# Create report month (IMPORTANT PART)
# -------------------------
df["report_month"] = df["business_date"].dt.strftime("%Y-%m")

df["report_month"] = df["report_month"].fillna("NO PAYMENT")


# -------------------------
# Filters
# -------------------------
st.sidebar.header("Filters")

selected_ids = st.sidebar.multiselect(
    "Select ID",
    sorted(df["id"].unique())
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    sorted(df["report_month"].unique())
)


filtered = df.copy()

if selected_ids:
    filtered = filtered[filtered["id"].isin(selected_ids)]

filtered = filtered[filtered["report_month"] == selected_month]


# -------------------------
# Display
# -------------------------
st.subheader("Member Data (Including Missing Payments)")

st.dataframe(
    filtered[
        [
            "business_date",
            "report_month",
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
# GRAND TOTAL
# -------------------------
st.subheader("Grand Total")

col1, col2 = st.columns(2)

col1.metric(
    "Total Monthly Payment",
    f"{filtered['monthly_payment'].sum():,.2f}"
)

col2.metric(
    "Total Payment",
    f"{filtered['total_payment'].sum():,.2f}"
)


# -------------------------
# DOWNLOAD
# -------------------------
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Report",
    csv,
    "report.csv",
    "text/csv"
)
