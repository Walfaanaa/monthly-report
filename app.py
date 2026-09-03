import streamlit as st
import pandas as pd
import requests
from io import BytesIO


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EGSA Member Report",
    layout="wide"
)


# ============================================================
# LOGO
# ============================================================

LOGO_URL = (
    "https://raw.githubusercontent.com/Walfaanaa/"
    "monthly-report/main/EGSA.png"
)

st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" width="250" style="border-radius:10px;">
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   MAIN APP
   ============================================================ */

[data-testid="stAppViewContainer"] {
    background-color: white;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background-color: #6a0dad;
}


/* Default sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}


/* ============================================================
   BUSINESS DATE
   ============================================================ */

/* Business Date label */
section[data-testid="stSidebar"]
[data-testid="stDateInput"] label {
    color: white !important;
    font-weight: 600 !important;
}


/* Selected Business Date */
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


/* Date input */
section[data-testid="stSidebar"]
[data-testid="stDateInput"] {
    color: #0066CC !important;
}


/* ============================================================
   MULTISELECT
   ============================================================ */

.stMultiSelect div {
    color: black !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.header-box {
    background-color: #d32f2f;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}


/* ============================================================
   REPORT BOX
   ============================================================ */

.report-box {
    background-color: #1976d2;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}


/* ============================================================
   SUMMARY BOX
   ============================================================ */

.summary-box {
    background-color: #2e7d32;
    padding: 10px;
    border-radius: 10px;
    margin-top: 15px;
}


/* ============================================================
   METRICS
   ============================================================ */

div[data-testid="stMetric"] {
    background-color: #2e7d32;
    padding: 15px;
    border-radius: 10px;
}


div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color: white !important;
}


/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] * {
    color: black !important;
}


/* ============================================================
   HEADINGS
   ============================================================ */

h1,
h2,
h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="header-box">
        <h1>EGSA 2026/27 Member Report Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA SOURCE
# ============================================================

DATA_URL = (
    "https://raw.githubusercontent.com/Walfaanaa/"
    "monthly-report/main/EGSA2026_27_Monthly_report.xlsx"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(
        BytesIO(response.content),
        engine="openpyxl"
    )

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = df.columns.str.strip()


    # --------------------------------------------------------
    # Business Date
    # --------------------------------------------------------

    df["business_date"] = pd.to_datetime(
        df["business_date"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # Member ID
    # --------------------------------------------------------

    df["id"] = (
        df["id"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Monthly Payment
    # --------------------------------------------------------

    df["EGSA2026_27_monthly_payment"] = pd.to_numeric(
        df["EGSA2026_27_monthly_payment"],
        errors="coerce"
    ).fillna(0)


    # --------------------------------------------------------
    # End 2026 Achievement
    # --------------------------------------------------------

    df["End_2026_achievement"] = pd.to_numeric(
        df["End_2026_achievement"],
        errors="coerce"
    ).fillna(0)


    # --------------------------------------------------------
    # 2027 Half Year Plan
    # --------------------------------------------------------

    df["EGSA2027_Half_Year_plan"] = pd.to_numeric(
        df["EGSA2027_Half_Year_plan"],
        errors="coerce"
    ).fillna(0)


    # --------------------------------------------------------
    # 2027 Half Year Achievement
    # --------------------------------------------------------

    df["EGSA2027_Half_Year_achievement"] = pd.to_numeric(
        df["EGSA2027_Half_Year_achievement"],
        errors="coerce"
    ).fillna(0)


    return df


# Load data
df = load_data()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Filters")


# ------------------------------------------------------------
# Business Date Range
# ------------------------------------------------------------

valid_dates = df["business_date"].dropna()


if not valid_dates.empty:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

else:

    min_date = pd.Timestamp.today().date()
    max_date = pd.Timestamp.today().date()


date_range = st.sidebar.date_input(
    "Business Date Range",
    value=[
        min_date,
        max_date
    ]
)


# ------------------------------------------------------------
# Member ID
# ------------------------------------------------------------

selected_ids = st.sidebar.multiselect(
    "Select Member ID",
    sorted(df["id"].dropna().unique())
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


# ------------------------------------------------------------
# Business Date Filter
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Member ID Filter
# ------------------------------------------------------------

if selected_ids:

    filtered_df = filtered_df[
        filtered_df["id"].isin(selected_ids)
    ]


# ============================================================
# MEMBER SUMMARY FOR MAIN REPORT
# ============================================================

member_summary = (
    filtered_df
    .groupby(
        ["business_date", "id", "Name"],
        as_index=False
    )
    .agg(

        # Payment can occur by date
        EGSA2026_27_monthly_payment=(
            "EGSA2026_27_monthly_payment",
            "sum"
        ),

        # Half year plan
        EGSA2027_Half_Year_plan=(
            "EGSA2027_Half_Year_plan",
            "sum"
        ),

        # Half year achievement
        EGSA2027_Half_Year_achievement=(
            "EGSA2027_Half_Year_achievement",
            "sum"
        )
    )
)


# ============================================================
# END 2026 ACHIEVEMENT
# ============================================================

# End_2026_achievement is a cumulative/member-level amount.
#
# Therefore:
#   1. Group by member
#   2. Take MAX for each member
#   3. Sum the member-level values
#
# This prevents the same member's achievement from being
# incorrectly duplicated across multiple business dates.

end_2026_by_member = (
    filtered_df
    .groupby(
        ["id", "Name"],
        as_index=False
    )["End_2026_achievement"]
    .max()
)


total_achievement = (
    end_2026_by_member[
        "End_2026_achievement"
    ].sum()
)


# ============================================================
# MAIN REPORT
# ============================================================

st.markdown(
    """
    <div class="report-box">
        <h3>Member Payment Report</h3>
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Prepare display dataframe
# ------------------------------------------------------------

display_df = member_summary.copy()


# Format Business Date
display_df["business_date"] = (
    display_df["business_date"]
    .dt.strftime("%Y-%m-%d")
)


# ------------------------------------------------------------
# Display report
# ------------------------------------------------------------

st.dataframe(
    display_df[
        [
            "business_date",
            "id",
            "Name",
            "EGSA2026_27_monthly_payment",
            "EGSA2027_Half_Year_plan",
            "EGSA2027_Half_Year_achievement"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SUMMARY
# ============================================================

st.markdown(
    """
    <div class="summary-box">
        <h3>Summary</h3>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUMMARY CALCULATIONS
# ============================================================

# Total members in the dashboard
if selected_ids:

    TOTAL_MEMBERS = len(selected_ids)

else:

    TOTAL_MEMBERS = df["id"].nunique()


# Monthly target per member
MONTHLY_TARGET = 1000


# ------------------------------------------------------------
# Total Monthly Payment
# ------------------------------------------------------------

total_monthly_payment = (
    filtered_df[
        "EGSA2026_27_monthly_payment"
    ].sum()
)


# ------------------------------------------------------------
# End 2026 Achievement
# ------------------------------------------------------------

# IMPORTANT:
# Do NOT use:
#
# member_summary["End_2026_achievement"].sum()
#
# because member_summary is grouped by business_date.
#
# Instead we already calculated:
#
# total_achievement
#
# at member level above.


# ------------------------------------------------------------
# Half Year Plan
# ------------------------------------------------------------

total_half_plan = (
    filtered_df[
        "EGSA2027_Half_Year_plan"
    ].sum()
    + 168000
)


# ------------------------------------------------------------
# Half Year Achievement
# ------------------------------------------------------------

total_half_achieved = (
    filtered_df[
        "EGSA2027_Half_Year_achievement"
    ].sum()
    + total_monthly_payment
)


# ------------------------------------------------------------
# Total Collected
# ------------------------------------------------------------

total_collected = (
    total_achievement
    + total_half_achieved
)


# ------------------------------------------------------------
# Expected Monthly Amount
# ------------------------------------------------------------

expected_amount = (
    TOTAL_MEMBERS
    *
    MONTHLY_TARGET
)


# ------------------------------------------------------------
# Outstanding Monthly Amount
# ------------------------------------------------------------

outstanding_amount = (
    expected_amount
    -
    total_monthly_payment
)


# ============================================================
# MEMBER PAYMENT STATUS
# ============================================================

member_payment_status = (
    filtered_df
    .groupby(
        ["id", "Name"],
        as_index=False
    )["EGSA2026_27_monthly_payment"]
    .sum()
)


# ------------------------------------------------------------
# Paid Members
# ------------------------------------------------------------

paid_members = member_payment_status[
    member_payment_status[
        "EGSA2026_27_monthly_payment"
    ] > 0
].shape[0]


# ------------------------------------------------------------
# Unpaid Members
# ------------------------------------------------------------

unpaid_members = member_payment_status[
    member_payment_status[
        "EGSA2026_27_monthly_payment"
    ] == 0
].shape[0]


# ============================================================
# METRICS - FIRST ROW
# ============================================================

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


# ============================================================
# METRICS - SECOND ROW
# ============================================================

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


# ============================================================
# TOTAL COLLECTED
# ============================================================

col9 = st.columns(1)[0]


with col9:

    st.metric(
        "Total Collected",
        f"{total_collected:,.2f}"
    )


# ============================================================
# UNPAID MEMBERS LIST
# ============================================================

st.markdown(
    """
    <div class="report-box">
        <h3>Members Who Did Not Pay Monthly Contribution</h3>
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Calculate payment by member
# ------------------------------------------------------------

unpaid_df = (
    filtered_df
    .groupby(
        ["id", "Name"],
        as_index=False
    )["EGSA2026_27_monthly_payment"]
    .sum()
)


# ------------------------------------------------------------
# Keep only members with zero payment
# ------------------------------------------------------------

unpaid_df = unpaid_df[
    unpaid_df[
        "EGSA2026_27_monthly_payment"
    ] == 0
]


# ------------------------------------------------------------
# Display only ID and Name
# ------------------------------------------------------------

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
