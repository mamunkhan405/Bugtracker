import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from tracker.middleware import JWTAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator
import tracker.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bugtracker.settings")

django_asgi_app  = get_asgi_application()

application = ProtocolTypeRouter({
     "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            tracker.routing.websocket_urlpatterns
        )
    ),
})