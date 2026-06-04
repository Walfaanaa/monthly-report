import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Member Report", layout="wide")

# =====================================
# STYLE
# =====================================
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: white;
}

section[data-testid="stSidebar"] {
    background-color: #6a0dad;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stDateInput"] input {
    color: black !important;
    -webkit-text-fill-color: black !important;
    font-weight: bold !important;
}

[data-testid="stDateInput"] {
    background-color: white !important;
    border-radius: 8px;
}

[data-testid="stDateInput"] svg {
    color: black !important;
}

.stMultiSelect div {
    color: black !important;
}

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

[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}

[data-testid="stDataFrame"] * {
    color: black !important;
}

h1, h2, h3 {
    color: white;
}

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
MONTHLY_CONTRIBUTION = 1000

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
# FILTER DATA
# =====================================
filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["business_date"] >= pd.Timestamp(start_date)) &
        (filtered_df["business_date"] <= pd.Timestamp(end_date))
    ]

# =====================================
# MEMBER PAYMENT IN PERIOD
# =====================================
member_period = filtered_df.groupby("id", as_index=False).agg(
    monthly_payment=("monthly_payment", "sum")
)

capital_df = df.groupby("id", as_index=False).agg(
    total_payment=("total_payment", "max"),
    member_rank=("member_rank", "max")
)

# =====================================
# MASTER TABLE
# =====================================
master = pd.DataFrame({"id": MASTER_IDS})

display = master.merge(capital_df, on="id", how="left")
display = display.merge(member_period, on="id", how="left")

display["monthly_payment"] = display["monthly_payment"].fillna(0)
display["total_payment"] = display["total_payment"].fillna(0)

# =====================================
# PAYMENT LOGIC (FIXED AS YOU REQUESTED)
# =====================================
paid_mask = display["monthly_payment"] > 0

paid_members = display.loc[paid_mask, "id"]
non_paid_members = display.loc[~paid_mask, "id"]

paid_count = len(paid_members)
unpaid_count = len(non_paid_members)

total_members = len(MASTER_IDS)

# Expected = flat per member (NO months)
expected_amount = total_members * MONTHLY_CONTRIBUTION
collected_amount = display["monthly_payment"].sum()

# 🔥 KEY FIX: ONLY non-paying members × 1000
unpaid_amount_total = len(non_paid_members) * MONTHLY_CONTRIBUTION

# =====================================
# FILTER SELECTION
# =====================================
if selected_ids:
    display = display[display["id"].isin(selected_ids)]

# =====================================
# REPORT TABLE
# =====================================
st.markdown("""
<div class="report-box">
    <h3>Member Report</h3>
</div>
""", unsafe_allow_html=True)

st.dataframe(
    display[
        ["id", "monthly_payment", "total_payment", "member_rank"]
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
    st.metric("Collected Amount", f"{collected_amount:,.2f}")

with col2:
    st.metric("Expected Amount", f"{expected_amount:,.2f}")

with col3:
    st.metric("Unpaid Amount", f"{unpaid_amount_total:,.2f}")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Total Members", total_members)

with col5:
    st.metric("Paid Members", paid_count)

with col6:
    st.metric("Unpaid Members", unpaid_count)

# =====================================
# UNPAID LIST
# =====================================
st.markdown("""
<div class="report-box">
    <h3>Members Who Did Not Pay</h3>
</div>
""", unsafe_allow_html=True)

unpaid_df = pd.DataFrame({
    "Member ID": sorted(non_paid_members)
})

st.dataframe(unpaid_df, use_container_width=True, hide_index=True)
