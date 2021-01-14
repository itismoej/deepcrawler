import json
from math import floor
from random import randint

from django.db import models


class Crawl(models.Model):
    pass


class Site(models.Model):
    crawl = models.ForeignKey(Crawl, on_delete=models.CASCADE)
    url = models.URLField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)


class Content(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    content = models.TextField()


class MemorySite:
    def __init__(self, site: Site, sender, steps):
        self.site = site
        self._sender = sender
        self.steps = steps
        self.current_step = 0
        self.progress = 0

    def send_progress(self, percent):
        self._sender(text_data=json.dumps({
            'site_id': self.site.id,
            'progress': percent
        }))

    def go_next_step(self):
        self.send_progress(percent=self.current_step * 100 / self.steps)
        self.current_step += 1

    def increment_progress(self):
        if self.progress < 89:
            self.progress += randint(5, 25) / 10
        elif self.progress < 96:
            self.progress += randint(1, 4) / 10
        elif self.progress < 99:
            self.progress += randint(2, 8) / 100

        if self.progress != floor(self.progress):
            self.send_progress(floor(self.progress))
