"""
ASGI config for server.parent project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

import channels_graphql_ws
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path


class GraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""

    # This property method delays the import of the schema until the consumer class is instantiated.
    @property
    def schema(self):
        from ix.schema import schema

        return schema

    # Uncomment to send keepalive message every 42 seconds.
    # send_keepalive_every = 42

    # Uncomment to process requests sequentially (useful for tests).
    # strict_ordering = True

    async def on_connect(self, payload):
        """New client connection handler."""
        pass


# Set up the ASGI application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ix.server.settings")
django_application = get_asgi_application()
graphql_application = URLRouter(
    [
        # Route for the websocket consumers
        path("graphql-ws/", GraphqlWsConsumer.as_asgi())
    ]
)

application = ProtocolTypeRouter(
    {
        "http": django_application,  # Django handles HTTP requests
        "websocket": graphql_application,  # Starlette handles WebSocket requests
    }
)
