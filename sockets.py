import json

import socketio

from database import get_db
from models.chat import Message, Attachment

sio = socketio.AsyncServer(
    cors_allowed_origins='*',
    async_mode='asgi'
)
manager = socketio.AsyncManager()
db = get_db()


class SocketIOAsyncNamespace(socketio.AsyncNamespace):
    async def send_to_chat(self, event, data, to, skip_sid=None):
        await self.emit(event, data, to=to, skip_sid=skip_sid)

    async def online_counts(self, chat_id):
        online_users = len(manager.get_participants(self.namespace, chat_id))
        await self.emit('online_counts', str(online_users), to=chat_id)

    async def on_connect(self, sid, env):
        username = env.get('HTTP_X_USERNAME')
        chat_id = env.get('HTTP_X_CHAT_ID')

        async with self.session(sid) as session:
            session["username"] = username
            session["chat_id"] = chat_id

        await self.enter_room(sid, chat_id)

        sio.start_background_task(self.send_to_chat, 'user_joined', username, chat_id)
        sio.start_background_task(self.online_counts, chat_id)

    async def on_disconnect(self, sid):
        async with sio.session(sid) as session:
            chat_id = session["chat_id"]
            username = session["username"]
            await self.leave_room(sid, chat_id)

            if len(manager.get_participants(self.namespace, chat_id)) == 0:
                await self.close_room(chat_id)

            sio.start_background_task(self.send_to_chat, 'user_left', username, chat_id)
            sio.start_background_task(self.online_counts, chat_id)

    async def on_message(self, sid, data):
        """
        data = {
            "chat_type": private|group,
            "sender_id": username,
            "caption": string content,
            "attachments": list({"file": url , "type": str}),
        }
        """
        async with sio.session(sid) as session:
            chat_id = session["chat_id"]
            message = self.save_message_to_db(data, chat_id)
            if message:
                sio.start_background_task(self.send_to_chat, 'new_message', message, chat_id, sid)

    @staticmethod
    def save_message_to_db(data, chat_id):
        try:
            data = json.load(data)
            attachments = [Attachment(type=attachment["type"], file=attachment["file"])
                           for attachment in data["attachments"]]
            message = Message(
                sender_id=data["sender_id"],
                caption=data["caption"],
                attachments=attachments,
            ).dict()

            db.update_one(f"{data['chat_type']}_chats", {"_id": chat_id}, "push", {"messages": message})
            return message

        except ValueError:
            return None


"""
<script>
        const socket = io('ws://localhost:8000/',  { transports: ["websocket"] });
        socket.on(<EVENT>, function (data) {
            ...
        });
</script>
"""
