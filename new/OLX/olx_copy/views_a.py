import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from olx_copy import models
from django.core.exceptions import ObjectDoesNotExist


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.token = self.scope["query_string"].decode("utf-8").split("=")[1]

        # Validate the token before connecting
        if not await self.is_valid_token():
            await self.close()
            return

        self.room_group_name = f"chat_online_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: bytes):
        data = json.loads(text_data)
        username = data["username"]
        room = data["room"]
        message = data["message"]

        await self.save_message(username, room, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
                "room": room,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        room = event["room"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "room": room,
                }
            )
        )

    @database_sync_to_async
    def is_valid_token(self):
        try:
            room = models.Room.objects.get(slug=self.room_name)
            return room.token == self.token
        except ObjectDoesNotExist:
            return False

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = models.Room.objects.get(slug=room)

        models.Message.objects.create(user=user, room=room, content=str(message))
