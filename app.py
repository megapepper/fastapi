from fastapi import FastAPI
from fastapi import FastAPI
from routers import health, auth, user
import database
import middlewares

def make_app(pool_config=None):
    database.user.init_pool(pool_config)
    app = FastAPI()

    app.include_router(health.router)
    app.include_router(user.router)
    app.include_router(auth.router)

    app.add_middleware(middlewares.CheckAuthentication)
    app.add_middleware(middlewares.ExceptionHandlingMiddleware)

    return app