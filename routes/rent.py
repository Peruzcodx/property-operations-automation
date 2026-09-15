from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
)

from database import (
    get_connection,
    release_connection,
)

from schemas.rent import (
    RentCreate,
    RentUpdate,
    RentResponse,
)


router = APIRouter(
    prefix="/rent",
    tags=["Rent"],
)


# =========================================================
# GET ALL RENT RECORDS
# =========================================================

@router.get(
    "/",
    response_model=List[RentResponse],
)
def get_rent_records():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                ORDER BY due_date DESC, id DESC;
                """
            )

            rows = cursor.fetchall()

            return [
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
                for row in rows
            ]

    finally:
        release_connection(connection)


# =========================================================
# CREATE RENT RECORD
# =========================================================

@router.post(
    "/",
    response_model=RentResponse,
    status_code=201,
)
def create_rent_record(
    rent_data: RentCreate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO rent_records (
                    unit_id,
                    tenant_id,
                    rent_amount,
                    due_date,
                    amount_paid,
                    payment_date,
                    payment_status,
                    notes
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING
                    id,
                    unit_id,
                    tenant_id,
                    rent_amount,
                    due_date,
                    amount_paid,
                    payment_date,
                    payment_status,
                    notes,
                    created_at;
                """,
                (
                    rent_data.unit_id,
                    rent_data.tenant_id,
                    rent_data.rent_amount,
                    rent_data.due_date,
                    rent_data.amount_paid,
                    rent_data.payment_date,
                    (
                        "Paid"
                        if rent_data.amount_paid
                        >= rent_data.rent_amount
                        else (
                            "Partial"
                            if rent_data.amount_paid > 0
                            else "Pending"
                        )
                    ),
                    rent_data.notes,
                ),
            )

            row = cursor.fetchone()

            connection.commit()

            return {
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

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)


# =========================================================
# UPDATE RENT PAYMENT
# =========================================================

@router.patch(
    "/{rent_id}",
    response_model=RentResponse,
)
def update_rent_record(
    rent_id: int,
    rent_data: RentUpdate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE rent_records
                SET
                    amount_paid = COALESCE(
                        %s,
                        amount_paid
                    ),
                    payment_date = COALESCE(
                        %s,
                        payment_date
                    ),
                    payment_status = CASE
                        WHEN COALESCE(
                            %s,
                            amount_paid
                        ) >= rent_amount
                            THEN 'Paid'

                        WHEN COALESCE(
                            %s,
                            amount_paid
                        ) > 0
                            THEN 'Partial'

                        ELSE 'Pending'
                    END,
                    notes = COALESCE(
                        %s,
                        notes
                    )
                WHERE id = %s
                RETURNING
                    id,
                    unit_id,
                    tenant_id,
                    rent_amount,
                    due_date,
                    amount_paid,
                    payment_date,
                    payment_status,
                    notes,
                    created_at;
                """,
                (
                    rent_data.amount_paid,
                    rent_data.payment_date,
                    rent_data.amount_paid,
                    rent_data.amount_paid,
                    rent_data.notes,
                    rent_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Rent record not found",
                )

            connection.commit()

            return {
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

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)