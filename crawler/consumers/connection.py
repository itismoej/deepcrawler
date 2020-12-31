import json
from uuid import uuid4

from channels.generic.websocket import AsyncWebsocketConsumer

from crawler.engine import run_engine


class ConnectionConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks_status: dict[str, bool] = {}
        self.crawl_id: str = ''

    async def connect(self):
        await self.accept()
        self.crawl_id = uuid4().hex[8:12]

    async def receive(self, text_data=None, bytes_data=None):
        data: dict = json.loads(text_data)
        if 'initial_links' in data:
            initial_links = data['initial_links']
            self.tasks_status = {
                site['id']: False for site in initial_links
            }
            run_engine(initial_links, self)
