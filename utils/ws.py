from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = dict()

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        print("accept handshake:", username)

    def disconnect(self, username):
        self.active_connections.pop(username)
        print(username, "disconnected.")

    async def send_message(self, message: str, receiver: str, message_type: str):
        if receiver in self.active_connections:
            await self.active_connections[receiver].send_json({
                "message": message,
                "type": message_type
            })

    async def send_private_message(self, message: str, user1: str, user2: str):
        await self.send_message(message, user1, "private")
        await self.send_message(message, user2, "private")

    async def send_group_message(self, message: str, group_members: list[str]):
        for member in group_members:
            await self.send_message(message, member, "group")
