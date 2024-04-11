from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from clothes_app import models, serializers, utils


@swagger_auto_schema(
    method="get",
)
@api_view(http_method_names=["GET"])
@permission_classes([AllowAny])
def home(request: Request) -> Response:
    return Response({"message": "OK"}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="GET",
    operation_summary="Получить предупреждения для пользователя/пользователей",
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


@swagger_auto_schema(
    method="GET",
    operation_summary="Получить данные о человеке по идентификатору",
    manual_parameters=[
        openapi.Parameter(
            name="person_id",
            in_=openapi.IN_QUERY,
            required=True,
            type=openapi.TYPE_INTEGER,
            description="Идентификатор человека, для которого требуется получить данные.",
        ),
    ],
    responses={
        200: openapi.Response(
            "Данные о человеке успешно получены",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Идентификатор человека.",
                    ),
                    "cloth_title": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Название одежды.",
                    ),
                    "cloth_category": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Категория одежды.",
                    ),
                    "date_of_start": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATE,
                        description="Дата начала использования одежды (гггг-мм-дд).",
                    ),
                    "end_date_of_wearing": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATE,
                        description="Дата окончания использования одежды (гггг-мм-дд).",
                    ),
                    "period_in_days": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Период использования в днях.",
                    ),
                    "first_name": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Имя человека.",
                    ),
                    "last_name": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Фамилия человека.",
                    ),
                    "patranomic": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Отчество человека.",
                    ),
                },
            ),
        ),
        404: openapi.Response(
            "Данные не найдены",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке, указывающее на то, что данные не найдены.",
                    )
                },
            ),
        ),
        500: openapi.Response(
            "Внутренняя ошибка сервера",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке сервера.",
                    )
                },
            ),
        ),
    },
    operation_description="Получает данные о человеке по его идентификатору.",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_person_data_by_id(request):
    person_id = request.GET.get("person_id", None)
    try:
        if person_id is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Person id is required"},
            )

        query = "SELECT * FROM public.get_cloth_info(%s);"
        result = utils.execute_query(query, params=[person_id], fetch=True)
        if result is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Empty"},
            )

        formatted_result = {
            "id": result[0],
            "cloth_title": result[1],
            "cloth_category": result[2],
            "date_of_start": result[3].strftime("%Y-%m-%d"),
            "end_date_of_wearing": result[4].strftime("%Y-%m-%d"),
            "period_in_days": result[5],
            "first_name": result[6],
            "last_name": result[7],
            "patranomic": result[8],
        }
        return Response(status=status.HTTP_200_OK, data=formatted_result)

    except Exception as e:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"message": str(e)})


@swagger_auto_schema(
    method="DELETE",
    operation_summary="Удалить одежду по идентификатору",
    manual_parameters=[
        openapi.Parameter(
            name="cloth_to_delete",
            in_=openapi.IN_QUERY,
            required=True,
            type=openapi.TYPE_INTEGER,
            description="Идентификатор одежды, которую требуется удалить.",
        ),
    ],
    responses={
        200: openapi.Response(
            "Одежда успешно удалена",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение о успешном удалении одежды.",
                    )
                },
            ),
        ),
        500: openapi.Response(
            "Ошибка на стороне сервера",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение с информацией об ошибке.",
                    )
                },
            ),
        ),
    },
    operation_description="Удаляет одежду по её идентификатору.",
)
@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_clothes(request):
    cloth_to_delete = request.GET.get("cloth_to_delete", None)
    try:
        if cloth_to_delete is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Clothe Id is required"},
            )
        query = "CALL delete_clothes(%s);"
        utils.execute_query(query, params=[cloth_to_delete])

        return Response(status=status.HTTP_200_OK, data={"message": "Deleted"})
    except Exception as e:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"message": str(e)}
        )


@swagger_auto_schema(
    method="POST",
    operation_summary="Добавить новую одежду",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["cloth_title", "cloth_category", "cloth_slug", "period_in_days"],
        properties={
            "cloth_title": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Название одежды.",
            ),
            "cloth_category": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Категория одежды.",
            ),
            "cloth_slug": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Код одежды.",
            ),
            "period_in_days": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Период использования в днях.",
            ),
            "description": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Описание одежды (опционально).",
            ),
        },
    ),
    responses={
        201: openapi.Response(
            "Одежда успешно добавлена",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение о успешном добавлении одежды.",
                    )
                },
            ),
        ),
        400: openapi.Response(
            "Ошибка в запросе",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке в запросе.",
                    )
                },
            ),
        ),
        500: openapi.Response(
            "Внутренняя ошибка сервера",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке сервера.",
                    )
                },
            ),
        ),
    },
    operation_description="Добавляет новую одежду с указанными параметрами.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def insert_new_clothe(request):
    cloth_title = request.data.get("cloth_title", None)
    cloth_category = request.data.get("cloth_category", None)
    cloth_slug = request.data.get("cloth_slug", None)
    period_in_days = request.data.get("period_in_days", None)
    description = request.data.get("description", None)

    if not all([cloth_title, cloth_category, cloth_slug, period_in_days]):
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "All fields are required"},
        )
    try:
        query = "CALL create_clothes((%s,%s,%s,%s,%s));"
        result = utils.execute_query(
            query,
            params=(
                str(cloth_title),
                str(cloth_category),
                str(cloth_slug).lower(),
                int(period_in_days),
                str(description),
            ),
            commit=True,
        )

        if result == -1:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"message": "Failed to insert data into the database"},
            )

        return Response(status=status.HTTP_201_CREATED, data={"message": "Success"})
    except Exception as e:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"message": str(e)}
        )


@swagger_auto_schema(
    method="PUT",
    operation_summary="Обновление данных пользователя одежды",
    manual_parameters=[
        openapi.Parameter(
            "clothes_id",
            openapi.IN_QUERY,
            description="Идентификатор одежды",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            "person_id",
            openapi.IN_QUERY,
            description="Идентификатор пользователя",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            "date_started_wearing",
            openapi.IN_QUERY,
            description="Дата начала ношения (ГГГГ-ММ-ДД)",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "date_ended_wearing",
            openapi.IN_QUERY,
            description="Дата окончания ношения (ГГГГ-ММ-ДД)",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            "Успешно",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об успешном обновлении данных",
                    )
                },
            ),
        ),
        400: openapi.Response(
            "Неверный запрос",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке в запросе",
                    )
                },
            ),
        ),
        500: openapi.Response(
            "Внутренняя ошибка сервера",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Сообщение об ошибке на сервере",
                    )
                },
            ),
        ),
    },
)
@api_view(["PUT"])
@permission_classes([AllowAny])
def update_clothe(request):
    clothes_id = request.GET.get("clothes_id", None)
    person_id = request.GET.get("person_id", None)
    date_started_wearing = request.GET.get("date_started_wearing", None)
    date_ended_wearing = request.GET.get("date_started_wearing", None)

    if not all([clothes_id, person_id, date_started_wearing, date_ended_wearing]):
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "All fields are required"},
        )
    try:
        query = "CALL update_clothes_user (%s,%s,%s,%s);"

        result = utils.execute_query(
            query,
            params=(
                int(clothes_id),
                int(person_id),
                date_started_wearing,
                date_ended_wearing,
            ),
            commit=True,
        )

        if result == -1:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"message": "Failed to Update data into the database"},
            )
        return Response(status=status.HTTP_200_OK, data={"message": "Success"})
    except Exception as e:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"message": str(e)}
        )
