import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Member Report", layout="wide")
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
# FULL CAPITAL (IMPORTANT FIX)
# -------------------------
capital_df = df.groupby("id", as_index=False).agg({
    "total_payment": "max",   # lifetime value
    "member_rank": "max"
})

# -------------------------
# PERIOD DATA ONLY
# -------------------------
period_df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]

period_df = period_df[[
    "id",
    "business_date",
    "monthly_payment"
]]

# -------------------------
# MASTER TABLE
# -------------------------
master = pd.DataFrame({"id": MASTER_IDS})

# merge capital FIRST (fixes KeyError)
display = master.merge(capital_df, on="id", how="left")

# merge period data SECOND
display = display.merge(period_df, on="id", how="left")

# -------------------------
# CLEAN DISPLAY ONLY
# -------------------------
display["Name"] = display.get("Name", "NO PAYMENT")
display["monthly_payment"] = display["monthly_payment"].fillna(0)

display["total_payment"] = display["total_payment"].fillna(0)
display["member_rank"] = display["member_rank"].fillna("-")

# -------------------------
# FILTER UI
# -------------------------
st.sidebar.header("Filters")

selected_ids = st.sidebar.multiselect("Select ID", MASTER_IDS)

filtered = display.copy()

if selected_ids:
    filtered = filtered[filtered["id"].isin(selected_ids)]

# -------------------------
# DISPLAY
# -------------------------
st.subheader("Member Report")

st.dataframe(
    filtered[
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
    "Monthly Payment (Period)",
    f"{filtered['monthly_payment'].sum():,.2f}"
)

col2.metric(
    "Total Payment (Capital)",
    f"{filtered['total_payment'].sum():,.2f}"
)
