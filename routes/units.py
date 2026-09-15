from typing import List

from fastapi import APIRouter

from database import (
    get_connection,
    release_connection,
)

from schemas.unit import (
    UnitCreate,
    UnitResponse,
)


router = APIRouter(
    prefix="/units",
    tags=["Units"],
)


# =========================================================
# GET ALL UNITS
# =========================================================

@router.get(
    "/",
    response_model=List[UnitResponse],
)
def get_units():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    property_id,
                    unit_name,
                    created_at
                FROM units
                ORDER BY id;
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "property_id": row[1],
                    "unit_name": row[2],
                    "created_at": row[3],
                }
                for row in rows
            ]

    finally:
        release_connection(connection)


# =========================================================
# CREATE UNIT
# =========================================================

@router.post(
    "/",
    response_model=UnitResponse,
    status_code=201,
)
def create_unit(
    unit_data: UnitCreate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO units (
                    property_id,
                    unit_name
                )
                VALUES (%s, %s)
                RETURNING
                    id,
                    property_id,
                    unit_name,
                    created_at;
                """,
                (
                    unit_data.property_id,
                    unit_data.unit_name,
                ),
            )

            row = cursor.fetchone()

            connection.commit()

            return {
                "id": row[0],
                "property_id": row[1],
                "unit_name": row[2],
                "created_at": row[3],
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)