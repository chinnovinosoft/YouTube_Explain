# 3) Python: fetch latest booking by phone
import psycopg2
from psycopg2.extras import RealDictCursor

def get_latest_booking_by_phone(host: str,
                                port: int,
                                dbname: str,
                                user: str,
                                password: str,
                                phone: str):
    """
    Connects to Postgres and returns the most recent booking record
    for the given phone number, or None if not found.
    """
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT room_number, check_out, price_per_night
                FROM booking_details
                WHERE phone = %s
                ORDER BY check_in DESC
                LIMIT 1
            """, (phone,))
            return cur.fetchone()
    finally:
        conn.close()


