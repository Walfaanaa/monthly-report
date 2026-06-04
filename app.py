import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Member Report", layout="wide")

# =====================================
# CUSTOM STYLE
# =====================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: white; }

section[data-testid="stSidebar"] { background-color: #6a0dad; }
section[data-testid="stSidebar"] * { color: white !important; }

[data-testid="stDateInput"] input {
    color: black !important;
    -webkit-text-fill-color: black !important;
    font-weight: bold !important;
}

[data-testid="stDateInput"] { background-color: white !important; border-radius: 8px; }
[data-testid="stDateInput"] svg { color: black !important; }

.stMultiSelect div { color: black !important; }

.header-box {
    background-color: #d32f2f;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.report-box {
    background-color: #1976d2;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.summary-box {
    background-color: #2e7d32;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}

div[data-testid="stMetric"] {
    background-color: #2e7d32;
    padding: 15px;
    border-radius: 10px;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color: white !important;
}

[data-testid="stDataFrame"] { background-color: white; border-radius: 10px; }
[data-testid="stDataFrame"] * { color: black !important; }

h1, h2, h3 { color: white; }

</style>
""", unsafe_allow_html=True)

# =====================================
# TITLE
# =====================================
st.markdown("""
<div class="header-box">
    <h1>Member Report Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# =====================================
# DATA SOURCE
# =====================================
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"
MASTER_IDS = [str(i) for i in range(1001, 1027)]

# =====================================
# LOAD DATA
# =====================================
@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
    df.columns = df.columns.str.strip()

    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")
    df["id"] = df["id"].astype(str)

    df = df[~df["id"].str.contains("GRAND", na=False)]
    df = df[~df["id"].str.contains(r"\*", regex=True, na=False)]

    return df

df = load_data()

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.header("Filters")

min_date = df["business_date"].min()
max_date = df["business_date"].max()

date_range = st.sidebar.date_input(
    "Business Date Range",
    value=[min_date, max_date]
)

selected_ids = st.sidebar.multiselect(
    "Select Member ID",
    MASTER_IDS
)

# =====================================
# FILTER DATA FIRST (IMPORTANT FIX)
# =====================================
filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["business_date"] >= pd.Timestamp(start_date)) &
        (filtered_df["business_date"] <= pd.Timestamp(end_date))
    ]

# =====================================
# AGGREGATE PER MEMBER (FIXED LOGIC)
# =====================================
member_period = filtered_df.groupby("id", as_index=False).agg(
    monthly_payment=("monthly_payment", "sum"),
    last_business_date=("business_date", "max")
)

capital_df = df.groupby("id", as_index=False).agg(
    total_payment=("total_payment", "max"),
    member_rank=("member_rank", "max")
)

master = pd.DataFrame({"id": MASTER_IDS})

display = master.merge(capital_df, on="id", how="left")
display = display.merge(member_period, on="id", how="left")

display[["monthly_payment", "total_payment"]] = display[
    ["monthly_payment", "total_payment"]
].fillna(0)

# =====================================
# FILTER MEMBERS
# =====================================
if selected_ids:
    display = display[display["id"].isin(selected_ids)]

# =====================================
# REPORT
# =====================================
st.markdown("""
<div class="report-box">
    <h3>Member Report</h3>
</div>
""", unsafe_allow_html=True)

st.dataframe(
    display[
        ["id", "monthly_payment", "total_payment", "member_rank", "last_business_date"]
    ],
    use_container_width=True,
    hide_index=True
)

# =====================================
# SUMMARY
# =====================================
st.markdown("""
<div class="summary-box">
    <h3>Summary</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Monthly Payment", f"{display['monthly_payment'].sum():,.2f}")

with col2:
    st.metric("Total Payment", f"{display['total_payment'].sum():,.2f}")

with col3:
    st.metric("Members", len(display))
