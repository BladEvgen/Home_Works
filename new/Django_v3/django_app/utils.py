import requests
import datetime
import sqlite3
from pathlib import Path
from time import perf_counter
from bs4 import BeautifulSoup
from django.http import HttpRequest
from django.shortcuts import render

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    "authority": "store.playstation.com",
    "sec-ch-ua-platform": '"Windows"',
}

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "database.db"


class Database:
    def __init__(self, database_path: str):
        self.database_path = database_path

    def query(
        self,
        query_str: str,
        args: tuple = (),
        many: bool = True,
        commit: bool = False,
    ) -> list | None:
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(query_str, args)
            try:
                if many:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
                if commit:
                    connection.commit()
                return result
            except Exception as error:
                print(f"Error executing query {str(error)} ")
                return None


def create_tables():
    db = Database(DB_PATH)

    query_str = """
        CREATE TABLE IF NOT EXISTS error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_description TEXT,
            datetime TEXT,
            route TEXT
        )
    """
    db.query(query_str, commit=True)

    query_str = """
        CREATE TABLE IF NOT EXISTS performance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            route TEXT,
            datetime TEXT,
            elapsed_time REAL
        )
    """
    db.query(query_str, commit=True)


def decorator_error_handler(view_func):
    create_tables()

    def wrapper(request, *args, **kwargs):
        start_time = perf_counter()
        db = Database(DB_PATH)
        current_time = datetime.datetime.now()

        try:
            response = view_func(request, *args, **kwargs)
        except Exception as error:
            error_message = str(error)
            route = request.path

            with open("logs.log", "a") as log_file:
                log_file.write(
                    f"{current_time} ERROR {request.path}: {error_message}\n"
                )

            query_str = "INSERT INTO error_log (error_description, datetime, route) VALUES (?, ?, ?)"
            db.query(query_str, (error_message, current_time, route), commit=True)

            return render(
                request, "error.html", {"error_message": error_message}, status=500
            )
        else:
            return response
        finally:
            end_time = perf_counter()
            elapsed_time = end_time - start_time

            username = (
                request.user.username
                if request.user.is_authenticated
                else "Anonymous_user"
            )
            formatted_datetime = current_time.strftime("%H:%M:%S %d-%m-%Y")
            with open("click.txt", "a") as click_file:
                click_file.write(
                    f'{formatted_datetime} Username: "{username}" clicked on "{request.path}" (elapsed time: {round(elapsed_time, 5)} seconds)\n'
                )

            query_str = "INSERT INTO performance_log (username, route, datetime, elapsed_time) VALUES (?, ?, ?, ?)"
            db.query(
                query_str,
                (username, request.path, formatted_datetime, elapsed_time),
                commit=True,
            )

    return wrapper


def api_request(data: dict, res_type: any):
    response = requests.post("http://127.0.0.1:8001/api", json=data)
    return response.json().get("result", res_type)


def get_exchange_data():
    url = "https://www.mig.kz/"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    exchange_data = soup.find("ul", class_="clearfix").find_all("li")

    currencies = ["USD", "EUR", "RUB", "KGS", "GBP", "CNY", "GOLD"]

    result_data = [
        (currencies[i], exchange_data[i].text.strip()) for i in range(len(currencies))
    ]

    return result_data
