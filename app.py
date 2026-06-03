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
# MASTER ID LIST (IMPORTANT)
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
# FILTER DATA BY DATE
# -------------------------
df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]


# -------------------------
# BUILD MASTER TABLE (LEFT JOIN LOGIC)
# -------------------------
master_df = pd.DataFrame({"id": MASTER_IDS})

merged = master_df.merge(df, on="id", how="left")


# -------------------------
# HANDLE MISSING DATA
# -------------------------
merged["business_date"] = merged["business_date"].fillna(pd.NaT)
merged["report_month"] = merged["business_date"].dt.strftime("%Y-%m")
merged["report_month"] = merged["report_month"].fillna("NO PAYMENT")

merged["Name"] = merged["Name"].fillna("NO PAYMENT")
merged["monthly_payment"] = merged["monthly_payment"].fillna(0)
merged["total_payment"] = merged["total_payment"].fillna(0)
merged["member_rank"] = merged["member_rank"].fillna("-")


# -------------------------
# Filters
# -------------------------
st.sidebar.header("Filters")

selected_ids = st.sidebar.multiselect(
    "Select ID",
    MASTER_IDS
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    sorted(merged["report_month"].unique())
)

filtered = merged.copy()

if selected_ids:
    filtered = filtered[filtered["id"].isin(selected_ids)]

filtered = filtered[filtered["report_month"] == selected_month]


# -------------------------
# DISPLAY
# -------------------------
st.subheader("All Members (Guaranteed Full ID Coverage)")

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
st.subheader("Grand Total Summary")

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
    "full_member_report.csv",
    "text/csv"
)
