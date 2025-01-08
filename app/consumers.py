import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom  # Assuming you have a ChatRoom model

logger = logging.getLogger(__name__)

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("ChatRoomConsumer: connect")
        self.chat_box_name = self.scope["url_route"]["kwargs"]["chat_box_name"]
        self.group_name = "chat_%s" % self.chat_box_name

        # Ensure the chat room exists
        await self.ensure_chat_room_exists(self.chat_box_name)

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"ChatRoomConsumer: disconnect {close_code}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info(f"ChatRoomConsumer: receive {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chatbox_message",
                "message": message,
                "username": username,
            },
        )

    async def chatbox_message(self, event):
        logger.info(f"ChatRoomConsumer: chatbox_message {event}")
        message = event["message"]
        username = event["username"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                }
            )
        )

    @database_sync_to_async
    def ensure_chat_room_exists(self, chat_box_name):
        if not ChatRoom.objects.filter(name=chat_box_name).exists():
            ChatRoom.objects.create(name=chat_box_name)
