from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from contracts import models, serializers


@api_view(http_method_names=["GET"])
def home(request) -> Response:
    return Response(
        data={"data": "Ok"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@csrf_exempt
def contracts(request):
    if request.method == "GET":
        paginator = PageNumberPagination()
        paginator.page_size = 3
        contracts = models.Contract.objects.all()
        result_page = paginator.paginate_queryset(contracts, request)
        serializer = serializers.ContractSerializer(result_page, many=True)
        return paginator.get_paginated_response({"data": serializer.data})
    elif request.method == "POST":
        try:
            agent_id = request.data.get("agent")
            total = request.data.get("total")
            comment_text = request.data.get("comment")
            file = request.FILES.get("file")

            agent: models.Contragent = get_object_or_404(models.Contragent, pk=agent_id)
            comment: models.Comment = models.Comment.objects.create(
                comment=comment_text
            )
            contract: models.Contract = models.Contract.objects.create(
                agent=agent,
                total=total,
                comment=comment,
                file=file,
            )

            response_data = {"data": {"id": contract.id, "status": "Created"}}
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
