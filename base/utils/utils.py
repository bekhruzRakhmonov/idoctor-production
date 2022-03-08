from ..models import ChatMessage, ChatRoom, User
from channels.db import database_sync_to_async

@database_sync_to_async
def get_room_id(_from,_to):
    user1 = User.objects.get(email=_from)
    user2 = User.objects.get(email=_to)
    try:
        room_id = ChatRoom.get_room_id(user1,user2)
    except ChatRoom.DoesNotExist:
        room_id = ChatRoom.create_room_id(user1,user2)
    return room_id

@database_sync_to_async
def create_message(_from,_to,message,room_id):
    user1 = User.objects.get(email=_from)
    user2 = User.objects.get(email=_to)
    if len(message) > 0:
        messages = ChatMessage(outgoing=user1,incoming=user2,message=message)
        messages.save(force_insert=True)
        chat_room = ChatRoom.objects.get(room_id=room_id)
        chat_room.messages.add(messages)
        return {
            "from": str(messages.outgoing.email),
            "to": str(messages.incoming.email),
            "message": str(messages.message),
            "date": str(messages.date),
        }