import datetime
import json
import sys
import threading
import time
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication
import sqlite3
import requests


class Utils:
    HOST = "127.0.0.1"
    PORT = 8000

    class Query:
        @staticmethod
        def create_table_params() -> str:
            return """
                CREATE TABLE IF NOT EXISTS params (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL DEFAULT ''
                );"""

        @staticmethod
        def get_all_params() -> str:
            return """
            SELECT key, value 
            FROM params
            ;"""

        @staticmethod
        def get_insert_or_replace_params() -> str:
            return """
                INSERT OR REPLACE 
                INTO params
                    (key, value)
                VALUES
                    (:key, :value)
                ;"""

    @staticmethod
    def sql_execute(_query: str, _kwargs: dict, _source: str):
        try:
            with sqlite3.connect(
                f"django_digital_home/desktop/src/database/{_source}"
            ) as _connection:
                _connection.execute(_query, _kwargs)
                _data = _connection.execute(Utils.Query.get_all_params()).fetchall()
            return _data
        except Exception as error:
            print(error)
            return None

    @staticmethod
    def database_init():
        Utils.sql_execute(
            _query=Utils.Query.create_table_params(),
            _kwargs={},
            _source="local_settings.db",
        )

    @staticmethod
    def sync_settings_to_web():
        
        _rows = Utils.sql_execute(
            _query=Utils.Query.get_all_params(),
            _kwargs={},
            _source="local_settings.db",
        )
        if _rows is not None:
            _params = dict((str(x[0]), str(x[1])) for x in _rows)
            try:
                _response = requests.post(
                    url=f"http://{Utils.HOST}:{Utils.PORT}/api/settings/set/",
                    headers={"Authorization": "Token=auth1234"},
                    data=json.dumps({"id": "970801", "params": _params}),
                )
                if _response.status_code not in (200, 201):
                    raise Exception(f"WEB ERROR {_response.status_code}")
            except Exception as error:
                # print(error)
                pass

    @staticmethod
    def sync_settings_from_web():
        try:
            _response = requests.get(
                f"http://{Utils.HOST}:{Utils.PORT}/api/settings/get/",
                headers={"Authorization": "Token=auth123"},
            )
            if _response.status_code not in (200, 201):
                raise Exception(f"WEB ERROR {_response.status_code}")
            _data = _response.json().get("data", {})
            for k, v in _data.items():
                Utils.sql_execute(
                    _query=Utils.Query.get_insert_or_replace_params(),
                    _kwargs={"key": str(k), "value": str(v)},
                    _source="local_settings.db",
                )
        except Exception as error:
            print(error)

    @staticmethod
    def loop(target: callable, args: tuple, delay: float | int, prefix: str):
        while True:
            try:
                threading.Thread(target=target, args=args, daemon=True).start()
            except Exception as error:
                print(f"{datetime.datetime.now()} {prefix}:", error)
            time.sleep(delay)


class Ui(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("django_digital_home/desktop/src/main.ui", self)
        self.__params = {}

        self.ui.pushButton_temp_plan_plus.clicked.connect(
            self.push_button_temp_plan_plus
        )
        self.ui.pushButton_temp_plan_minus.clicked.connect(
            self.push_button_temp_plan_minus
        )

        self.show()
        threading.Thread(target=self.loop, daemon=True).start()

    def push_button_temp_plan(self, delta):
        _rows = Utils.sql_execute(
            _query=Utils.Query.get_all_params(),
            _kwargs={},
            _source="local_settings.db",
        )
        if _rows is not None:
            _params = dict((str(x[0]), str(x[1])) for x in _rows)
            for key in ["temp_plan_high", "temp_plan_down"]:
                _params[key] = str(int(_params.get(key, -7)) + delta)
            for k, v in _params.items():
                Utils.sql_execute(
                    _query=Utils.Query.get_insert_or_replace_params(),
                    _kwargs={"key": str(k), "value": str(v)},
                    _source="local_settings.db",
                )
            threading.Thread(target=Utils.sync_settings_to_web, daemon=True).start()

    def push_button_temp_plan_plus(self):
        self.push_button_temp_plan(1)

    def push_button_temp_plan_minus(self):
        self.push_button_temp_plan(-1)

    def update_ui_from_local_settings(self):
        _rows = Utils.sql_execute(
            _query=Utils.Query.get_all_params(),
            _kwargs={},
            _source="local_settings.db",
        )
        if _rows is not None:
            _params = dict((str(x[0]), str(x[1])) for x in _rows)
            self.__params["temp_plan_high"] = int(_params.get("temp_plan_high", -7))
            self.__params["temp_plan_down"] = int(_params.get("temp_plan_down", -20))
            self.ui.label_temp_plan_high.setText(str(self.__params["temp_plan_high"]))
            self.ui.label_temp_plan_down.setText(str(self.__params["temp_plan_down"]))

    def loop(self):
        Utils.loop(
            self.update_ui_from_local_settings, (), 0.1, "update_ui_from_local_settings"
        )
        # web syncing is disabled 
        # Utils.loop(Utils.sync_settings_from_web, (), 3.0, "Utils.sync_settings_from_web")


if __name__ == "__main__":
    Utils.database_init()
    app = QApplication(sys.argv)
    ui = Ui()
    sys.exit(app.exec())
