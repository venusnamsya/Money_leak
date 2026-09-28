import sqlite3

DATABASE_NAME = "moneyleak.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL
            )
        """)


def add_transaction(date, description, amount, category):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO transactions
                (date, description, amount, category)
            VALUES (?, ?, ?, ?)
        """, (date, description, amount, category))

        return cursor.lastrowid


def get_transactions():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, date, description, amount, category
            FROM transactions
            ORDER BY date DESC, id DESC
        """).fetchall()

        return [tuple(row) for row in rows]


def delete_transaction(transaction_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

        return cursor.rowcount > 0


def update_category(transaction_id, new_category):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE transactions
            SET category = ?
            WHERE id = ?
        """, (new_category, transaction_id))

        return cursor.rowcount > 0


def clear_transactions():
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM transactions"
        )

        return cursor.rowcount