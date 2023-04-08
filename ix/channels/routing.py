from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from ix.channels import consumers

application = ProtocolTypeRouter(
    {
        "http": URLRouter([]),
        "websocket": URLRouter(
            [
                path(
                    "ws/check_task_status/", consumers.CheckTaskStatusConsumer.as_asgi()
                ),
            ]
        ),
    }
)
