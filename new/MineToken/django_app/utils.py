import re
import sqlite3


def execute_sqlite(database: str, query: str, kwargs={}):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(query, kwargs)
        connection.commit()
        return cursor.fetchall()


create_table = """
    CREATE TABLE IF NOT EXISTS Token (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        token  TEXT UNIQUE,
        created_at TEXT
    );

"""
create_user_table = """
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    );
"""


insert_user = """
    INSERT INTO User (username, password) VALUES ('Evgen_1', 'Evgen_12345678')

"""
try:
    execute_sqlite(
        database=r"D:\Github_Code\Python\project\token.db", query=create_table
    )
    execute_sqlite(
        database=r"D:\Github_Code\Python\project\token.db", query=create_user_table
    )
    # execute_sqlite(
    #     database=r"D:\Github_Code\Python\project\token.db", query=insert_user
    # )
    print("Successful execute_sqlite")
except Exception as e:
    print("Error: ", str(e))


def password_check(password: str) -> bool:
    return (
        True
        if re.match(
            r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{12,}$",
            password,
        )
        is not None
        else False
    )


def username_check(username: str) -> bool:
    return (
        True
        if re.match(
            r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{4,}$", username
        )
        is not None
        else False
    )
