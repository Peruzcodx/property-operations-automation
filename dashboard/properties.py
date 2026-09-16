from decimal import Decimal

import streamlit as st
from api import (
    get_properties,
    get_property_overview,
    create_property,
    create_unit,
    create_tenant,
    create_inspection,
    create_maintenance_request,
    create_rent,
)


def show_properties_page():
    # ---------------------------------------------------------
    # Add-property form
    # ---------------------------------------------------------
    if st.session_state.get("property_action") == "add":
        show_add_property_form()
        return

    # ---------------------------------------------------------
    # Property detail
    # ---------------------------------------------------------
    if (
        "selected_property_id" in st.session_state
        and st.session_state.get("property_action") == "view"
    ):
        show_property_detail(
            st.session_state.selected_property_id
        )
        return

    # ---------------------------------------------------------
    # Property list
    # ---------------------------------------------------------
    st.title("Properties")
    st.caption("Manage properties in the portfolio")

    properties = get_properties()

    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.metric(
            "Total Properties",
            len(properties),
        )

    with top_right:
        if st.button(
            "＋ Add Property",
            type="primary",
            width="stretch",
        ):
            st.session_state.property_action = "add"
            st.rerun()

    st.divider()

    if not properties:
        st.info("No properties found.")
        return

    for property_item in properties:
        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [3, 3, 1]
            )

            with col1:
                st.markdown(
                    f"### "
                    f"{property_item['property_name']}"
                )

            with col2:
                st.write(
                    property_item["address"]
                )
                st.caption(
                    property_item["property_type"]
                )

            with col3:
                if st.button(
                    "View",
                    key=(
                        f"view_property_"
                        f"{property_item['id']}"
                    ),
                    width="stretch",
                ):
                    st.session_state[
                        "selected_property_id"
                    ] = property_item["id"]

                    st.session_state[
                        "property_action"
                    ] = "view"

                    st.rerun()


# =========================================================
# ADD PROPERTY
# =========================================================

def show_add_property_form():
    st.title("Add Property")
    st.caption(
        "Create a new property in the portfolio"
    )

    if st.button("← Back to Properties"):
        st.session_state.property_action = "list"
        st.rerun()

    st.divider()

    with st.form("add_property_form"):

        property_name = st.text_input(
            "Property Name",
            placeholder=(
                "e.g. Cedar Grove Apartments"
            ),
        )

        address = st.text_input(
            "Address",
            placeholder=(
                "e.g. 25 Admiralty Road, "
                "Lekki Phase 1, Lagos"
            ),
        )

        property_type = st.selectbox(
            "Property Type",
            [
                "Apartment",
                "House",
                "Commercial",
                "Office",
                "Warehouse",
                "Other",
            ],
        )

        submitted = st.form_submit_button(
            "Create Property",
            type="primary",
            width="stretch",
        )

    if submitted:

        if not property_name.strip():
            st.error(
                "Property name is required."
            )
            return

        if not address.strip():
            st.error(
                "Address is required."
            )
            return

        try:
            created = create_property(
                property_name=property_name.strip(),
                address=address.strip(),
                property_type=property_type,
            )

            st.session_state[
                "selected_property_id"
            ] = created["id"]

            st.session_state[
                "property_action"
            ] = "view"

            st.rerun()

        except Exception as exc:
            st.error(
                f"Could not create property: {exc}"
            )


# =========================================================
# PROPERTY DETAIL
# =========================================================

def show_property_detail(property_id: int):

    # ---------------------------------------------------------
    # ONE API REQUEST FOR THE WHOLE PROPERTY
    # ---------------------------------------------------------
    overview = get_property_overview(
        property_id
    )

    property_item = overview["property"]
    units = overview["units"]
    tenants = overview["tenants"]
    inspections = overview["inspections"]
    maintenance = overview["maintenance"]
    rent = overview["rent"]
    # ---------------------------------------------------------
    # Back button
    # ---------------------------------------------------------
    st.write("")

    if st.button("← Back to Properties"):
        st.session_state.pop(
            "selected_property_id",
            None,
        )

        st.session_state.property_action = "list"

        st.rerun()

    # ---------------------------------------------------------
    # Property information
    # ---------------------------------------------------------
    st.title(
        property_item["property_name"]
    )

    st.caption("Property details")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "### Property Information"
        )

        st.write(
            f"**Property ID:** "
            f"{property_item['id']}"
        )

        st.write(
            f"**Property Type:** "
            f"{property_item['property_type']}"
        )

    with col2:
        st.markdown("### Location")

        st.write(
            property_item["address"]
        )

    st.divider()

    # ---------------------------------------------------------
    # Property operations
    # ---------------------------------------------------------
    st.subheader(
        "Property Operations"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Units",
            "Tenants",
            "Inspections",
            "Maintenance",
            "Rent",
        ]
    )

    # =========================================================
    # UNITS
    # =========================================================

    with tab1:

        top_left, top_right = st.columns(
            [4, 1]
        )

        with top_left:
            st.markdown("### Units")

            st.caption(
                f"{len(units)} unit"
                f"{'s' if len(units) != 1 else ''}"
            )

        with top_right:
            if st.button(
                "＋ Add Unit",
                type="primary",
                width="stretch",
                key=f"add_unit_{property_id}",
            ):
                st.session_state[
                    "unit_action"
                ] = "add"

        if st.session_state.get(
            "unit_action"
        ) == "add":

            st.divider()

            st.markdown("### Add Unit")

            with st.form(
                f"add_unit_form_{property_id}"
            ):

                unit_name = st.text_input(
                    "Unit Name",
                    placeholder="e.g. Unit 4A",
                )

                col1, col2 = st.columns(2)

                with col1:
                    submitted = (
                        st.form_submit_button(
                            "Create Unit",
                            type="primary",
                            width="stretch",
                        )
                    )

                with col2:
                    cancelled = (
                        st.form_submit_button(
                            "Cancel",
                            width="stretch",
                        )
                    )

            if cancelled:
                st.session_state[
                    "unit_action"
                ] = None

                st.rerun()

            if submitted:

                if not unit_name.strip():
                    st.error(
                        "Unit name is required."
                    )

                else:
                    try:
                        created = create_unit(
                            property_id=property_id,
                            unit_name=unit_name.strip(),
                        )

                        st.session_state[
                            "unit_action"
                        ] = None

                        st.success(
                            f"{created['unit_name']} "
                            "was created successfully."
                        )

                        st.rerun()

                    except Exception as exc:
                        st.error(
                            f"Could not create unit: "
                            f"{exc}"
                        )

        if not units:
            st.info(
                "No units found for this property."
            )

        else:
            for unit in units:

                with st.container(
                    border=True
                ):

                    col1, col2 = st.columns(
                        [3, 1]
                    )

                    with col1:
                        st.markdown(
                            f"**{unit['unit_name']}**"
                        )

                        st.caption(
                            f"Unit ID: {unit['id']}"
                        )

                    with col2:
                        st.caption(
                            "Property"
                        )

                        st.write(
                            f"#{property_id}"
                        )

    # =========================================================
    # TENANTS
    # =========================================================

    with tab2:

        top_left, top_right = st.columns(
            [4, 1]
        )

        with top_left:
            st.markdown("### Tenants")

            st.caption(
                f"{len(tenants)} tenant"
                f"{'s' if len(tenants) != 1 else ''}"
            )

        with top_right:
            if st.button(
                "＋ Add Tenant",
                type="primary",
                width="stretch",
                key=f"add_tenant_{property_id}",
            ):
                st.session_state[
                    "tenant_action"
                ] = "add"

        if st.session_state.get(
            "tenant_action"
        ) == "add":

            st.divider()

            st.markdown(
                "### Add Tenant"
            )

            if not units:
                st.warning(
                    "This property has no units yet. "
                    "Add a unit before creating a tenant."
                )

            else:

                unit_options = {
                    (
                        f"{unit['unit_name']} "
                        f"(ID: {unit['id']})"
                    ): unit["id"]
                    for unit in units
                }

                with st.form(
                    f"add_tenant_form_{property_id}"
                ):

                    name = st.text_input(
                        "Full Name",
                        placeholder="e.g. John Doe",
                    )

                    email = st.text_input(
                        "Email",
                        placeholder=(
                            "e.g. john@example.com"
                        ),
                    )

                    phone = st.text_input(
                        "Phone",
                        placeholder=(
                            "e.g. +2348012345678"
                        ),
                    )

                    selected_unit = (
                        st.selectbox(
                            "Unit",
                            list(
                                unit_options.keys()
                            ),
                        )
                    )

                    col1, col2 = st.columns(
                        2
                    )

                    with col1:
                        submitted = (
                            st.form_submit_button(
                                "Create Tenant",
                                type="primary",
                                width="stretch",
                            )
                        )

                    with col2:
                        cancelled = (
                            st.form_submit_button(
                                "Cancel",
                                width="stretch",
                            )
                        )

                if cancelled:
                    st.session_state[
                        "tenant_action"
                    ] = None

                    st.rerun()

                if submitted:

                    if not name.strip():
                        st.error(
                            "Full name is required."
                        )

                    elif not email.strip():
                        st.error(
                            "Email is required."
                        )

                    elif not phone.strip():
                        st.error(
                            "Phone is required."
                        )

                    else:
                        try:
                            created = create_tenant(
                                unit_id=unit_options[
                                    selected_unit
                                ],
                                name=name.strip(),
                                email=email.strip(),
                                phone=phone.strip(),
                            )

                            st.session_state[
                                "tenant_action"
                            ] = None

                            st.success(
                                f"{created['name']} "
                                "was created successfully."
                            )

                            st.rerun()

                        except Exception as exc:
                            st.error(
                                f"Could not create tenant: "
                                f"{exc}"
                            )

        if not tenants:
            st.info(
                "No tenants found for this property."
            )

        else:

            unit_lookup = {
                unit["id"]: unit["unit_name"]
                for unit in units
            }

            for tenant in tenants:

                unit_name = unit_lookup.get(
                    tenant["unit_id"],
                    f"Unit {tenant['unit_id']}",
                )

                with st.container(
                    border=True
                ):

                    col1, col2 = st.columns(
                        [2, 2]
                    )

                    with col1:
                        st.markdown(
                            f"**{tenant['name']}**"
                        )

                        st.caption(
                            f"Tenant ID: {tenant['id']}"
                        )

                    with col2:

                        st.write(
                            f"**Unit:** "
                            f"{unit_name}"
                        )

                        st.write(
                            f"**Email:** "
                            f"{tenant['email']}"
                        )

                        st.write(
                            f"**Phone:** "
                            f"{tenant['phone']}"
                        )

    # =========================================================
    # INSPECTIONS
    # =========================================================

    with tab3:

        top_left, top_right = st.columns(
            [4, 1]
        )

        with top_left:
            st.markdown(
                "### Inspections"
            )

            st.caption(
                f"{len(inspections)} inspection"
                f"{'s' if len(inspections) != 1 else ''}"
            )

        with top_right:
            if st.button(
                "＋ New Inspection",
                type="primary",
                width="stretch",
                key=f"add_inspection_{property_id}",
            ):
                st.session_state[
                    "inspection_action"
                ] = "add"

        if st.session_state.get(
            "inspection_action"
        ) == "add":

            st.divider()

            st.markdown(
                "### New Inspection"
            )

            if not units:
                st.warning(
                    "This property has no units yet. "
                    "Add a unit before creating an inspection."
                )

            else:

                unit_options = {
                    (
                        f"{unit['unit_name']} "
                        f"(ID: {unit['id']})"
                    ): unit["id"]
                    for unit in units
                }

                with st.form(
                    f"add_inspection_form_{property_id}"
                ):

                    selected_unit = (
                        st.selectbox(
                            "Unit",
                            list(
                                unit_options.keys()
                            ),
                        )
                    )

                    inspection_type = (
                        st.selectbox(
                            "Inspection Type",
                            [
                                "Routine",
                                "Move-in",
                                "Move-out",
                                "Maintenance",
                                "Follow-up",
                            ],
                        )
                    )

                    inspection_date = (
                        st.date_input(
                            "Inspection Date"
                        )
                    )

                    inspector = st.text_input(
                        "Inspector",
                        placeholder=(
                            "e.g. John Carter"
                        ),
                    )

                    condition_notes = (
                        st.text_area(
                            "Condition Notes",
                            placeholder=(
                                "Describe the general "
                                "condition of the unit."
                            ),
                        )
                    )

                    flagged_issue = (
                        st.text_area(
                            "Flagged Issue",
                            placeholder=(
                                "Leave blank if no issue "
                                "was found."
                            ),
                        )
                    )

                    col1, col2 = st.columns(
                        2
                    )

                    with col1:
                        submitted = (
                            st.form_submit_button(
                                "Create Inspection",
                                type="primary",
                                width="stretch",
                            )
                        )

                    with col2:
                        cancelled = (
                            st.form_submit_button(
                                "Cancel",
                                width="stretch",
                            )
                        )

                if cancelled:
                    st.session_state[
                        "inspection_action"
                    ] = None

                    st.rerun()

                if submitted:

                    if not inspector.strip():
                        st.error(
                            "Inspector is required."
                        )

                    else:
                        try:
                            created = (
                                create_inspection(
                                    unit_id=unit_options[
                                        selected_unit
                                    ],
                                    inspection_type=(
                                        inspection_type
                                    ),
                                    inspection_date=(
                                        inspection_date.isoformat()
                                    ),
                                    inspector=(
                                        inspector.strip()
                                    ),
                                    condition_notes=(
                                        condition_notes.strip()
                                        or None
                                    ),
                                    flagged_issue=(
                                        flagged_issue.strip()
                                        or None
                                    ),
                                )
                            )

                            st.session_state[
                                "inspection_action"
                            ] = None

                            st.success(
                                f"Inspection #{created['id']} "
                                "was created successfully."
                            )

                            st.rerun()

                        except Exception as exc:
                            st.error(
                                f"Could not create inspection: "
                                f"{exc}"
                            )

        # -----------------------------------------------------
        # Inspection records
        # -----------------------------------------------------

        if not inspections:
            st.info(
                "No inspections found for this property."
            )

        else:

            unit_lookup = {
                unit["id"]: unit["unit_name"]
                for unit in units
            }

            for inspection in inspections:

                with st.container(
                    border=True
                ):

                    col1, col2 = st.columns(
                        [2, 3]
                    )

                    with col1:

                        st.markdown(
                            f"**"
                            f"{inspection['inspection_type']}"
                            f"**"
                        )

                        st.caption(
                            f"Inspection ID: "
                            f"{inspection['id']}"
                        )

                        st.caption(
                            f"Unit: "
                            f"{unit_lookup.get(
                                inspection['unit_id'],
                                f'Unit {inspection["unit_id"]}'
                            )}"
                        )

                    with col2:

                        st.write(
                            f"**Date:** "
                            f"{inspection['inspection_date']}"
                        )

                        st.write(
                            f"**Inspector:** "
                            f"{inspection['inspector']}"
                        )

                        if inspection[
                            "condition_notes"
                        ]:
                            st.write(
                                f"**Notes:** "
                                f"{inspection['condition_notes']}"
                            )

                        if inspection[
                            "flagged_issue"
                        ]:

                            st.warning(
                                f"Flagged issue: "
                                f"{inspection['flagged_issue']}"
                            )

                            button_key = (
                                "create_maintenance_"
                                f"{inspection['id']}"
                            )

                            if st.button(
                                "Create Maintenance Request",
                                key=button_key,
                                type="primary",
                                width="stretch",
                            ):
                                st.session_state[
                                    "maintenance_from_inspection"
                                ] = inspection["id"]

                                st.rerun()

        # -----------------------------------------------------
        # Create maintenance request from inspection
        # -----------------------------------------------------

        maintenance_inspection_id = (
            st.session_state.get(
                "maintenance_from_inspection"
            )
        )

        if maintenance_inspection_id is not None:

            selected_inspection = next(
                (
                    item
                    for item in inspections
                    if item["id"]
                    == maintenance_inspection_id
                ),
                None,
            )

            if selected_inspection:

                st.divider()

                st.markdown(
                    "### Create Maintenance Request"
                )

                with st.form(
                    f"maintenance_form_"
                    f"{selected_inspection['id']}"
                ):

                    st.text_input(
                        "Unit",
                        value=(
                            f"Unit: "
                            f"{unit_lookup.get(
                                selected_inspection['unit_id'],
                                f'Unit {selected_inspection["unit_id"]}'
                            )}"
                        ),
                        disabled=True,
                    )

                    st.text_input(
                        "Inspection",
                        value=(
                            f"Inspection #"
                            f"{selected_inspection['id']}"
                        ),
                        disabled=True,
                    )

                    description = st.text_area(
                        "Description",
                        value=(
                            selected_inspection[
                                "flagged_issue"
                            ]
                            or ""
                        ),
                    )

                    reported_by = st.text_input(
                        "Reported By",
                        value=(
                            selected_inspection[
                                "inspector"
                            ]
                        ),
                    )

                    priority = st.selectbox(
                        "Priority",
                        [
                            "Low",
                            "Medium",
                            "High",
                            "Urgent",
                        ],
                        index=1,
                    )

                    assigned_contractor = (
                        st.text_input(
                            "Assigned Contractor",
                            placeholder="Optional",
                        )
                    )

                    col1, col2 = st.columns(
                        2
                    )

                    with col1:
                        submitted = (
                            st.form_submit_button(
                                "Create Request",
                                type="primary",
                                width="stretch",
                            )
                        )

                    with col2:
                        cancelled = (
                            st.form_submit_button(
                                "Cancel",
                                width="stretch",
                            )
                        )

                if cancelled:

                    st.session_state.pop(
                        "maintenance_from_inspection",
                        None,
                    )

                    st.rerun()

                if submitted:

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

                            created = (
                                create_maintenance_request(
                                    unit_id=(
                                        selected_inspection[
                                            "unit_id"
                                        ]
                                    ),
                                    inspection_id=(
                                        selected_inspection[
                                            "id"
                                        ]
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
                                        or None
                                    ),
                                )
                            )

                            st.session_state.pop(
                                "maintenance_from_inspection",
                                None,
                            )

                            st.success(
                                f"Maintenance request "
                                f"#{created['id']} created."
                            )

                            st.rerun()

                        except Exception as exc:
                            st.error(
                                "Could not create "
                                f"maintenance request: "
                                f"{exc}"
                            )

    # =========================================================
    # MAINTENANCE
    # =========================================================

    with tab4:

        st.markdown(
            "### Maintenance"
        )

        st.caption(
            f"{len(maintenance)} request"
            f"{'s' if len(maintenance) != 1 else ''}"
        )

        if not maintenance:
            st.info(
                "No maintenance requests found "
                "for this property."
            )

        else:

            unit_lookup = {
                unit["id"]: unit["unit_name"]
                for unit in units
            }

            for request in maintenance:

                with st.container(
                    border=True
                ):

                    col1, col2 = st.columns(
                        [2, 3]
                    )

                    with col1:

                        st.markdown(
                            f"**"
                            f"{request['description']}"
                            f"**"
                        )

                        st.caption(
                            f"Request ID: "
                            f"{request['id']}"
                        )

                        st.caption(
                            f"Unit: "
                            f"{unit_lookup.get(
                                request['unit_id'],
                                f'Unit {request["unit_id"]}'
                            )}"
                        )

                    with col2:

                        st.write(
                            f"**Priority:** "
                            f"{request['priority']}"
                        )

                        st.write(
                            f"**Status:** "
                            f"{request['status']}"
                        )

                        if request[
                            "assigned_contractor"
                        ]:
                            st.write(
                                f"**Contractor:** "
                                f"{request['assigned_contractor']}"
                            )

                        st.caption(
                            f"Reported by: "
                            f"{request['reported_by']}"
                        )

                        if request["status"] == "Resolved":

                            if request[
                                "resolved_at"
                            ]:
                                st.write(
                                    f"**Resolved:** "
                                    f"{request['resolved_at']}"
                                )

                            if request[
                                "resolution_notes"
                            ]:
                                st.write(
                                    f"**Resolution:** "
                                    f"{request['resolution_notes']}"
                                )

    # =========================================================
    # RENT
    # =========================================================

    with tab5:

        st.markdown(
            "### Rent"
        )

        st.caption(
            f"{len(rent)} rent record"
            f"{'s' if len(rent) != 1 else ''}"
        )

        if not rent:
            st.info(
                "No rent records found "
                "for this property."
            )

        else:

            unit_lookup = {
                unit["id"]: unit["unit_name"]
                for unit in units
            }

            tenant_lookup = {
                tenant["id"]: tenant["name"]
                for tenant in tenants
            }

            for record in rent:

                unit_name = unit_lookup.get(
                    record["unit_id"],
                    f"Unit {record['unit_id']}",
                )

                tenant_name = tenant_lookup.get(
                    record["tenant_id"],
                    f"Tenant {record['tenant_id']}",
                )

                rent_amount = Decimal(
                    record["rent_amount"]
                )

                amount_paid = Decimal(
                    record["amount_paid"]
                )

                outstanding = (
                    rent_amount - amount_paid
                )

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {tenant_name}"
                    )

                    st.caption(
                        f"{unit_name} • "
                        f"Rent Record "
                        f"#{record['id']}"
                    )

                    col1, col2, col3 = (
                        st.columns(3)
                    )

                    with col1:
                        st.metric(
                            "Rent Amount",
                            f"₦{rent_amount:,.2f}",
                        )

                    with col2:
                        st.metric(
                            "Amount Paid",
                            f"₦{amount_paid:,.2f}",
                        )

                    with col3:
                        st.metric(
                            "Outstanding",
                            f"₦{outstanding:,.2f}",
                        )

                    st.write(
                        f"**Status:** "
                        f"{record['payment_status']}"
                    )

                    st.write(
                        f"**Due Date:** "
                        f"{record['due_date']}"
                    )

                    if record["payment_date"]:
                        st.write(
                            f"**Payment Date:** "
                            f"{record['payment_date']}"
                        )

                    if record["notes"]:
                        st.caption(
                            record["notes"]
                        )