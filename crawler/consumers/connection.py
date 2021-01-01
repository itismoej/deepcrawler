import json
from uuid import uuid4

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from crawler.engine import run_engine


class ConnectionConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks_status: dict[str, bool] = {}
        self.crawl_id: str = ''

    async def connect(self):
        await self.accept()
        self.crawl_id = uuid4().hex

    async def receive(self, text_data=None, bytes_data=None):
        data: dict = json.loads(text_data)
        if 'initial_links' in data:
            run_engine(data, self)
            # await sync_to_async(run_engine)(data, self)
