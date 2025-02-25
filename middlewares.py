from fastapi import Request
from fastapi.responses import Response
import psycopg2
from routers import auth
import models
from starlette.middleware.base import BaseHTTPMiddleware


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except models.LoginNotUnique as e:
            return Response(status_code=409, content = e)
        except models.LoginNotExists as e:
            return Response(status_code=401, content = repr(e))
        except models.IncorrectPassword as e:
            return Response(status_code=401, content = repr(e))
        except models.UserNotExists as e:
            return Response(status_code=401, content = repr(e))
        except auth.jwt.exceptions.ExpiredSignatureError as e:
            return Response(status_code=401, content = 'Login Please')
        except auth.jwt.exceptions.DecodeError as e:
            return Response(status_code=401, content = 'Login Please')
        except models.AccessDenied as e:
            return Response(status_code=401, content = repr(e))
        except models.LoggedOut as e:
            return Response(status_code=401, content = repr(e))
    

class CheckAuthentication(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        url = request.url.path
        default_auth = [('GET','/health'), ('POST','/api/v1/auth'), ('POST', '/api/v1/users'), ('GET', '/docs'), ('GET', '/openapi.json')]
        if (method, url) not in default_auth:
            token = request.headers.get("Authorization")
            params = request.query_params
            user_id = params.get('user_id')
            auth.check_token(token, user_id)
        return await call_next(request)

