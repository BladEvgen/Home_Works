import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django_app import models


@api_view(http_method_names=["GET"])
def home(request: Request):
    try:
        param_date_from = request.GET.get("param_date_from")
        param_date_to = request.GET.get("param_date_to")

        if param_date_from and param_date_to:
            date_format = "%m-%d-%Y"
            param_date_from = datetime.datetime.strptime(param_date_from, date_format)
            param_date_to = datetime.datetime.strptime(param_date_to, date_format)
            if param_date_to < param_date_from:
                return Response(
                    data={"message": "End date cannot be before start date."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            today = datetime.datetime.today()
            param_date_from = today.replace(day=1)
            param_date_to = param_date_from.replace(
                month=param_date_from.month + 1, day=1
            )

        filter_date = models.Sale.objects.filter(
            date__gte=param_date_from, date__lte=param_date_to
        )

        data_1 = {}

        for sale in filter_date:
            month_key = sale.date.strftime("%Y-%m")
            shop_key = sale.shop.name
            category_key = sale.product.category

            if month_key not in data_1:
                data_1[month_key] = {}

            if shop_key not in data_1[month_key]:
                data_1[month_key][shop_key] = {}

            if category_key not in data_1[month_key][shop_key]:
                data_1[month_key][shop_key][category_key] = 0

            old_totalPrice = (
                data_1.get(month_key, {}).get(shop_key, {}).get(category_key, 0)
            )
            data_1[month_key][shop_key][category_key] = (
                old_totalPrice + sale.quantity * sale.price
            )

        data_2 = []

        for month, shops in data_1.items():
            for shop, categories in shops.items():
                sladosti = categories.get("сладости", 0)
                other = categories.get("другое", 0)
                hleb = categories.get("хлеб", 0)
                data_2.append([month, shop, sladosti, other, hleb])

        data_2 = sorted(data_2, key=lambda x: (x[0], x[1]))

        return Response(data={"message": data_2}, status=status.HTTP_200_OK)

    except (ValueError, TypeError) as e:
        return Response(
            data={"error": f"Invalid date format or parameter: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
