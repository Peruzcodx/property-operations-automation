from typing import List

from fastapi import APIRouter

from database import (
    get_connection,
    release_connection,
)

from schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
)


router = APIRouter(
    prefix="/inspections",
    tags=["Inspections"],
)


# =========================================================
# GET ALL INSPECTIONS
# =========================================================

@router.get(
    "/",
    response_model=List[InspectionResponse],
)
def get_inspections():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                ORDER BY inspection_date DESC, id DESC;
                """
            )

            rows = cursor.fetchall()

            return [
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
                for row in rows
            ]

    finally:
        release_connection(connection)


# =========================================================
# CREATE INSPECTION
# =========================================================

@router.post(
    "/",
    response_model=InspectionResponse,
    status_code=201,
)
def create_inspection(
    inspection_data: InspectionCreate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inspections (
                    unit_id,
                    inspection_type,
                    inspection_date,
                    inspector,
                    condition_notes,
                    flagged_issue
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    unit_id,
                    inspection_type,
                    inspection_date,
                    inspector,
                    condition_notes,
                    flagged_issue,
                    created_at;
                """,
                (
                    inspection_data.unit_id,
                    inspection_data.inspection_type,
                    inspection_data.inspection_date,
                    inspection_data.inspector,
                    inspection_data.condition_notes,
                    inspection_data.flagged_issue,
                ),
            )

            row = cursor.fetchone()

            connection.commit()

            return {
                "id": row[0],
                "unit_id": row[1],
                "inspection_type": row[2],
                "inspection_date": row[3],
                "inspector": row[4],
                "condition_notes": row[5],
                "flagged_issue": row[6],
                "created_at": row[7],
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)