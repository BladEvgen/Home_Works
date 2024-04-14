from functools import wraps
from database.db_conf import connect_to_database
from sanic import response


async def db_query_tool(query, method, *args, fetch=False):
    connection = await connect_to_database()
    try:
        if method == "GET":
            if fetch:
                return await connection.fetch(query, *args)
            else:
                return await connection.fetch(query)
        else:
            await connection.execute(query, *args)
    except Exception as e:
        return {"message": str(e)}
    finally:
        await connection.close()


def make_exception(func):
    @wraps
    async def wrapper(*args, **kwargs):
        try:
            original = func(*args, **kwargs)
            return await original
        except Exception as e:
            return response.json({"message": str(e)}, status=500)

    return wrapper
