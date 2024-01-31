import sqlite3
import os
from django.http import JsonResponse
from datetime import datetime


class Utils:
    @staticmethod
    def get_database_path(database_filename, source_folder="database"):
        base_path = os.path.abspath(
            os.path.join("django_digital_home", "desktop", "src", source_folder)
        )
        return os.path.join(base_path, database_filename)

    @staticmethod
    def get_current_timestamp():
        return datetime.now()


def auth_paramaterized_decorator(_token: str = ""):
    def decor(func):
        def wrapper(*args, **kwargs):
            if args[0].headers.get("Authorization", "") != _token:
                return JsonResponse(data={"error": "Not valid token"}, status=401)
            try:
                _response: dict = func(*args, **kwargs)
                return JsonResponse(data=_response, status=200)
            except Exception as error:
                Utils.save_error_to_db(str(error))
                return JsonResponse(data={"error": str(error)}, status=500)

        return wrapper

    return decor


class Sql:
    @staticmethod
    def table_init():
        with Sql.connect_db(Utils.get_database_path("local_settings.db")) as connection:
            Sql.execute_query(
                connection,
                """
                CREATE TABLE IF NOT EXISTS params (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL DEFAULT ''
                );
                """,
            )

    @staticmethod
    def save_error_to_db(error_message: str):
        try:
            with Sql.connect_db(Utils.get_database_path("error_log.db")) as connection:
                Sql.execute_query(
                    connection,
                    """
                    INSERT INTO error_log (timestamp, message)
                    VALUES (?, ?);
                    """,
                    (datetime.now(), error_message),
                )
        except Exception as db_error:
            print(f"Database error while saving error log: {db_error}")

    @staticmethod
    def sql_execute(_query: str, _kwargs: dict, _source: str):
        try:
            with Sql.connect_db(Utils.get_database_path(_source)) as connection:
                return Sql.execute_query(connection, _query, _kwargs)
        except Exception as error:
            Utils.save_error_to_db(str(error))
            return None

    @staticmethod
    def connect_db(db_path):
        return sqlite3.connect(db_path)

    @staticmethod
    def execute_query(connection, query, parameters=None):
        with connection:
            cursor = connection.cursor()
            cursor.execute(query, parameters)
            return cursor.fetchall()
