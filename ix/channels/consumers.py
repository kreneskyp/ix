import json
import aioredis
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class CheckTaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.redis = await aioredis.create_redis_pool("redis://localhost:6379")
        self.pubsub = self.redis.pubsub()
        self.pubsub_channel = "task_updates"
        await self.pubsub.subscribe(self.pubsub_channel)

        self.accept_task = asyncio.create_task(self.accept())
        self.pubsub_task = asyncio.create_task(self.handle_pubsub())

    async def disconnect(self, close_code):
        await self.pubsub.unsubscribe(self.pubsub_channel)
        await self.redis.close()
        await self.redis.wait_closed()
        self.pubsub_task.cancel()
        self.accept_task.cancel()

    async def handle_pubsub(self):
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await self.send(json.dumps({"status": message["data"].decode()}))
            await asyncio.sleep(0.1)

    async def receive(self, text_data):
        if text_data == "start_task":
            my_celery_task.delay()
