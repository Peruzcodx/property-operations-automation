import streamlit as st

from api import (
    get_maintenance,
    update_maintenance_request,
)


# =========================================================
# MAINTENANCE PAGE
# =========================================================

def show_maintenance_page():
    st.title("Maintenance")
    st.caption("Maintenance request management")

    maintenance_requests = get_maintenance()

    if not maintenance_requests:
        st.info("No maintenance requests found.")
        return

    # =====================================================
    # SUMMARY
    # =====================================================

    open_requests = [
        request
        for request in maintenance_requests
        if request["status"] == "Open"
    ]

    in_progress_requests = [
        request
        for request in maintenance_requests
        if request["status"] == "In Progress"
    ]

    resolved_requests = [
        request
        for request in maintenance_requests
        if request["status"] == "Resolved"
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Requests",
        len(maintenance_requests),
    )

    col2.metric(
        "Open",
        len(open_requests),
    )

    col3.metric(
        "In Progress",
        len(in_progress_requests),
    )

    col4.metric(
        "Resolved",
        len(resolved_requests),
    )

    st.divider()

    # =====================================================
    # FILTER
    # =====================================================

    st.subheader("Maintenance Requests")

    status_filter = st.selectbox(
        "Filter by status",
        [
            "All",
            "Open",
            "In Progress",
            "Resolved",
        ],
    )

    filtered_requests = maintenance_requests

    if status_filter != "All":
        filtered_requests = [
            request
            for request in maintenance_requests
            if request["status"] == status_filter
        ]

    if not filtered_requests:
        st.info("No requests match this filter.")
        return

    # =====================================================
    # REQUEST LIST
    # =====================================================

    for request in filtered_requests:

        status = request["status"]
        priority = request["priority"]

        if status == "Open":
            status_label = "🔴 Open"
        elif status == "In Progress":
            status_label = "🟡 In Progress"
        else:
            status_label = "🟢 Resolved"

        with st.container(border=True):

            top_left, top_right = st.columns([3, 1])

            with top_left:
                st.markdown(
                    f"### #{request['id']} — "
                    f"{request['description']}"
                )

                st.write(
                    f"Unit ID: {request['unit_id']}"
                )

                st.write(
                    f"Reported by: {request['reported_by']}"
                )

            with top_right:
                st.markdown(
                    f"**{status_label}**"
                )

                st.write(
                    f"Priority: {priority}"
                )

            contractor = (
                request["assigned_contractor"]
                or "Not assigned"
            )

            st.write(
                f"Assigned contractor: {contractor}"
            )

            if request["resolution_notes"]:
                st.write(
                    f"Resolution: "
                    f"{request['resolution_notes']}"
                )

            # =================================================
            # UPDATE FORM
            # =================================================

            with st.expander("Update request"):

                with st.form(
                    key=f"maintenance_form_{request['id']}"
                ):

                    new_priority = st.selectbox(
                        "Priority",
                        [
                            "Low",
                            "Medium",
                            "High",
                            "Urgent",
                        ],
                        index=[
                            "Low",
                            "Medium",
                            "High",
                            "Urgent",
                        ].index(request["priority"])
                        if request["priority"]
                        in [
                            "Low",
                            "Medium",
                            "High",
                            "Urgent",
                        ]
                        else 0,
                    )

                    new_contractor = st.text_input(
                        "Assigned contractor",
                        value=(
                            request["assigned_contractor"]
                            or ""
                        ),
                    )

                    new_status = st.selectbox(
                        "Status",
                        [
                            "Open",
                            "In Progress",
                            "Resolved",
                        ],
                        index=[
                            "Open",
                            "In Progress",
                            "Resolved",
                        ].index(request["status"])
                        if request["status"]
                        in [
                            "Open",
                            "In Progress",
                            "Resolved",
                        ]
                        else 0,
                    )

                    new_resolution_notes = st.text_area(
                        "Resolution notes",
                        value=(
                            request["resolution_notes"]
                            or ""
                        ),
                    )

                    submitted = st.form_submit_button(
                        "Update Request",
                        type="primary",
                    )

                    if submitted:

                        try:
                            update_maintenance_request(
                                maintenance_id=request["id"],
                                priority=new_priority,
                                assigned_contractor=(
                                    new_contractor
                                    if new_contractor.strip()
                                    else None
                                ),
                                status=new_status,
                                resolution_notes=(
                                    new_resolution_notes
                                    if new_resolution_notes.strip()
                                    else None
                                ),
                            )

                            st.success(
                                "Maintenance request updated."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"Update failed: {error}"
                            )