from fastapi import FastAPI
from routes import user, admin, event, auth, superadmin, team, remarks, rootTeam, rootEvent, rootUser
from fastapi.middleware.cors import CORSMiddleware
from utils.reader import Frontend

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Frontend],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



app.include_router(user.router)
app.include_router(event.router)
app.include_router(auth.router)
app.include_router(superadmin.router)
app.include_router(team.router)
app.include_router(remarks.router)
app.include_router(rootTeam.router)
app.include_router(rootUser.router)
app.include_router(rootEvent.router)
app.include_router(admin.router)
