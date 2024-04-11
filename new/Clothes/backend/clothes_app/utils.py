from django.db import connection


def execute_query(query, params=None, fetch=False, many=False, commit=False):
    try:
        cursor = connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)

        if commit:
            connection.commit()

        if fetch:
            if many:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
        else:
            return None
    except Exception as e:
        print(str(e))
        return -1
