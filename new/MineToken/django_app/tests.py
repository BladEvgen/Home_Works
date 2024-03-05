from django.test import TestCase
import requests

# Create your tests here.


def tests():
    try:
        response = requests.get("http://localhost:8000/api/user/list/")
        print(response, response.status_code)
        print(response.json())
        if response.status_code not in [201, 200]:
            raise Exception("123")

    except:
        print("УСПЕХ")

    try:
        data: dict[str, str] = {"username": "Evgen_12", "password": "Evgen_12345678"}
        response = requests.post("http://localhost:8000/api/token/", data)
        print(response, response.status_code)
        print(response.json())
        if response.status_code not in [201, 200]:
            raise Exception("123")
    except:
        print("Успех token на не правильного")
    token = ""
    try:
        data: dict[str, str] = {"username": "Evgen_1", "password": "Evgen_12345678"}
        response = requests.post("http://localhost:8000/api/token/", data)
        print(response, response.status_code)
        print(response.json())
        if response.status_code not in [201, 200]:
            raise Exception("123")
        token = response.json()["token"]
        print("Успех в отсутсвии ошибки token на правильного")
    except:
        print("не успех")

    try:
        response = requests.get(f"http://localhost:8000/api/token/check/?token={token}")
        print(response, response.status_code)
        if response.status_code in [201, 200]:
            print("Успешно check")
    except:
        print("Ошибка check")

    try:
        response = requests.get(f"http://localhost:8000/api/user/list/?token={token}")
        print(response, response.status_code)
        print(response.json())

        if response.status_code not in [201, 200]:
            raise Exception("123")
        print("УСПЕХ list")
    except:
        print("Не УСПЕХ list")

    try:
        data = {"token": token}
        response = requests.post("http://localhost:8000/api/token/block/", data)
        print(response, response.status_code)
        print(response.json())
        if response.status_code not in [201, 200]:
            raise Exception("123")
        print("TOKEN BLOCKED УСПЕХ")
    except:
        print("НЕ УСПЕх TOKEN BLOCKED ")

    try:
        response = requests.get(f"http://localhost:8000/api/user/list/?token={token}")
        print(response, response.status_code)
        print(response.json())

        if response.status_code not in [201, 200]:
            raise Exception("123")
        print("УСПЕХ list")
    except:
        print("Не УСПЕХ list")


tests()
