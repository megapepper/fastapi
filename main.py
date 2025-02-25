import app


app = app.make_app()

'''
app = FastAPI()

app.include_router(health.router)
app.include_router(user.router)
app.include_router(auth.router)

app.add_middleware(middlewares.CheckAuthentication)
app.add_middleware(middlewares.ExceptionHandlingMiddleware)
'''
