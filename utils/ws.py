from fastapi import WebSocket

from models.chat import Message


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = dict()

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        print("accept handshake:", username)

    async def disconnect(self, username):
        await self.active_connections.pop(username).close()
        print(username, "disconnected.")

    async def send_message(self, message: Message, receivers: list[str], chat_id: str):
        receivers = filter(lambda x: x in self.active_connections, receivers)
        for receiver in receivers:
            await self.active_connections[receiver].send_json({
                "sender": message.sender_id,
                "caption": message.caption,
                "attachments": message.attachments,
                "chat_id": chat_id,
            })
