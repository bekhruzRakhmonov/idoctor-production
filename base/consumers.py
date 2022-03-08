import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from channels.layers import get_channel_layer
from .models import ChatMessage, ChatRoom, User
from .utils.utils import get_room_id, create_message
import datetime

class ChatConsumer(AsyncWebsocketConsumer):

	async def connect(self):
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
		match message["command"]:
			case "join":
				await self.join_room(self.room_id)
			case "send":
				await self.send_room(message,self.room_id)
			case "leave":
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

