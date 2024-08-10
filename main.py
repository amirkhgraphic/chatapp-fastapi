from fastapi import FastAPI

from routes import auth, chat

app = FastAPI()
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
