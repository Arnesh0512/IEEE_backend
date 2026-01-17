from fastapi import FastAPI
from routes import user, event, auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



app.include_router(user.router)
app.include_router(event.router)
app.include_router(auth.router)
