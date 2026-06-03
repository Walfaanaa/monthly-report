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
# FILTER PERIOD DATA
# -------------------------
filtered_df = df[df["business_date"] >= pd.Timestamp("2026-05-25")]

# -------------------------
# MASTER TABLE (ALL IDs)
# -------------------------
master = pd.DataFrame({"id": MASTER_IDS})

# attach filtered data (for display)
display_df = master.merge(filtered_df, on="id", how="left")

# attach FULL data (for ranking)
rank_df = df.groupby("id", as_index=False)["total_payment"].sum()

display_df = display_df.merge(rank_df, on="id", how="left", suffixes=("", "_full"))

# -------------------------
# CLEAN MISSING VALUES
# -------------------------
display_df["Name"] = display_df["Name"].fillna("NO PAYMENT")
display_df["monthly_payment"] = display_df["monthly_payment"].fillna(0)
display_df["total_payment"] = display_df["total_payment"].fillna(0)
display_df["total_payment_full"] = display_df["total_payment_full"].fillna(0)

# -------------------------
# CREATE RANK (BASED ON FULL PAYMENT)
# -------------------------
display_df["rank"] = display_df["total_payment_full"].rank(
    ascending=False,
    method="min"
).astype(int)

# -------------------------
# FILTER UI
# -------------------------
st.sidebar.header("Filters")

selected_ids = st.sidebar.multiselect("Select ID", MASTER_IDS)

filtered = display_df.copy()

if selected_ids:
    filtered = filtered[filtered["id"].isin(selected_ids)]

# -------------------------
# DISPLAY
# -------------------------
st.subheader("Member Report (Full Ranking Included)")

st.dataframe(
    filtered[
        [
            "business_date",
            "id",
            "Name",
            "monthly_payment",
            "total_payment",
            "total_payment_full",
            "rank"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# -------------------------
# GRAND TOTAL (FILTERED PERIOD ONLY)
# -------------------------
st.subheader("Grand Total (Filtered Period Only)")

col1, col2 = st.columns(2)

col1.metric(
    "Monthly Payment",
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
