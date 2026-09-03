import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(
    page_title="EGSA Member Report",
    layout="wide"
)


# ================= LOGO =================

LOGO_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/EGSA.png"

st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" width="250" style="border-radius:10px;">
    </div>
    """,
    unsafe_allow_html=True
)


# ================= CSS =================

st.markdown("""
<style>

/* ================= MAIN APP ================= */

[data-testid="stAppViewContainer"] {
    background-color: white;
}


/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background-color: #6a0dad;
}


/* Default sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}


/* ================= BUSINESS DATE ================= */

/* Date input label */
section[data-testid="stSidebar"]
[data-testid="stDateInput"] label {
    color: white !important;
    font-weight: 600 !important;
}


/* Selected date text */
section[data-testid="stSidebar"]
[data-testid="stDateInput"] input {
    color: #0066CC !important;
    -webkit-text-fill-color: #0066CC !important;
    font-weight: 700 !important;
}


/* Date placeholder */
section[data-testid="stSidebar"]
[data-testid="stDateInput"] input::placeholder {
    color: #0066CC !important;
    -webkit-text-fill-color: #0066CC !important;
}


/* Date input container */
section[data-testid="stSidebar"]
[data-testid="stDateInput"] {
    color: #0066CC !important;
}


/* ================= MULTISELECT ================= */

.stMultiSelect div {
    color: black !important;
}


/* ================= HEADER ================= */

.header-box {
    background-color: #d32f2f;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}


/* ================= REPORT BOX ================= */

.report-box {
    background-color: #1976d2;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}


/* ================= SUMMARY BOX ================= */

.summary-box {
    background-color: #2e7d32;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}


/* ================= METRICS ================= */

div[data-testid="stMetric"] {
    background-color: #2e7d32;
    padding: 15px;
    border-radius: 10px;
}


div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color: white !important;
}


/* ================= DATAFRAME ================= */

[data-testid="stDataFrame"] * {
    color: black !important;
}


/* ================= HEADINGS ================= */

h1,
h2,
h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ================= HEADER =================

st.markdown(
    """
    <div class="header-box">
        <h1>EGSA 2026/27 Member Report Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)


# ================= DATA SOURCE =================

DATA_URL = (
    "https://raw.githubusercontent.com/Walfaanaa/"
    "monthly-report/main/EGSA2026_27_Monthly_report.xlsx"
)


@st.cache_data
def load_data():

    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(
        BytesIO(response.content),
        engine="openpyxl"
    )

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # Convert business date
    df["business_date"] = pd.to_datetime(
        df["business_date"],
        errors="coerce"
    )

    # Convert ID to string
    df["id"] = df["id"].astype(str)

    # Monthly payment
    df["EGSA2026_27_monthly_payment"] = pd.to_numeric(
        df["EGSA2026_27_monthly_payment"],
        errors="coerce"
    ).fillna(0)

    # End 2026 achievement
    df["End_2026_achievement"] = pd.to_numeric(
        df["End_2026_achievement"],
        errors="coerce"
    ).fillna(0)

    # 2027 half year plan
    df["EGSA2027_Half_Year_plan"] = pd.to_numeric(
        df["EGSA2027_Half_Year_plan"],
        errors="coerce"
    ).fillna(0)

    # 2027 half year achievement
    df["EGSA2027_Half_Year_achievement"] = pd.to_numeric(
        df["EGSA2027_Half_Year_achievement"],
        errors="coerce"
    ).fillna(0)

    return df


# Load data
df = load_data()


# ================= SIDEBAR =================

st.sidebar.header("Filters")


# Business Date Range
date_range = st.sidebar.date_input(
    "Business Date Range",
    value=[
        df["business_date"].min().date(),
        df["business_date"].max().date()
    ]
)


# Member ID
selected_ids = st.sidebar.multiselect(
    "Select Member ID",
    sorted(df["id"].unique())
)


# ================= FILTER =================

# IMPORTANT:
# Create filtered_df BEFORE using it anywhere else.

filtered_df = df.copy()


# ================= BUSINESS DATE FILTER =================

if len(date_range) == 2:

    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1])

    filtered_df = filtered_df[
        (
            filtered_df["business_date"].between(
                start,
                end
            )
        )
        |
        (
            filtered_df["business_date"].isna()
        )
    ]


# ================= MEMBER ID FILTER =================

if selected_ids:

    filtered_df = filtered_df[
        filtered_df["id"].isin(selected_ids)
    ]


# ================= MEMBER SUMMARY =================

member_summary = filtered_df.groupby(
    ["id", "Name"],
    as_index=False
).agg(

    EGSA2026_27_monthly_payment=(
        "EGSA2026_27_monthly_payment",
        "sum"
    ),

    End_2026_achievement=(
        "End_2026_achievement",
        "max"
    ),

    EGSA2027_Half_Year_plan=(
        "EGSA2027_Half_Year_plan",
        "sum"
    ),

    EGSA2027_Half_Year_achievement=(
        "EGSA2027_Half_Year_achievement",
        "sum"
    )
)


# ================= REPORT =================

st.markdown(
    """
    <div class="report-box">
        <h3>Member Payment Report</h3>
    </div>
    """,
    unsafe_allow_html=True
)


st.dataframe(
    member_summary[
        [
            "id",
            "Name",
            "EGSA2026_27_monthly_payment",
            "End_2026_achievement",
            "EGSA2027_Half_Year_plan",
            "EGSA2027_Half_Year_achievement"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ================= SUMMARY =================

st.markdown(
    """
    <div class="summary-box">
        <h3>Summary</h3>
    </div>
    """,
    unsafe_allow_html=True
)


# ================= SUMMARY CALCULATIONS =================

TOTAL_MEMBERS = df["id"].nunique()

MONTHLY_TARGET = 1000


# Total monthly payment
total_monthly_payment = (
    member_summary[
        "EGSA2026_27_monthly_payment"
    ].sum()
)


# End 2026 achievement
total_achievement = (
    member_summary[
        "End_2026_achievement"
    ].sum()
)


# Half year plan
total_half_plan = (
    member_summary[
        "EGSA2027_Half_Year_plan"
    ].sum()
    + 168000
)


# Half year achievement
total_half_achieved = (
    member_summary[
        "EGSA2027_Half_Year_achievement"
    ].sum()
    + total_monthly_payment
)


# Total collected
total_collected = (
    total_achievement
    + total_half_achieved
)


# Expected monthly amount
expected_amount = (
    TOTAL_MEMBERS
    *
    MONTHLY_TARGET
)


# Outstanding monthly amount
outstanding_amount = (
    expected_amount
    -
    total_monthly_payment
)


# ================= PAID MEMBERS =================

paid_members = member_summary[
    member_summary[
        "EGSA2026_27_monthly_payment"
    ] > 0
].shape[0]


# ================= UNPAID MEMBERS =================

unpaid_members = (
    TOTAL_MEMBERS
    -
    paid_members
)


# ================= METRICS =================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Monthly Payment Total",
        f"{total_monthly_payment:,.2f}"
    )


with col2:

    st.metric(
        "Expected Monthly",
        f"{expected_amount:,.2f}"
    )


with col3:

    st.metric(
        "Outstanding Monthly",
        f"{outstanding_amount:,.2f}"
    )


with col4:

    st.metric(
        "Paid Members",
        paid_members
    )


# ================= SECOND ROW =================

col5, col6, col7, col8 = st.columns(4)


with col5:

    st.metric(
        "End 2026 Achievement",
        f"{total_achievement:,.2f}"
    )


with col6:

    st.metric(
        "EGSA2027_Half_Year_plan",
        f"{total_half_plan:,.2f}"
    )


with col7:

    st.metric(
        "EGSA2027_Half_Year_achievement",
        f"{total_half_achieved:,.2f}"
    )


with col8:

    st.metric(
        "Unpaid Members",
        unpaid_members
    )


# ================= TOTAL COLLECTED =================

col9 = st.columns(1)[0]


with col9:

    st.metric(
        "Total Collected",
        f"{total_collected:,.2f}"
    )


# ================= UNPAID LIST =================

st.markdown(
    """
    <div class="report-box">
        <h3>Members Who Did Not Pay Monthly Contribution</h3>
    </div>
    """,
    unsafe_allow_html=True
)


unpaid_df = member_summary[
    member_summary[
        "EGSA2026_27_monthly_payment"
    ] == 0
]


st.dataframe(
    unpaid_df[
        [
            "id",
            "Name"
        ]
    ],
    use_container_width=True,
    hide_index=True
)
