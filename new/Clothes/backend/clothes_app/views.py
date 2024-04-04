from django.contrib.auth.models import User
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
