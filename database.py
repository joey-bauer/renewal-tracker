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

def get_account_by_id(account_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, account_name, renewal_date, created_at
        FROM accounts
        WHERE id = ?
        """,
        (account_id,)
    )

    account = cursor.fetchone()

    connection.close()

    return account

def account_exists(account_name):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM accounts
        WHERE LOWER(account_name) = LOWER(?)
        LIMIT 1
        """,
        (account_name,)
    )

    account = cursor.fetchone()

    connection.close()

    return account is not None


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

def add_custom_task(account_id, task_name, due_date):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks(
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
            due_date.isoformat(),
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

def delete_account(account_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE account_id = ?
        """,
        (account_id,)
    )

    cursor.execute(
        """
        DELETE FROM accounts
        WHERE id = ?
        """,
        (account_id,)
    )

    connection.commit()
    connection.close()

def delete_task(task_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    connection.commit()
    connection.close()

def update_task_status(task_id, new_status):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        """,
        (
            new_status,
            task_id
        )
    )

    connection.commit()
    connection.close()