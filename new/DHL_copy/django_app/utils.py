import datetime
import random
from django.shortcuts import render
from .models import Price

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    "authority": "store.playstation.com",
    "sec-ch-ua-platform": '"Windows"',
}


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

    Price.objects.all().delete()

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
