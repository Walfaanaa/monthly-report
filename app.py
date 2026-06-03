import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Monthly Member Report", layout="wide")

st.title("Monthly Member Report")

DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"


@st.cache_data
def load_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()

        df = pd.read_excel(BytesIO(response.content), engine="openpyxl")

        # Validate required columns
        required_cols = [
            "business_date", "id", "Name",
            "monthly_payment", "total_payment", "member_rank"
        ]

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")

        df = df.dropna(subset=["business_date"])

        return df

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()


df = load_data()

# Create month column ONCE
df["month"] = df["business_date"].dt.strftime("%Y-%m")

months = sorted(df["month"].dropna().unique(), reverse=True)

selected_month = st.sidebar.selectbox("Select Month", months)

report = df[df["month"] == selected_month]

if report.empty:
    st.warning("No data available for selected month.")
    st.stop()

# Summary
st.subheader(f"Summary Report: {selected_month}")

c1, c2, c3 = st.columns(3)

c1.metric("Total Members", report["id"].nunique())
c2.metric("Monthly Payment", f"{report['monthly_payment'].sum():,.2f}")
c3.metric("Total Payment", f"{report['total_payment'].sum():,.2f}")

# Detail table
st.subheader("Member Details")

st.dataframe(
    report.sort_values("member_rank", na_position="last")[
        ["business_date", "id", "Name", "monthly_payment", "total_payment", "member_rank"]
    ],
    use_container_width=True,
    hide_index=True
)

# Top 10
st.subheader("Top 10 Members by Total Payment")

top_members = (
    report.groupby("Name")["total_payment"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_members)

# Download
csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Report",
    data=csv,
    file_name=f"monthly_report_{selected_month}.csv",
    mime="text/csv"
)
