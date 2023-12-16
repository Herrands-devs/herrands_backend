"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application
from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from config.middleware import TokenAuthMiddlewareStack
from api.consumers import ErrandConsumer, ChatConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('errand/', ErrandConsumer.as_asgi()),
            path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),
        ])
    ),
})
