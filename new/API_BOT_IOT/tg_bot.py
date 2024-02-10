import sqlite3
import requests
import time
import json
import signal
from contextlib import contextmanager
from datetime import datetime

from telegram import Bot, Update
from telegram.ext import (
    CommandHandler,
    Updater,
    CallbackContext,
    MessageHandler,
    Filters,
)

with open("tg_config.json") as config_file:
    config = json.load(config_file)

TOKEN = config.get("telegram_bot_token")
bot = Bot(token=TOKEN)

API_URL = f"http://{config['ip']}:{config['port']}/api/sent_messages/"


@contextmanager
def db_connect():
    conn = sqlite3.connect("subscriptions.db")
    try:
        yield conn
    finally:
        conn.close()


def create_tables():
    with db_connect() as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, subscribed BOOLEAN)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS errors
                     (timestamp TIMESTAMP, error TEXT)"""
        )
        conn.commit()


def log_error(error_msg):
    with db_connect() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO errors (timestamp, error) VALUES (?, ?)",
            (datetime.now(), error_msg),
        )
        conn.commit()


def send_message():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        message = format_message(data)
        send_to_subscribers(message)
    except requests.exceptions.RequestException as e:
        error_msg = f"Error occurred: {str(e)}"
        print(error_msg)
        log_error(error_msg)


def format_message(data):
    formatted_data = []
    for item in data["data"]:
        status = "Работает" if item["is_working"] else "Не работает"
        formatted_data.append(
            f"Серийный номер: {item['device_id']}\n"
            f"- Статус: {status}\n"
            f"- Уровень топлива: {item['fuel']} L\n"
            f"- Скорость: {item['speed']} Km/h\n"
        )

    no_network_devices = []
    for device in data["no_network_data"]:
        no_network_devices.append(
            f"- Серийный номер: {device['id']} \n (Время последнего подключения: {device['last_seen_time']})"
        )

    message = "\n\n".join(formatted_data)
    if no_network_devices:
        message += "\n\nУстройства без подключения к сети:\n" + "\n".join(
            no_network_devices
        )

    message += "\n\nЧтобы отписаться от рассылки, используйте команду /unsubscribe."

    return message


def send_to_subscribers(message):
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM subscriptions WHERE subscribed = 1")
        subscribed_users = c.fetchall()

    for user_id in subscribed_users:
        bot.send_message(chat_id=user_id[0], text=message)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Привет! Используйте /subscribe, чтобы подписаться на рассылку новостей. Используйте /unsubscribe, чтобы отписаться."
    )


def subscribe(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Чтобы подписаться, отправьте пароль.")


def password_verification(update: Update, context: CallbackContext) -> None:
    password = update.message.text
    if password == "Qwerty1234!!":
        user_id = update.message.from_user.id
        with db_connect() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO subscriptions (user_id, subscribed) VALUES (?, ?)",
                (user_id, 1),
            )
            conn.commit()
        update.message.reply_text("Вы подписались на рассылку новостей.")
    else:
        update.message.reply_text("Неверный пароль. Попробуйте снова.")
        print("Incorrect password.")


def unsubscribe(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT subscribed FROM subscriptions WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        if result and result[0] == 1:
            c.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
            conn.commit()
            update.message.reply_text("Вы отписались от рассылки новостей.")
            print("Unsubscription successful.")
        else:
            update.message.reply_text("Вы не подписаны на рассылку новостей.")


def stop_program(signal, frame):
    global cycle
    print("Stopping program...")
    cycle = False
    updater.stop()
    print("Program stopped.")
    exit(0)


def main():
    create_tables()

    global updater
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, password_verification)
    )

    updater.start_polling()

    cycle = True
    try:
        while cycle:
            send_message()
            time.sleep(5)
    except KeyboardInterrupt:
        stop_program(signal.SIGINT, None)


if __name__ == "__main__":
    main()
