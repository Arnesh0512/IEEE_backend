from fastapi import FastAPI
from routes import user, event

app = FastAPI()

app.include_router(user.router)
app.include_router(event.router)
