from datetime import datetime
import io

import pandas as pd
import streamlit as st

from api import (
    get_inspections,
    get_units,
    create_inspection,
    create_maintenance_request,
)


# =========================================================
# DATE FORMATTING
# =========================================================

def format_date(value):
    if not value:
        return "Not recorded"

    try:
        return datetime.fromisoformat(
            str(value)
        ).strftime("%b %d, %Y")
    except ValueError:
        return str(value)


# =========================================================
# INSPECTIONS PAGE
# =========================================================

def show_inspections_page():
    st.title("Inspections")
    st.caption("Property inspection management")

    inspections = get_inspections()
    units = get_units()

    unit_map = {
        unit["id"]: unit["unit_name"]
        for unit in units
    }

    if not inspections:
        st.info("No inspections found.")
    else:

        # =====================================================
        # SUMMARY
        # =====================================================

        total_inspections = len(inspections)

        flagged_inspections = [
            inspection
            for inspection in inspections
            if inspection["flagged_issue"]
        ]

        clean_inspections = (
            total_inspections
            - len(flagged_inspections)
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Inspections",
            total_inspections,
        )

        col2.metric(
            "Flagged Issues",
            len(flagged_inspections),
        )

        col3.metric(
            "No Issues Flagged",
            clean_inspections,
        )

        st.divider()

        # =====================================================
        # FILTER
        # =====================================================

        left, right = st.columns([3, 1])

        with left:

            issue_filter = st.selectbox(
                "Filter inspections",
                [
                    "All",
                    "Flagged Issues",
                    "No Issues",
                ],
            )

        filtered_inspections = inspections

        if issue_filter == "Flagged Issues":
            filtered_inspections = [
                inspection
                for inspection in inspections
                if inspection["flagged_issue"]
            ]

        elif issue_filter == "No Issues":
            filtered_inspections = [
                inspection
                for inspection in inspections
                if not inspection["flagged_issue"]
            ]

        # =====================================================
        # CSV DOWNLOAD
        # =====================================================

        with right:

            export_rows = []

            for inspection in filtered_inspections:

                export_rows.append(
                    {
                        "Inspection ID": inspection["id"],
                        "Unit": unit_map.get(
                            inspection["unit_id"],
                            f"Unit {inspection['unit_id']}",
                        ),
                        "Inspection Type": inspection[
                            "inspection_type"
                        ],
                        "Inspection Date": format_date(
                            inspection["inspection_date"]
                        ),
                        "Inspector": inspection["inspector"],
                        "Condition Notes": (
                            inspection["condition_notes"]
                            or ""
                        ),
                        "Flagged Issue": (
                            inspection["flagged_issue"]
                            or ""
                        ),
                    }
                )

            export_df = pd.DataFrame(
                export_rows
            )

            csv_buffer = io.StringIO()

            export_df.to_csv(
                csv_buffer,
                index=False,
            )

            st.download_button(
                label="Download CSV",
                data=csv_buffer.getvalue(),
                file_name="inspection_records.csv",
                mime="text/csv",
                width="stretch",
            )

        # =====================================================
        # INSPECTION RECORDS
        # =====================================================

        st.subheader("Inspection Records")

        if not filtered_inspections:
            st.info(
                "No inspections match this filter."
            )

        for inspection in filtered_inspections:

            flagged_issue = inspection[
                "flagged_issue"
            ]

            if flagged_issue:
                status_label = "🔴 Issue Flagged"
            else:
                status_label = "🟢 No Issue"

            unit_name = unit_map.get(
                inspection["unit_id"],
                f"Unit {inspection['unit_id']}",
            )

            with st.container(
                border=True
            ):

                top_left, top_right = st.columns(
                    [3, 1]
                )

                with top_left:

                    st.markdown(
                        f"### Inspection #{inspection['id']}"
                    )

                    st.write(
                        f"Unit: {unit_name}"
                    )

                    st.write(
                        f"Type: {inspection['inspection_type']}"
                    )

                    st.write(
                        f"Inspector: {inspection['inspector']}"
                    )

                with top_right:

                    st.markdown(
                        f"**{status_label}**"
                    )

                    st.write(
                        "Date: "
                        f"{format_date(inspection['inspection_date'])}"
                    )

                if inspection["condition_notes"]:

                    st.write(
                        "Condition notes: "
                        f"{inspection['condition_notes']}"
                    )

                if flagged_issue:

                    st.warning(
                        f"Flagged issue: {flagged_issue}"
                    )

                    st.write(
                        "This issue can be converted "
                        "into a maintenance request."
                    )

                    maintenance_button = st.button(
                        "Create Maintenance Request",
                        key=(
                            f"maintenance_"
                            f"{inspection['id']}"
                        ),
                    )

                    if maintenance_button:

                        st.session_state[
                            "maintenance_inspection_id"
                        ] = inspection["id"]

                        st.session_state[
                            "maintenance_unit_id"
                        ] = inspection["unit_id"]

                        st.session_state[
                            "maintenance_description"
                        ] = flagged_issue

                st.caption(
                    f"Inspection ID: {inspection['id']}"
                )

    # =========================================================
    # CREATE INSPECTION
    # =========================================================

    st.divider()

    st.subheader("Create Inspection")

    with st.form(
        "create_inspection_form"
    ):

        unit_options = {
            f"{unit['unit_name']} (ID {unit['id']})":
            unit["id"]
            for unit in units
        }

        selected_unit_label = st.selectbox(
            "Unit",
            list(unit_options.keys())
            if unit_options
            else [],
        )

        inspection_type = st.text_input(
            "Inspection type",
            placeholder=(
                "e.g. Routine, Move-in, Move-out"
            ),
        )

        inspection_date = st.date_input(
            "Inspection date"
        )

        inspector = st.text_input(
            "Inspector"
        )

        condition_notes = st.text_area(
            "Condition notes"
        )

        flagged_issue = st.text_area(
            "Flagged issue",
            placeholder=(
                "Leave blank when no issue was found."
            ),
        )

        submitted = st.form_submit_button(
            "Create Inspection",
            type="primary",
        )

        if submitted:

            if not unit_options:
                st.error(
                    "No units are available."
                )

            elif not inspection_type.strip():
                st.error(
                    "Inspection type is required."
                )

            elif not inspector.strip():
                st.error(
                    "Inspector is required."
                )

            else:

                try:

                    create_inspection(
                        unit_id=unit_options[
                            selected_unit_label
                        ],
                        inspection_type=(
                            inspection_type.strip()
                        ),
                        inspection_date=str(
                            inspection_date
                        ),
                        inspector=inspector.strip(),
                        condition_notes=(
                            condition_notes.strip()
                            if condition_notes.strip()
                            else None
                        ),
                        flagged_issue=(
                            flagged_issue.strip()
                            if flagged_issue.strip()
                            else None
                        ),
                    )

                    st.success(
                        "Inspection created successfully."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Creation failed: {error}"
                    )

    # =========================================================
    # CREATE MAINTENANCE FROM INSPECTION
    # =========================================================

    if (
        "maintenance_inspection_id"
        in st.session_state
    ):

        st.divider()

        st.subheader(
            "Create Maintenance Request"
        )

        inspection_id = st.session_state[
            "maintenance_inspection_id"
        ]

        unit_id = st.session_state[
            "maintenance_unit_id"
        ]

        default_description = (
            st.session_state.get(
                "maintenance_description",
                "",
            )
        )

        inspection = next(
            (
                item
                for item in inspections
                if item["id"] == inspection_id
            ),
            None,
        )

        if inspection:

            st.info(
                "Maintenance request linked to "
                f"Inspection #{inspection_id}"
            )

            st.write(
                f"Unit: "
                f"{unit_map.get(unit_id, f'Unit {unit_id}')}"
            )

            with st.form(
                "create_maintenance_from_inspection"
            ):

                description = st.text_area(
                    "Description",
                    value=default_description,
                )

                reported_by = st.text_input(
                    "Reported by",
                    value=inspection[
                        "inspector"
                    ],
                )

                priority = st.selectbox(
                    "Priority",
                    [
                        "Low",
                        "Medium",
                        "High",
                        "Urgent",
                    ],
                )

                assigned_contractor = (
                    st.text_input(
                        "Assigned contractor"
                    )
                )

                maintenance_submitted = (
                    st.form_submit_button(
                        "Create Maintenance Request",
                        type="primary",
                    )
                )

                if maintenance_submitted:

                    if not description.strip():
                        st.error(
                            "Description is required."
                        )

                    elif not reported_by.strip():
                        st.error(
                            "Reported by is required."
                        )

                    else:

                        try:

                            create_maintenance_request(
                                unit_id=unit_id,
                                inspection_id=(
                                    inspection_id
                                ),
                                description=(
                                    description.strip()
                                ),
                                reported_by=(
                                    reported_by.strip()
                                ),
                                priority=priority,
                                assigned_contractor=(
                                    assigned_contractor.strip()
                                    if assigned_contractor.strip()
                                    else None
                                ),
                            )

                            st.success(
                                "Maintenance request "
                                "created successfully."
                            )

                            del st.session_state[
                                "maintenance_inspection_id"
                            ]

                            del st.session_state[
                                "maintenance_unit_id"
                            ]

                            del st.session_state[
                                "maintenance_description"
                            ]

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Creation failed: {error}"
                            )