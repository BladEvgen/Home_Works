from django.core.cache import caches
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from contracts import models, serializers

Cache = caches["default"]


def get_cache(
    key: str, query: callable = lambda: any, timeout: int = 10, cache: any = Cache
) -> any:
    data = cache.get(key)
    if data is None:
        data = query()
        cache.set(key, data, timeout)
    return data


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
        contracts = models.Contract.objects.all()
        serializer = serializers.ContractSerializer(contracts, many=True)
        return Response({"data": serializer.data})
    elif request.method == "POST":
        try:
            agent_id = request.data.get("agent_id")
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


@api_view(["GET", "POST"])
def agents_detail(request, id=None) -> Response:
    try:
        if request.method == "GET":
            if id is None:
                agents = models.Contragent.objects.all()
                serialized_agents = [
                    {"id": agent.id, "bin": agent.bin, "title": agent.title}
                    for agent in agents
                ]
                return Response({"data": serialized_agents}, status=status.HTTP_200_OK)

            else:
                agent = models.Contragent.objects.get(pk=id)
                serialized_agent = {
                    "id": agent.id,
                    "bin": agent.bin,
                    "title": agent.title,
                }
                return Response({"data": serialized_agent}, status=status.HTTP_200_OK)

        elif request.method == "POST":
            bin = request.data.get("bin")
            title = request.data.get("title")
            if bin and title:
                agent = models.Contragent.objects.create(bin=bin, title=title)
                serialized_agent = {
                    "id": agent.id,
                    "bin": agent.bin,
                    "title": agent.title,
                }
                return Response(
                    {"data": serialized_agent}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"message": "bin and title are required fields"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    except models.Contragent.DoesNotExist:
        return Response(
            {"message": "Agent does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return Response(
            {"message": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
