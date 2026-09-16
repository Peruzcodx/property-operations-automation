import streamlit as st

from api import get_dashboard_summary
from properties import show_properties_page
from maintenance import show_maintenance_page
from inspections import show_inspections_page
from rent import show_rent_page
from reports import show_reports_page


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Property Operations Automation",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PAGE STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = st.query_params.get(
        "page",
        "Dashboard",
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN APP
       ======================================================== */

    .block-container {
        max-width: 1500px;
        padding-top: 2.8rem !important;
        padding-bottom: 2.5rem;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #171b22 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.10);
        z-index: 999999 !important;
    }

    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] > div > div {
        background-color: #171b22 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #d1d5db;
    }


    /* ========================================================
       BRAND
       ======================================================== */

    .sidebar-brand {
        color: #ffffff !important;
        font-size: 1.70rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }

    .sidebar-subtitle {
        color: #9ca3af !important;
        font-size: 0.82rem;
        line-height: 1.2;
        margin-bottom: 1.35rem;
    }


    /* ========================================================
       NAVIGATION HEADING
       ======================================================== */

    .sidebar-section-title {
        color: #9ca3af !important;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0.35rem 0 0.7rem 0;
    }


    /* ========================================================
       NAVIGATION BUTTONS
       ======================================================== */

    section[data-testid="stSidebar"] div.stButton {
        margin-bottom: 0.15rem;
    }

    section[data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        min-height: 38px !important;

        border-radius: 8px !important;
        border: 1px solid transparent !important;

        background-color: transparent !important;

        color: #d1d5db !important;

        font-size: 1rem !important;
        font-weight: 600 !important;

        text-align: left !important;

        padding: 0.32rem 0.55rem !important;

        box-shadow: none !important;

        transition:
            background-color 0.15s ease,
            border-color 0.15s ease,
            color 0.15s ease !important;
    }


    /* ========================================================
       ICON + TEXT ALIGNMENT
       ======================================================== */

    section[data-testid="stSidebar"]
    div.stButton
    > button
    > div {
        gap: 0.4rem !important;
        justify-content: flex-start !important;
        align-items: center !important;
    }

    section[data-testid="stSidebar"]
    div.stButton
    > button
    p,
    section[data-testid="stSidebar"]
    div.stButton
    > button
    span {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }


    /* ========================================================
       HOVER
       ======================================================== */

    section[data-testid="stSidebar"]
    div.stButton
    > button:hover {
        background-color: #222832 !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
    }


    /* ========================================================
       ACTIVE NAVIGATION
       ======================================================== */

    section[data-testid="stSidebar"]
    div.stButton
    > button[kind="primary"] {
        background-color: #26313d !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
    }


    /* ========================================================
       FOCUS
       ======================================================== */

    section[data-testid="stSidebar"]
    div.stButton
    > button:focus {
        outline: none !important;
        box-shadow: none !important;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        section[data-testid="stSidebar"] {
            width: 260px !important;
            min-width: 260px !important;
            max-width: 260px !important;

            background-color: #171b22 !important;

            box-shadow:
                8px 0 25px rgba(0, 0, 0, 0.30);
        }

        section[data-testid="stSidebar"] > div {
            width: 260px !important;
            background-color: #171b22 !important;

            max-height: 100vh !important;

            overflow-y: auto !important;
            overflow-x: hidden !important;

            box-sizing: border-box !important;
        }

        section[data-testid="stSidebar"] > div > div {
            background-color: #171b22 !important;
            height: auto !important;
            min-height: auto !important;
        }

        section[data-testid="stSidebar"] div.stButton > button {
            min-height: 38px !important;
            padding: 0.3rem 0.45rem !important;
            border-radius: 8px !important;
        }

        section[data-testid="stSidebar"]
        div.stButton
        > button
        p,
        section[data-testid="stSidebar"]
        div.stButton
        > button
        span {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
        }

        .sidebar-brand {
            font-size: 1.55rem;
        }

        .sidebar-subtitle {
            font-size: 0.78rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            🏠 Homestead
        </div>

        <div class="sidebar-subtitle">
            Property Operations
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-section-title">
            Navigation
        </div>
        """,
        unsafe_allow_html=True,
    )

    navigation_items = [
        ("Dashboard", ":material/dashboard:"),
        ("Properties", ":material/domain:"),
        ("Inspections", ":material/assignment:"),
        ("Maintenance", ":material/build:"),
        ("Rent", ":material/receipt_long:"),
        ("Reports", ":material/description:"),
    ]

    for item, icon in navigation_items:

        is_active = (
            st.session_state.page == item
        )

        if st.button(
            item,
            key=f"nav_{item}",
            icon=icon,
            width="stretch",
            type=(
                "primary"
                if is_active
                else "secondary"
            ),
        ):
            st.session_state.page = item
            st.query_params["page"] = item
            st.rerun()

    st.divider()


# ============================================================
# CURRENT PAGE
# ============================================================

page = st.session_state.page


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "Properties":
    show_properties_page()
    st.stop()

if page == "Inspections":
    show_inspections_page()
    st.stop()

if page == "Maintenance":
    show_maintenance_page()
    st.stop()

if page == "Rent":
    show_rent_page()
    st.stop()

if page == "Reports":
    show_reports_page()
    st.stop()


# ============================================================
# DASHBOARD
# ============================================================

st.title("Property Operations Dashboard")
st.caption("Internal management operations")


# ============================================================
# LOAD DASHBOARD SUMMARY
# ============================================================

summary = get_dashboard_summary()

properties_count = summary["properties_count"]
units_count = summary["units_count"]
tenants_count = summary["tenants_count"]

open_count = summary["maintenance"]["open"]
in_progress_count = summary["maintenance"]["in_progress"]
resolved_count = summary["maintenance"]["resolved"]

paid_count = summary["rent"]["paid"]
partial_count = summary["rent"]["partial"]
pending_count = summary["rent"]["pending"]
outstanding_rent = summary["rent"]["outstanding"]


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Properties",
    properties_count,
)

col2.metric(
    "Units",
    units_count,
)

col3.metric(
    "Tenants",
    tenants_count,
)

col4.metric(
    "Open Maintenance",
    open_count,
)

col5.metric(
    "Outstanding Rent",
    f"₦{outstanding_rent:,.2f}",
)


# ============================================================
# OPERATIONS OVERVIEW
# ============================================================

st.divider()

st.subheader("Operations Overview")

left, right = st.columns(2)

with left:

    st.markdown("### Maintenance")

    st.write(
        f"Open: {open_count}"
    )

    st.write(
        f"In Progress: {in_progress_count}"
    )

    st.write(
        f"Resolved: {resolved_count}"
    )


with right:

    st.markdown("### Rent")

    st.write(
        f"Paid: {paid_count}"
    )

    st.write(
        f"Partial: {partial_count}"
    )

    st.write(
        f"Pending: {pending_count}"
    )


# ============================================================
# RECENT ACTIVITY
# ============================================================

st.divider()

st.subheader("Recent Activity")

st.write(
    "Current operational activity across the portfolio."
)

activity_col1, activity_col2 = st.columns(2)

with activity_col1:

    st.markdown("### Maintenance")

    if open_count > 0:
        st.write(
            f"🔴 {open_count} maintenance request(s) "
            "currently open."
        )

    if in_progress_count > 0:
        st.write(
            f"🟡 {in_progress_count} maintenance "
            "request(s) in progress."
        )

    if resolved_count > 0:
        st.write(
            f"🟢 {resolved_count} maintenance "
            "request(s) resolved."
        )


with activity_col2:

    st.markdown("### Rent")

    if pending_count > 0:
        st.write(
            f"🔴 {pending_count} rent payment(s) "
            "pending."
        )

    if partial_count > 0:
        st.write(
            f"🟡 {partial_count} rent payment(s) "
            "partially paid."
        )

    if paid_count > 0:
        st.write(
            f"🟢 {paid_count} rent payment(s) "
            "paid."
        )