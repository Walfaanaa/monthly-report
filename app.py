import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# -------------------------
# Page setup
# -------------------------
st.set_page_config(
    page_title="Member Report",
    layout="wide"
)

st.title("Member Report")

DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"

# -------------------------
# MASTER IDS
# -------------------------
MASTER_IDS = [str(i) for i in range(1001, 1027)]

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
    df["id"] = df["id"].astype(str)

    # remove garbage rows only
    df = df[~df["id"].str.contains("GRAND", na=False)]
    df = df[~df["id"].str.contains(r"\*", regex=True, na=False)]

    return df


df = load_data()

# -------------------------
# APPLY DATE FILTER
# -------------------------
df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]

# -------------------------
# MASTER JOIN (ENSURE ALL IDS EXIST)
# -------------------------
master_df = pd.DataFrame({"id": MASTER_IDS})

full_df = master_df.merge(df, on="id", how="left")

# -------------------------
# CLEAN MISSING VALUES
# -------------------------
full_df["business_date"] = full_df["business_date"]
full_df["Name"] = full_df["Name"].fillna("NO PAYMENT")

full_df["monthly_payment"] = full_df["monthly_payment"].fillna(0)
full_df["total_payment"] = full_df["total_payment"].fillna(0)
full_df["member_rank"] = full_df["member_rank"].fillna("-")

# -------------------------
# OPTIONAL FILTERS
# -------------------------
st.sidebar.header("Filters")

selected_ids = st.sidebar.multiselect("Select ID", MASTER_IDS)

filtered = full_df.copy()

if selected_ids:
    filtered = filtered[filtered["id"].isin(selected_ids)]

# -------------------------
# DISPLAY
# -------------------------
st.subheader("Full Member Report")

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
    "member_report.csv",
    "text/csv"
)
