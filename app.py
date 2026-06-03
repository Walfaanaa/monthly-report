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

    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")

    df = df.dropna(subset=["business_date", "id"])

    df["id"] = df["id"].astype(str)
    df = df[~df["id"].str.contains("GRAND", na=False)]
    df = df[~df["id"].str.contains(r"\*", regex=True, na=False)]

    return df


df = load_data()

# -------------------------
# Base filter (required rule)
# -------------------------
df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]


# -------------------------
# Filters (USER CONTROL)
# -------------------------
st.sidebar.header("Filters")

# ID filter
id_list = sorted(df["id"].unique())
selected_ids = st.sidebar.multiselect("Select ID (optional)", id_list)

# Date filter
min_date = df["business_date"].min()
max_date = df["business_date"].max()

date_range = st.sidebar.date_input(
    "Select Business Date Range",
    [min_date, max_date]
)


# -------------------------
# Apply filters
# -------------------------
filtered = df.copy()

if selected_ids:
    filtered = filtered[filtered["id"].isin(selected_ids)]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["business_date"] >= pd.Timestamp(start_date)) &
        (filtered["business_date"] <= pd.Timestamp(end_date))
    ]


# -------------------------
# Show data
# -------------------------
st.subheader("Filtered Data")

st.dataframe(
    filtered[
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
# GRAND TOTAL SECTION
# -------------------------
st.subheader("Grand Total Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Monthly Payment (Grand Total)",
        f"{filtered['monthly_payment'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Total Payment (Grand Total)",
        f"{filtered['total_payment'].sum():,.2f}"
    )


# -------------------------
# DOWNLOAD
# -------------------------
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="filtered_report.csv",
    mime="text/csv"
)
