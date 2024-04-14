import datetime

from sanic import Sanic, response
from sanic_ext import openapi
from utils import db_query_tool, make_exception

app = Sanic("CrudAPP")


@make_exception
@app.delete("/delete_clothes")
@openapi.parameter(
    "cloth_to_delete",
    required=True,
    location="query",
    type="integer",
    description="The ID of the cloth to delete",
)
@openapi.response(
    200,
    {"application/json": {"description": "Success message after cloth deletion"}},
    description="Cloth deleted successfully",
)
@openapi.response(
    404,
    {"application/json": {"description": "Error message for missing cloth ID"}},
    description="Cloth ID is required",
)
@openapi.response(
    400,
    {"application/json": {"description": "Cloth Id must be an integer"}},
    description="Cloth ID is not Integer",
)
@openapi.response(
    500,
    {"application/json": {"description": "Error message for internal server error"}},
    description="Internal Server Error",
)
async def delete_clothes(request):
    cloth_to_delete = request.args.get("cloth_to_delete")
    try:
        if cloth_to_delete is None:
            return response.json({"message": "Cloth Id is required"}, status=404)
        try:
            cloth_to_delete = int(cloth_to_delete)
        except ValueError:
            return response.json({"message": "Cloth Id must be an integer"}, status=400)
        query = "CALL delete_clothes($1);"
        await db_query_tool(query, "DELETE", cloth_to_delete)

        return response.json({"message": "Deleted"}, status=200)
    except Exception as e:
        return response.json({"message": str(e)}, status=500)


@make_exception
@app.post("/insert_new_clothe")
@openapi.body(
    {
        "application/json": {
            "required": [
                "cloth_title",
                "cloth_category",
                "cloth_slug",
                "period_in_days",
            ],
            "type": "object",
            "properties": {
                "cloth_title": {"type": "string", "description": "Title of the cloth"},
                "cloth_category": {
                    "type": "string",
                    "description": "Category of the cloth",
                },
                "cloth_slug": {
                    "type": "string",
                    "description": "Unique slug for the cloth",
                },
                "period_in_days": {
                    "type": "integer",
                    "description": "Period in days for the cloth",
                },
                "description": {
                    "type": "string",
                    "description": "Description of the cloth (optional)",
                },
            },
        }
    }
)
@openapi.response(
    201,
    {"application/json": {"description": "Success message after cloth insertion"}},
    description="Cloth inserted successfully",
)
@openapi.response(
    400,
    {"application/json": {"description": "Error message for missing fields"}},
    description="All fields are required",
)
@openapi.response(
    500,
    {"application/json": {"description": "Error message for internal server error"}},
    description="Internal Server Error",
)
async def insert_new_clothe(request):
    cloth_title = request.json.get("cloth_title", None)
    cloth_category = request.json.get("cloth_category", None)
    cloth_slug = request.json.get("cloth_slug", None)
    period_in_days = request.json.get("period_in_days", None)
    description = request.json.get("description", None)

    if not all([cloth_title, cloth_category, cloth_slug, period_in_days]):
        raise response.json(data={"message": "All fields are required"}, status=400)

    try:
        query = "CALL create_clothes(($1,$2,$3,$4,$5));"
        await db_query_tool(
            query,
            "POST",
            str(cloth_title),
            str(cloth_category),
            str(cloth_slug).lower(),
            int(period_in_days),
            str(description),
        )

        return response.json({"message": "Success"}, status=201)

    except Exception as e:
        return response.json({"message": str(e)}, status=500)


@make_exception
@app.put("/update_clothe")
@openapi.parameter(
    name="clothes_id",
    required=True,
    type="integer",
    description="The ID of the clothes to update",
)
@openapi.parameter(
    name="person_id",
    required=True,
    type="integer",
    description="The ID of the person wearing the clothes",
)
@openapi.parameter(
    name="date_started_wearing",
    required=True,
    type="string",
    description="The date the person started wearing the clothes (format: YYYY-MM-DD)",
)
@openapi.parameter(
    name="date_ended_wearing",
    required=True,
    type="string",
    description="The date the person ended wearing the clothes (format: YYYY-MM-DD)",
)
@openapi.response(
    200,
    {"application/json": {"description": "Success message after cloth update"}},
    description="Clothes user association updated successfully",
)
@openapi.response(
    400,
    {"application/json": {"description": "Error message for missing fields"}},
    description="All fields are required",
)
@openapi.response(
    500,
    {"application/json": {"description": "Error message for internal server error"}},
    description="Internal Server Error",
)
async def update_clothe(request):
    clothes_id = request.args.get("clothes_id")
    person_id = request.args.get("person_id")
    date_started_wearing = request.args.get("date_started_wearing")
    date_ended_wearing = request.args.get("date_ended_wearing")

    if not all([clothes_id, person_id, date_started_wearing, date_ended_wearing]):
        return response.json({"message": "All fields are required"}, status=400)
    try:
        date_started_wearing = datetime.datetime.strptime(
            date_started_wearing, "%Y-%m-%d"
        ).date()
        date_ended_wearing = datetime.datetime.strptime(
            date_ended_wearing, "%Y-%m-%d"
        ).date()

        query = "CALL update_clothes_user ($1, $2, $3, $4);"
        method = "PUT"
        await db_query_tool(
            query,
            method,
            int(clothes_id),
            int(person_id),
            date_started_wearing,
            date_ended_wearing,
        )

        return response.json({"message": "Success"}, status=200)
    except Exception as e:
        return response.json({"message": str(e)}, status=500)


@make_exception
@app.get("/get_person_data")
@openapi.parameter(
    name="person_id",
    required=True,
    type="integer",
    description="The ID of the person to retrieve data for",
)
@openapi.response(
    200,
    {"application/json": {"description": "List of clothes data for the person"}},
    description="Person data retrieved successfully",
)
@openapi.response(
    400,
    {"application/json": {"description": "Error message for invalid person ID"}},
    description="Person ID must be an integer",
)
@openapi.response(
    404,
    {"application/json": {"description": "Error message for person not found"}},
    description="Person with the given ID not found",
)
@openapi.response(
    500,
    {"application/json": {"description": "Error message for internal server error"}},
    description="Internal Server Error",
)
async def get_person_data_by_id(request):
    person_id = request.args.get("person_id", None)
    try:
        if person_id is None:
            return response.json(
                status=404,
                data={"message": "Person id is required"},
            )
        try:
            person_id = int(person_id)
        except ValueError:
            return response.json(
                {"message": "Person Id must be an integer"}, status=400
            )
        query = "SELECT * FROM get_cloth_info($1);"
        method = "GET"
        result = await db_query_tool(query, method, person_id, fetch=True)

        if not result:
            return response.json(
                status=404,
                data={"message": "Empty"},
            )

        result_dict = [dict(row) for row in result]

        for row in result_dict:
            for key, value in row.items():
                if isinstance(value, datetime.date):
                    row[key] = str(value)

        return response.json(status=200, body=result_dict)

    except Exception as e:

        return response.json(status=500, data={"message": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, fast=True, auto_reload=True)
