import django
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from channels.layers import get_channel_layer
from ..models import ChatMessage, ChatRoom, User
from ..utils.utils import get_room_id, create_message
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("REQUEST KELDI==============")
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()

    async def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        command = message["command"]
        self.room_id = await get_room_id(message["from"],message["to"])
        self.room_group_name = "chat_%s" % self.room_id
        # match message["command"]:
        if message["command"] == "join":
            await self.join_room(self.room_id)
        elif message["command"] == "send":
            await self.send_room(message,self.room_id)
        elif message["command"] == "leave":
            await self.leave_room(self.room_id)

    async def disconnect(self,close_code):
        await self.leave_room(self.room_id)

    async def join_room(self,room_id):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.join",
                "room_id": room_id
            }
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def leave_room(self,room_id):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.leave",
                "room_id": room_id,
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def send_room(self,message,room_id):
        data = await create_message(message["from"],message["to"],message["message"],room_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":"chat.message",
                "message": data,
                "room_id": room_id,
            }
        )

    async def chat_join(self,event):
        pass

    async def chat_leave(self,event):
        pass

    async def chat_message(self,event):
        message = event["message"]

        await self.send(text_data=json.dumps({
            "message": message,
        }))

class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anon or self.scope["user"].is_authenticated:
            self.video_data = []
            await self.accept()
        else:
            await self.close()
   
    async def receive(self,text_data=None, bytes_data=None):
        self.streamer_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.live_room_name = "stream_%s" % self.streamer_id
        self.user_id = self.scope["user"].id
        if str(self.user_id) == self.streamer_id:
            await self.send(json.dumps({"is_streamer": True}))
        else:
            await self.send(json.dumps({"is_streamer": False}))
        if bytes_data is not None:
            self.video_data.append(bytes_data)
            with open(f"./media/video_streams/{self.user_id}.webm","wb") as f:
                for d in self.video_data:
                    f.write(d)
                    await self.send(json.dumps({"streaming_data":d}))
        
