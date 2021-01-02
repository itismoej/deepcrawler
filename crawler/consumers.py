import json

from channels.generic.websocket import WebsocketConsumer

from crawler.engine import run_engine
from crawler.models import Crawl


class ConnectionConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks_status: dict[str, bool] = {}
        self.crawl = None

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        data: dict = json.loads(text_data)
        if 'initial_links' in data:
            self.crawl = Crawl.objects.create()
            run_engine(data, self)
