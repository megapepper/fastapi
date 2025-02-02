from fastapi import FastAPI, Request, Response
from routers import health, user, auth, db_interaction


app = FastAPI()


app.include_router(health.router)
app.include_router(user.router)
app.include_router(auth.router)

