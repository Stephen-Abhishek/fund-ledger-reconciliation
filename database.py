import sqlite3
import pandas as pd

DB_NAME = "fund_operations.db"


def create_database():
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_name TEXT NOT NULL,
            review_status TEXT NOT NULL,
            reviewer_notes TEXT,
            review_time TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_review(transaction_name, review_status, reviewer_notes):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO audit_log (
            transaction_name,
            review_status,
            reviewer_notes,
            review_time
        )
        VALUES (?, ?, ?, ?)
    """, (
        transaction_name,
        review_status,
        reviewer_notes,
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_audit_logs():
    connection = sqlite3.connect(DB_NAME)

    audit_df = pd.read_sql_query(
        "SELECT * FROM audit_log ORDER BY id DESC",
        connection
    )

    connection.close()

    return audit_df


if __name__ == "__main__":
    create_database()
    print("Database functions are ready!")