from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, chat

app = FastAPI()
app.include_router(auth.router)
app.include_router(chat.router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # should be updated as needed!!!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
