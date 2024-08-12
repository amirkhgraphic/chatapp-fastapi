import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, chat
from sockets import sio, SocketIOAsyncNamespace

app = FastAPI()
app.include_router(auth.router)
app.include_router(chat.router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # should be updated as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio.register_namespace(SocketIOAsyncNamespace("/"))
sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)
app.add_route("/socket.io/", route=sio_asgi_app)
app.add_websocket_route("/socket.io/", sio_asgi_app)


@app.get("/")  # test
async def root():
    return {"message": "Hello World"}
