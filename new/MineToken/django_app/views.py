import datetime
import random

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from django_app import utils
from django_settings import settings

"""
{
    "username": "Evgen_1",
    "password": "Evgen_12345678"
} 

{"token":
    "gegvev1vn_E_enggnv111eEg1E_nn1eg1nE11nvE_vvvg1geEegevgEeeve_vEvn_1vEvn_1_1evv_ng1E___E_e_1Evn1gvE___1ng1e1ven_vnEEee1_Eg1v1EggE_"
}
"""


# TODO переписать на ORM
# Create your views here.
@api_view(http_method_names=["POST"])
def token(request: Request):
    # Получение данных и запроса
    username = request.data.get("username", None)
    password = request.data.get("password", None)
    # Валидация данных
    if not utils.password_check(password) or not utils.username_check(username):
        return Response(data={"error": "Invalid"}, status=status.HTTP_401_UNAUTHORIZED)
    # Проверяем существует пользователь ли
    user = utils.execute_sqlite(
        database=r"D:\Github_Code\Python\project\token.db",
        query="SELECT id, username FROM User WHERE username = :username AND password = :password",
        kwargs={"username": username, "password": password},
    )
    # Ошибка при отстуствии пользователя
    if len(user) <= 0:
        return Response(
            data={"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    user_id, username = user[0]

    # Создания Хэша для пользователя
    hash: str = ""
    for _ in range(1, 129):
        hash += random.choice(username)

    # Создание токена для конкретного пользователя, и возрват
    utils.execute_sqlite(
        database=r"D:\Github_Code\Python\project\token.db",
        query="INSERT OR REPLACE INTO Token (user_id,token,created_at) VALUES (:user_id,:token,:created_at)",
        kwargs={
            "user_id": user_id,
            "token": hash,
            "created_at": str(datetime.datetime.now()),
        },
    )
    return Response(data={"token": hash})


def auth(func):
    def wrapper(*args, **kwargs):
        request: Request = args[0]
        token_str = request.query_params.get("token", "")
        if not token_str:
            token_str = request.data.get("token", "")
        token = utils.execute_sqlite(
            database=r"D:\Github_Code\Python\project\token.db",
            query="SELECT user_id, created_at FROM Token WHERE token = :token",
            kwargs={
                "token": token_str,
            },
        )
        if len(token) <= 0:
            return Response(
                data={"error": "Invalid TOKEN"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user_id, created_at = token[0]

        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f")
        if (
            datetime.datetime.now()
            - datetime.timedelta(minutes=settings.TOKEN_LIFE_TIME_IN_MINUTES)
        ) > created_at:
            return Response(
                data={"error": "Token Expired"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user = utils.execute_sqlite(
            database=r"D:\Github_Code\Python\project\token.db",
            query="SELECT username FROM User WHERE id = :user_id",
            kwargs={"user_id": user_id},
        )
        if len(user) <= 0:
            return Response(
                data={"error": "User Unknown"}, status=status.HTTP_401_UNAUTHORIZED
            )
        request.userxtend = user
        args = (request,)
        response = func(*args, **kwargs)

        return response

    return wrapper


@api_view(http_method_names=["GET"])
@auth
def user_list(request: Request):

    return Response(data={"data": [request.userxtend[0]]})


@api_view(http_method_names=["POST"])
def token_block(request: Request):
    token_to_block_str = request.data.get("token", "")
    utils.execute_sqlite(
        database=r"D:\Github_Code\Python\project\token.db",
        query="Delete from Token where token = :token_to_block_str",
        kwargs={
            "token_to_block_str": token_to_block_str,
        },
    )
    return Response(data={"data": "successfully deleted"}, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@auth
def token_verify(request: Request):
    return Response(data={"data": "success verified"}, status=status.HTTP_200_OK)
