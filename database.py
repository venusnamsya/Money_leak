import sqlite3
import hashlib


DATABASE_NAME = "moneyleak.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS merchant_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                merchant TEXT NOT NULL,
                category TEXT NOT NULL,

                UNIQUE(user_id, merchant),

                FOREIGN KEY (user_id)
                REFERENCES users(id)
            )
        """)

        # Migration for older MoneyLeak databases
        columns = connection.execute(
            "PRAGMA table_info(transactions)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "user_id" not in column_names:

            connection.execute("""
                ALTER TABLE transactions
                ADD COLUMN user_id INTEGER
            """)


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def create_user(name, email, password):

    email = email.strip().lower()

    try:

        with get_connection() as connection:

            cursor = connection.execute("""
                INSERT INTO users
                (name, email, password)

                VALUES (?, ?, ?)
            """, (
                name.strip(),
                email,
                hash_password(password)
            ))

            return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None


def authenticate_user(email, password):

    email = email.strip().lower()

    with get_connection() as connection:

        user = connection.execute("""
            SELECT id, name, email

            FROM users

            WHERE email = ?
            AND password = ?
        """, (
            email,
            hash_password(password)
        )).fetchone()

        if user:
            return dict(user)

        return None


def add_transaction(
    user_id,
    date,
    description,
    amount,
    category
):

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO transactions
            (
                user_id,
                date,
                description,
                amount,
                category
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            date,
            description,
            amount,
            category
        ))

        return cursor.lastrowid


def get_transactions(user_id):

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT
                id,
                date,
                description,
                amount,
                category

            FROM transactions

            WHERE user_id = ?

            ORDER BY date DESC, id DESC
        """, (user_id,)).fetchall()

        return [
            dict(row)
            for row in rows
        ]


def delete_transaction(
    transaction_id,
    user_id
):

    with get_connection() as connection:

        cursor = connection.execute("""
            DELETE FROM transactions

            WHERE id = ?
            AND user_id = ?
        """, (
            transaction_id,
            user_id
        ))

        return cursor.rowcount > 0


def update_category(
    transaction_id,
    user_id,
    category
):

    with get_connection() as connection:

        cursor = connection.execute("""
            UPDATE transactions

            SET category = ?

            WHERE id = ?
            AND user_id = ?
        """, (
            category,
            transaction_id,
            user_id
        ))

        return cursor.rowcount > 0


def save_merchant_category(
    user_id,
    merchant,
    category
):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO merchant_categories
            (
                user_id,
                merchant,
                category
            )

            VALUES (?, ?, ?)

            ON CONFLICT(user_id, merchant)

            DO UPDATE SET
                category = excluded.category
        """, (
            user_id,
            merchant.lower().strip(),
            category
        ))


def get_merchant_category(
    user_id,
    merchant
):

    with get_connection() as connection:

        row = connection.execute("""
            SELECT category

            FROM merchant_categories

            WHERE user_id = ?
            AND merchant = ?
        """, (
            user_id,
            merchant.lower().strip()
        )).fetchone()

        if row:
            return row["category"]

        return None