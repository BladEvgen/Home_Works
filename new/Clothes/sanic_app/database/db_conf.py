import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


async def connect_to_database():
    try:
        return await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise


async def disconnect_from_database(connection):
    await connection.close()
