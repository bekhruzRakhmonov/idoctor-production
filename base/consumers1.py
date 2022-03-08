import json
from channels.generic.websocket import WebsocketConsumer
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatMessage, ChatRoom, User
import datetime

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_anonymous:
            self.close()
        else:
            self.accept()
            self.rooms = set()
            self.room_id = None
            
            """
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = "chat_%s" % self.room_name
            print(self.room_group_name)
            print(self.channel_name)
            print(self.channel_layer)
            print(self.channel_receive)
            
            """

    def disconnect(self, close_code):
        print(close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.from_ = User.objects.get(email=message["from"])
        self.to = User.objects.get(email=message["to"])
        try:
            self.room_id = ChatRoom.get_room_id(self.from_,self.to)
            print("This is a ChatRoom: ",self.room_id)
        except ChatRoom.DoesNotExist:
            self.room_id = ChatRoom.create_room_id(self.from_,self.to)
        self.room_group_name = "chat_%s" % self.room_id
        print(self.room_group_name)
        command = message["command"]
        match command:
            case "join":
                return self.join_room(message)
            case "leave":
                return self.leave_room(message["room_id"])
            case "send":
                return self.send_room(message)
        status = message["status"]
        from_ = User.objects.get(email=message["from"])
        to = User.objects.get(email=message["to"])

        if status:
            from_.status = True
            from_.save()
        else:
            from_.status = False
            from_.save()

    def join_room(self,message):
        print("User is joined to CHAT ROOM")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.join",
                "room_id": message["room_id"]
            }
        )
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.send(text_data=json.dumps(
            {
                "message": message
            }
        ))

    def leave_room(self,room_id):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.leave",
                "room_id": room_id
            }
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )
        
        self.send(json.dumps({
            "leave": str(room_id)
        }))
    
    def send_room(self,message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message
            }
        )
    
    def chat_join(self,event):
        print("Event: ",event)
        self.send(text_data=json.dumps({
            "message": "User is joined to CHAT ROOM"
        }))
      
    def chat_message(self, event):
        print("CHAT MESSAGE")
        message = event["message"]
        _from, _to = User.objects.get(email=message["from"]),User.objects.get(email=message["to"])
        if len(message["message"]) > 0:
            messages = ChatMessage.create(outgoing=_from,incoming=_to,message=message["message"])
            messages.save()
            chat_room = ChatRoom.objects.get(room_id=self.room_id)
            chat_room.messages.add(messages)
        self.send(text_data=json.dumps({
            "message": message,
            "date": str(datetime.datetime.now()),
        }))
