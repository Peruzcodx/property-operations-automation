import streamlit as st

from properties import show_properties_page
from maintenance import show_maintenance_page
from inspections import show_inspections_page
from rent import show_rent_page
from api import get_dashboard_summary
from reports import show_reports_page
st.set_page_config(
    page_title="Property Operations Automation",
    page_icon="🏢",
    layout="wide",
)


# =========================================================
# PAGE STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = st.query_params.get(
        "page",
        "Dashboard",
    )

# =========================================================
# GLOBAL STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #171b21;
    }

    [data-testid="stSidebarContent"] {
        padding-top: 1.5rem;
    }

    /* Navigation buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 500;
        text-align: left;
        padding: 0.6rem 0.85rem;
        margin-bottom: 0.3rem;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid transparent;
        color: #e6e9ed;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background-color: #222933;
        border-color: #303a46;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #293541;
        border: 1px solid #44515f;
        color: #ffffff;
    }

    /* Sidebar brand */
    .sidebar-brand {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .sidebar-subtitle {
        font-size: 15px;
        color: #9aa4b2;
        margin-bottom: 24px;
    }

    .sidebar-nav-heading {
        font-size: 12px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.05em;
        margin-bottom: 9px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">🏠 Homestead</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">Property Operations</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-nav-heading">NAVIGATION</div>',
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
            key=f"sidebar_{item}",
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


page = st.session_state.page


# =========================================================
# PAGE ROUTING
# =========================================================

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


# =========================================================
# DASHBOARD
# =========================================================

st.title("Property Operations Dashboard")
st.caption("Internal management operations")


# =========================================================
# LOAD DASHBOARD SUMMARY
# =========================================================

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


# =========================================================
# KPI CARDS
# =========================================================

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


# =========================================================
# OPERATIONS OVERVIEW
# =========================================================

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
# =========================================================
# RECENT ACTIVITY
# =========================================================

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