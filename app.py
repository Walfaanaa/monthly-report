import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(
    page_title="Member Report",
    layout="wide"
)

# =========================
# CUSTOM THEME
# =========================
st.markdown("""
<style>

/* Main page */
[data-testid="stAppViewContainer"] {
    background-color: #ffffff;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #6a0dad;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Header */
.header-box {
    background-color: #d32f2f;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}

/* Report Section */
.report-box {
    background-color: #1976d2;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}

/* Summary Section */
.summary-box {
    background-color: #2e7d32;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #2e7d32;
    padding: 15px;
    border-radius: 10px;
}

/* Metric text */
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color: white !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}

/* Table text black */
[data-testid="stDataFrame"] * {
    color: black !important;
}

/* Date input values black */
input {
    color: black !important;
}

/* Select box values black */
.stSelectbox div,
.stMultiSelect div {
    color: black !important;
}

/* Headings */
h1, h2, h3 {
    color: white;
}

/* Hide charts */
[data-testid="stPlotlyChart"],
[data-testid="stVegaLiteChart"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown("""
<div class="header-box">
    <h1>Member Report Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# =========================
# DATA SOURCE
# =========================
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"

MASTER_IDS = [str(i) for i in range(1001, 1027)]

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(
        BytesIO(response.content),
        engine="openpyxl"
    )

    df.columns = df.columns.str.strip()

    df["business_date"] = pd.to_datetime(
        df["business_date"],
        errors="coerce"
    )

    df["id"] = df["id"].astype(str)

    df = df[
        ~df["id"].str.contains(
            "GRAND",
            na=False
        )
    ]

    df = df[
        ~df["id"].str.contains(
            r"\*",
            regex=True,
            na=False
        )
    ]

    return df

df = load_data()

# =========================
# CAPITAL TABLE
# =========================
capital_df = df.groupby(
    "id",
    as_index=False
).agg({
    "total_payment": "max",
    "member_rank": "max"
})

# =========================
# MASTER TABLE
# =========================
master = pd.DataFrame({
    "id": MASTER_IDS
})

display = master.merge(
    capital_df,
    on="id",
    how="left"
)

# =========================
# FILTERS
# =========================
st.sidebar.header("Filters")

min_date = df["business_date"].min()
max_date = df["business_date"].max()

date_range = st.sidebar.date_input(
    "Business Date Range",
    [min_date, max_date]
)

selected_ids = st.sidebar.multiselect(
    "Select Member ID",
    MASTER_IDS
)

# =========================
# DATE FILTER
# =========================
period_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range

    period_df = period_df[
        (period_df["business_date"] >= pd.Timestamp(start_date))
        &
        (period_df["business_date"] <= pd.Timestamp(end_date))
    ]

period_df = period_df[
    [
        "id",
        "business_date",
        "monthly_payment"
    ]
]

# =========================
# MERGE
# =========================
display = display.merge(
    period_df,
    on="id",
    how="left"
)

display["monthly_payment"] = (
    display["monthly_payment"]
    .fillna(0)
)

# =========================
# MEMBER FILTER
# =========================
if selected_ids:
    display = display[
        display["id"].isin(selected_ids)
    ]

# =========================
# REPORT HEADER
# =========================
st.markdown("""
<div class="report-box">
    <h3>Member Report</h3>
</div>
""", unsafe_allow_html=True)

# =========================
# TABLE
# =========================
st.dataframe(
    display[
        [
            "business_date",
            "id",
            "monthly_payment",
            "total_payment",
            "member_rank"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# =========================
# SUMMARY HEADER
# =========================
st.markdown("""
<div class="summary-box">
    <h3>Summary</h3>
</div>
""", unsafe_allow_html=True)

# =========================
# TOTALS
# =========================
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Monthly Payment",
        f"{display['monthly_payment'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Grand Total Payment",
        f"{display['total_payment'].sum():,.2f}"
    )
