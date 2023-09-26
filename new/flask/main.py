import datetime
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
    template_folder="templates",
)

class View:
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/faqs")
    def faqs():
        return render_template("faqs.html")

    @app.route("/add_vacancy", methods=["GET", "POST"])
    def add_vacancy():
        if request.method == "POST":
            name = str(request.form.get("name"))
            title = str(request.form.get("title"))
            location = str(request.form.get("location"))
            iin = str(request.form.get("iin"))
            description = str(request.form.get("description"))
            salary = float(request.form.get("salary"))
            date_posted = request.form.get("date_posted")

            DatabaseTools.insert_vacancy(
                name, title, location,iin, description, salary, date_posted
            )

            return redirect(url_for("candidates"))

        return render_template("add_vacancy.html")

    @app.route("/candidates")
    def candidates():
        candidates = DatabaseTools.query("SELECT * FROM vacancies")
        return render_template("candidates.html", candidates=candidates)


class DatabaseTools:
    @staticmethod
    def get_db_path():
        db_folder = os.path.join(os.path.dirname(__file__), "db")
        os.makedirs(db_folder, exist_ok=True)
        return os.path.join(db_folder, "database.db")

    @staticmethod
    def drop_table():
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS vacancies")
    
    @staticmethod
    def create_db():
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT,
                    location TEXT,
                    iin INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    salary REAL,
                    date_posted DATE
                );
                """
            )
    @staticmethod
    def convert_iin(iin: str):
        if isinstance(iin, int):
            return iin
        if isinstance(iin, str):
            try:
                iin = int(iin)
            except Exception as e:
                iin = 0
                print(str(e))
            return iin
    @staticmethod
    def insert_vacancy(
        name: str,
        title: str,
        location: str,
        iin: int | str,
        description: str,
        salary: int | float,
        date_posted: str,
    ):
        iin = DatabaseTools.convert_iin(iin) 
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            query_str = """
                INSERT INTO vacancies (name, title, location, iin, description, salary, date_posted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            vacancy_data = (name, title, location, iin, description, salary, date_posted)
            cursor.execute(query_str, vacancy_data)


    @staticmethod
    def update_vacancy_by_id(
        vacancy_id: int,
        name: str,
        title: str,
        location: str,
        iin: int,
        description: str,
        salary: int | float,
        date_posted: str,
    ):
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            query_str = """
                UPDATE vacancies
                SET name = ?, title = ?, location = ?, iin = ?, description = ?, salary = ?, date_posted = ?
                WHERE id = ?
            """
            vacancy_data = (
                name,
                title,
                location,
                iin,
                description,
                salary,
                date_posted,
                vacancy_id,
            )
            cursor.execute(query_str, vacancy_data)

    @staticmethod
    def query(query_str: str, args=(), many=True) -> list | None:
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(query_str, args)
            try:
                if many:
                    return cursor.fetchall()
                return cursor.fetchone()
            except sqlite3.Error as error:
                print(f"Error with sqlite3 connection {str(error)}")
                return None
            except Exception as error:
                print(f"Oop something went wrong {str(error)}")
                return None
            

DatabaseTools.drop_table()
DatabaseTools.create_db()
DatabaseTools.insert_vacancy(
    name="Leonid",
    title="Front-end Developer",
    location="New York",
    iin = "012345678912",  # str value for checking function to convert to int
    description="Skilled Front-end Developer.",
    salary=80000.0,
    date_posted=datetime.datetime.now().strftime("%Y-%m-%d"),
)
DatabaseTools.insert_vacancy(
    name="Kirill",
    title="Data Scientist",
    location="San Francisco",
    iin = 550033771199,  # int value
    description="Data Science loves to work on exciting projects.",
    salary=95000.0,
    date_posted=datetime.datetime.now().strftime("%Y-%m-%d"),
)
DatabaseTools.insert_vacancy(
    name="Alexander",
    title="Accountant",
    location="Detroit",
    iin = "978060102033",
    description="Detail-oriented Accountant.",
    salary=56000.0,
    date_posted=datetime.datetime.now().strftime("%Y-%m-%d"),
)


if __name__ == "__main__":
    app.run(debug=True)
