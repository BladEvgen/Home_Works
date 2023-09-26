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
            title = request.form.get("title")
            company = request.form.get("company")
            location = request.form.get("location")
            description = request.form.get("description")
            salary = float(request.form.get("salary"))
            date_posted = request.form.get("date_posted")

            DatabaseTools.insert_vacancy(
                title, company, location, description, salary, date_posted
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
                    title TEXT NOT NULL,
                    company TEXT,
                    location TEXT,
                    description TEXT NOT NULL,
                    salary REAL,
                    date_posted DATE
                );
                """
            )

    @staticmethod
    def insert_vacancy(
        title: str,
        company: str,
        location: str,
        description: str,
        salary: int | float,
        date_posted: str,
    ):
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            query_str = """
                INSERT INTO vacancies (title, company, location, description, salary, date_posted)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            vacancy_data = (title, company, location, description, salary, date_posted)
            cursor.execute(query_str, vacancy_data)

    @staticmethod
    def update_vacancy_by_id(
        vacancy_id: int,
        title: str,
        company: str,
        location: str,
        description: str,
        salary: int | float,
        date_posted: str,
    ):
        db_path = DatabaseTools.get_db_path()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            query_str = """
                UPDATE vacancies
                SET title = ?, company = ?, location = ?, description = ?, salary = ?, date_posted = ?
                WHERE id = ?
            """
            vacancy_data = (
                title,
                company,
                location,
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
            
def main():
    DatabaseTools.drop_table()
    DatabaseTools.create_db()
    DatabaseTools.insert_vacancy(
        title="Front-end Developer",
        company="ABC Company",
        location="New York",
        description="We are looking for a skilled Front-end Developer to join our team.",
        salary=80000.0,
        date_posted=datetime.datetime.now().strftime("%Y-%m-%d"),
    )
    DatabaseTools.insert_vacancy(
        title="Data Scientist",
        company="XYZ Corporation",
        location="San Francisco",
        description="Join our Data Science team and work on exciting projects.",
        salary=95000.0,
        date_posted=datetime.datetime.now().strftime("%Y-%m-%d"),
    )


if __name__ == "__main__":
    main()
    app.run(debug=True)
