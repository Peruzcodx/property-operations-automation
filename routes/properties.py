from fastapi import APIRouter, HTTPException

from database import (
    get_connection,
    release_connection,
)
from schemas.property import (
    PropertyCreate,
    PropertyResponse,
)


router = APIRouter(
    prefix="/properties",
    tags=["Properties"],
)


# =========================================================
# GET ALL PROPERTIES
# =========================================================

@router.get("/")
def get_properties():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    property_name,
                    address,
                    property_type,
                    created_at
                FROM properties
                ORDER BY id;
                """
            )

            properties = cursor.fetchall()

            return {
                "properties": [
                    {
                        "id": row[0],
                        "property_name": row[1],
                        "address": row[2],
                        "property_type": row[3],
                        "created_at": row[4],
                    }
                    for row in properties
                ]
            }

    finally:
        release_connection(connection)


# =========================================================
# CREATE PROPERTY
# =========================================================

@router.post(
    "/",
    response_model=PropertyResponse,
    status_code=201,
)
def create_property(
    property_data: PropertyCreate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO properties (
                    property_name,
                    address,
                    property_type
                )
                VALUES (%s, %s, %s)
                RETURNING
                    id,
                    property_name,
                    address,
                    property_type,
                    created_at;
                """,
                (
                    property_data.property_name,
                    property_data.address,
                    property_data.property_type,
                ),
            )

            row = cursor.fetchone()

            connection.commit()

            return {
                "id": row[0],
                "property_name": row[1],
                "address": row[2],
                "property_type": row[3],
                "created_at": row[4],
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)

# =========================================================
# DASHBOARD SUMMARY
#
# IMPORTANT:
# This route must remain ABOVE /{property_id}
# =========================================================

@router.get("/dashboard-summary")
def get_dashboard_summary():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM properties
                    ) AS properties_count,

                    (
                        SELECT COUNT(*)
                        FROM units
                    ) AS units_count,

                    (
                        SELECT COUNT(*)
                        FROM tenants
                    ) AS tenants_count,

                    (
                        SELECT COUNT(*)
                        FROM maintenance_requests
                        WHERE status = 'Open'
                    ) AS open_maintenance,

                    (
                        SELECT COUNT(*)
                        FROM maintenance_requests
                        WHERE status = 'In Progress'
                    ) AS in_progress_maintenance,

                    (
                        SELECT COUNT(*)
                        FROM maintenance_requests
                        WHERE status = 'Resolved'
                    ) AS resolved_maintenance,

                    (
                        SELECT COUNT(*)
                        FROM rent_records
                        WHERE payment_status = 'Paid'
                    ) AS paid_rent,

                    (
                        SELECT COUNT(*)
                        FROM rent_records
                        WHERE payment_status = 'Partial'
                    ) AS partial_rent,

                    (
                        SELECT COUNT(*)
                        FROM rent_records
                        WHERE payment_status = 'Pending'
                    ) AS pending_rent,

                    (
                        SELECT COALESCE(
                            SUM(rent_amount - amount_paid),
                            0
                        )
                        FROM rent_records
                    ) AS outstanding_rent;
                """
            )

            row = cursor.fetchone()

            return {
                "properties_count": row[0],
                "units_count": row[1],
                "tenants_count": row[2],
                "maintenance": {
                    "open": row[3],
                    "in_progress": row[4],
                    "resolved": row[5],
                },
                "rent": {
                    "paid": row[6],
                    "partial": row[7],
                    "pending": row[8],
                    "outstanding": row[9],
                },
            }

    finally:
        release_connection(connection)
# =========================================================
# PROPERTY OVERVIEW
#
# IMPORTANT:
# This route must remain ABOVE /{property_id}
# =========================================================

@router.get("/{property_id}/overview")
def get_property_overview(property_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # -------------------------------------------------
            # Property
            # -------------------------------------------------
            cursor.execute(
                """
                SELECT
                    id,
                    property_name,
                    address,
                    property_type,
                    created_at
                FROM properties
                WHERE id = %s;
                """,
                (property_id,),
            )

            property_row = cursor.fetchone()

            if property_row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Property not found",
                )

            # -------------------------------------------------
            # Units
            # -------------------------------------------------
            cursor.execute(
                """
                SELECT
                    id,
                    property_id,
                    unit_name,
                    created_at
                FROM units
                WHERE property_id = %s
                ORDER BY id;
                """,
                (property_id,),
            )

            unit_rows = cursor.fetchall()

            units = [
                {
                    "id": row[0],
                    "property_id": row[1],
                    "unit_name": row[2],
                    "created_at": row[3],
                }
                for row in unit_rows
            ]

            unit_ids = [
                row[0]
                for row in unit_rows
            ]

            # -------------------------------------------------
            # Tenants
            # -------------------------------------------------
            tenants = []

            if unit_ids:
                cursor.execute(
                    """
                    SELECT
                        id,
                        unit_id,
                        name,
                        email,
                        phone,
                        created_at
                    FROM tenants
                    WHERE unit_id = ANY(%s)
                    ORDER BY id;
                    """,
                    (unit_ids,),
                )

                tenant_rows = cursor.fetchall()

                tenants = [
                    {
                        "id": row[0],
                        "unit_id": row[1],
                        "name": row[2],
                        "email": row[3],
                        "phone": row[4],
                        "created_at": row[5],
                    }
                    for row in tenant_rows
                ]

            # -------------------------------------------------
            # Inspections
            # -------------------------------------------------
            inspections = []

            if unit_ids:
                cursor.execute(
                    """
                    SELECT
                        id,
                        unit_id,
                        inspection_type,
                        inspection_date,
                        inspector,
                        condition_notes,
                        flagged_issue,
                        created_at
                    FROM inspections
                    WHERE unit_id = ANY(%s)
                    ORDER BY inspection_date DESC, id DESC;
                    """,
                    (unit_ids,),
                )

                inspection_rows = cursor.fetchall()

                inspections = [
                    {
                        "id": row[0],
                        "unit_id": row[1],
                        "inspection_type": row[2],
                        "inspection_date": row[3],
                        "inspector": row[4],
                        "condition_notes": row[5],
                        "flagged_issue": row[6],
                        "created_at": row[7],
                    }
                    for row in inspection_rows
                ]

            # -------------------------------------------------
            # Maintenance
            # -------------------------------------------------
            maintenance = []

            if unit_ids:
                cursor.execute(
                    """
                    SELECT
                        id,
                        unit_id,
                        inspection_id,
                        description,
                        reported_by,
                        priority,
                        assigned_contractor,
                        status,
                        created_at,
                        resolved_at,
                        resolution_notes
                    FROM maintenance_requests
                    WHERE unit_id = ANY(%s)
                    ORDER BY created_at DESC, id DESC;
                    """,
                    (unit_ids,),
                )

                maintenance_rows = cursor.fetchall()

                maintenance = [
                    {
                        "id": row[0],
                        "unit_id": row[1],
                        "inspection_id": row[2],
                        "description": row[3],
                        "reported_by": row[4],
                        "priority": row[5],
                        "assigned_contractor": row[6],
                        "status": row[7],
                        "created_at": row[8],
                        "resolved_at": row[9],
                        "resolution_notes": row[10],
                    }
                    for row in maintenance_rows
                ]

            # -------------------------------------------------
            # Rent
            # -------------------------------------------------
            rent = []

            if unit_ids:
                cursor.execute(
                    """
                    SELECT
                        id,
                        unit_id,
                        tenant_id,
                        rent_amount,
                        due_date,
                        amount_paid,
                        payment_date,
                        payment_status,
                        notes,
                        created_at
                    FROM rent_records
                    WHERE unit_id = ANY(%s)
                    ORDER BY due_date DESC, id DESC;
                    """,
                    (unit_ids,),
                )

                rent_rows = cursor.fetchall()

                rent = [
                    {
                        "id": row[0],
                        "unit_id": row[1],
                        "tenant_id": row[2],
                        "rent_amount": row[3],
                        "due_date": row[4],
                        "amount_paid": row[5],
                        "payment_date": row[6],
                        "payment_status": row[7],
                        "notes": row[8],
                        "created_at": row[9],
                    }
                    for row in rent_rows
                ]

            return {
                "property": {
                    "id": property_row[0],
                    "property_name": property_row[1],
                    "address": property_row[2],
                    "property_type": property_row[3],
                    "created_at": property_row[4],
                },
                "units": units,
                "tenants": tenants,
                "inspections": inspections,
                "maintenance": maintenance,
                "rent": rent,
            }

    finally:
        release_connection(connection)


# =========================================================
# GET ONE PROPERTY
# =========================================================

@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
)
def get_property(property_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    property_name,
                    address,
                    property_type,
                    created_at
                FROM properties
                WHERE id = %s;
                """,
                (property_id,),
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Property not found",
                )

            return {
                "id": row[0],
                "property_name": row[1],
                "address": row[2],
                "property_type": row[3],
                "created_at": row[4],
            }

    finally:
        release_connection(connection)