import sqlite3

DATABASE_NAME = "renewal_tracker.db"


def initialize_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            renewal_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Not Started',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)

    connection.commit()
    connection.close()


def add_account(account_name, renewal_date):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO accounts (account_name, renewal_date)
        VALUES (?, ?)
        """,
        (
            account_name,
            renewal_date.isoformat()
        )
    )

    account_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return account_id


def get_all_accounts():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, account_name, renewal_date, created_at
        FROM accounts
        ORDER BY renewal_date
        """
    )

    accounts = cursor.fetchall()

    connection.close()

    return accounts


def add_tasks(account_id, renewal_tasks):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    for task_name, task_date in renewal_tasks:
        cursor.execute(
            """
            INSERT INTO tasks (
                account_id,
                task_name,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                account_id,
                task_name,
                task_date.isoformat(),
                "Not Started"
            )
        )

    connection.commit()
    connection.close()

def get_tasks_for_account(account_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, task_name, due_date, status
        FROM tasks
        WHERE account_id = ?
        ORDER BY due_date
        """,
        (account_id,)
    )

    tasks = cursor.fetchall()

    connection.close()

    return tasks