from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import close_old_connections

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        token = parse_qs(query_string).get('token')
        if token:
            try:
                validated_token = UntypedToken(token[0])
                user = JWTAuthentication().get_user(validated_token)
                scope['user'] = user
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        close_old_connections()
        return await super().__call__(scope, receive, send)