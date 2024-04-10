from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from clothes_app import models, serializers


@api_view(http_method_names=["GET"])
@permission_classes([AllowAny])
def home(request: Request) -> Response:
    return Response({"message": "OK"}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="GET",
    operation_summary="Получить предупреждения для пользователя",
    manual_parameters=[
        openapi.Parameter(
            name="user_id",
            in_=openapi.IN_QUERY,
            required=False,
            type=openapi.TYPE_INTEGER,
            description="ID пользователя, для которого требуется получить предупреждения.",
        ),
    ],
    responses={
        200: openapi.Response(
            "Предупреждения успешно получены",
            openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "tabel_id": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Табельный номер пользователя.",
                        ),
                        "person_full_name": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Полное имя человека.",
                        ),
                        "clothes_category": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Категория одежды.",
                        ),
                        "clothes_name": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Наименование одежды.",
                        ),
                        "remaining_days": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Оставшиеся дни.",
                        ),
                    },
                ),
            ),
        ),
        404: openapi.Response(
            "Пользователь не найден",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке, указывающее на то, что пользователь не найден.",
                    )
                },
            ),
        ),
        500: openapi.Response(
            "Внутренняя ошибка сервера",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке сервера.",
                    )
                },
            ),
        ),
    },
    operation_description="Получает предупреждения для пользователя. Если указан `user_id`, то получаются предупреждения именно для этого пользователя; в противном случае получаются предупреждения для всех пользователей.",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def warning_messages(request):
    user_id = request.query_params.get("user_id", None)
    if user_id:
        try:
            person = models.Person.objects.get(pk=user_id)
            clothes_users = models.ClothesUser.objects.filter(person=person)
            serializer = serializers.ClothesUserSerializer(clothes_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Person.DoesNotExist:
            return Response(
                {"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        clothes_users = models.ClothesUser.objects.all()
        serializer = serializers.ClothesUserSerializer(clothes_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
