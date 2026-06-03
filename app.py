import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Member Report", layout="wide")

# -------------------------
# UI THEME (UPDATED)
# -------------------------
st.markdown("""
<style>

/* Full page background: top green → blue → bottom indigo */
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(to bottom,
        #0f9d58 0%,      /* green (top) */
        #4285f4 50%,     /* blue (middle) */
        #3f51b5 100%     /* indigo (bottom) */
    );
}

/* Sidebar (filter area → violet) */
section[data-testid="stSidebar"] {
    background-color: #6a0dad;
}

/* Sidebar text color */
section[data-testid="stSidebar"] * {
    color: white;
}

/* Metric cards styling */
div[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.10);
    padding: 10px;
    border-radius: 10px;
}

/* Optional: make title more visible */
h1, h2, h3 {
    color: white;
}

/* Table background improvement */
div[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.05);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

st.title("Member Report")

DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"

MASTER_IDS = [str(i) for i in range(1001, 1027)]

# -------------------------
# LOAD DATA
# -------------------------
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

# -------------------------
# CAPITAL (UNCHANGED LOGIC)
# -------------------------
capital_df = df.groupby("id", as_index=False).agg({
    "total_payment": "max",
    "member_rank": "max"
})

# -------------------------
# MASTER TABLE
# -------------------------
master = pd.DataFrame({"id": MASTER_IDS})
display = master.merge(capital_df, on="id", how="left")

# -------------------------
# SIDEBAR FILTER
# -------------------------
st.sidebar.header("Filters")

min_date = df["business_date"].min()
max_date = df["business_date"].max()

date_range = st.sidebar.date_input(
    "Business Date Range",
    [min_date, max_date]
)

selected_ids = st.sidebar.multiselect("Select ID", MASTER_IDS)

# -------------------------
# APPLY DATE FILTER
# -------------------------
period_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range

    period_df = period_df[
        (period_df["business_date"] >= pd.Timestamp(start_date)) &
        (period_df["business_date"] <= pd.Timestamp(end_date))
    ]

period_df = period_df[["id", "business_date", "monthly_payment"]]

# -------------------------
# MERGE PERIOD DATA
# -------------------------
display = display.merge(period_df, on="id", how="left")
display["monthly_payment"] = display["monthly_payment"].fillna(0)

# -------------------------
# FILTER IDS
# -------------------------
if selected_ids:
    display = display[display["id"].isin(selected_ids)]

# -------------------------
# DISPLAY
# -------------------------
st.subheader("Member Report")

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

# -------------------------
# GRAND TOTAL
# -------------------------
st.subheader("Grand Total")

col1, col2 = st.columns(2)

col1.metric(
    "Monthly Payment (Filtered Period)",
    f"{display['monthly_payment'].sum():,.2f}"
)

col2.metric(
    "Total Payment (Grand still paid)",
    f"{display['total_payment'].sum():,.2f}"
)
