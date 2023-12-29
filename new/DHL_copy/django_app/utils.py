import datetime
import random
import sqlite3
from django.shortcuts import render
from .models import Price


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


def decorator_error_handler(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            response = view_func(request, *args, **kwargs)
        except Exception as error:
            print(f"{datetime.datetime.now()} ERROR {request.path}")
            # TODO: error log - логи ошибок создавать файл, с записью в каждый час
            return render(
                request, "error.html", {"error_message": str(error)}, status=500
            )
        else:
            return response
        finally:
            # TODO: action log - логи действий(переходы, клики...)
            pass

    return wrapper


def generate_random_prices():
    delivery_types = ["Local Delivery", "International Delivery", "Express Delivery"]

    descriptions = [
        "Fast and reliable delivery within the city.",
        "International shipping with tracking and insurance.",
        "Priority delivery for urgent shipments.",
    ]

    # Price.objects.all().delete()

    for _ in range(100):
        name = random.choice(delivery_types)
        description = random.choice(descriptions)

        if name == "Local Delivery":
            price = random.randint(1000, 10000)
        elif name == "International Delivery":
            price = random.randint(10000, 100000)
        else:
            price = random.randint(5000, 20000)

        Price.objects.create(name=name, description=description, price=price)
