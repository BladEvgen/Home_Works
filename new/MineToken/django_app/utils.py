import re
from rest_framework.response import Response
from rest_framework import status
from .models import Token


def password_check(password: str) -> bool:
    return (
        True
        if re.match(
            r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{10,}$",
            password,
        )
        is not None
        else False
    )


def username_check(username: str) -> bool:
    return (
        True
        if re.match(r"^(?=.*?[A-Za-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{4,}$", username)
        is not None
        else False
    )


def auth_required(func):
    def wrapper(request, *args, **kwargs):
        token_str = request.query_params.get("token", "") or request.data.get(
            "token", ""
        )
        if not token_str:
            return Response(
                data={"error": "Token not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = Token.objects.get(token=token_str)
        except Token.DoesNotExist:
            return Response(
                data={"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if token.is_expired():
            return Response(
                data={"error": "Token expired"}, status=status.HTTP_401_UNAUTHORIZED
            )

        request.user = token.user
        return func(request, *args, **kwargs)

    return wrapper
