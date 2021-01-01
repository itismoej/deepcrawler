import asyncio
import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from config import settings

executor = ThreadPoolExecutor(10)

options = Options()
options.page_load_strategy = 'normal'
options.headless = True


def scraper(url: str, site_id: str, consumer, event_loop):
    def send_progress(percent: int) -> None:
        asyncio.ensure_future(consumer.send(text_data=json.dumps({
            'site_id': site_id,
            'progress': percent
        })), loop=event_loop)

    try:
        send_progress(randint(23, 35))
        browser = webdriver.Chrome(
            executable_path=settings.BASE_DIR / 'chromedriver',
            chrome_options=options,
        )
        send_progress(randint(40, 47))
        browser.get(url)
        send_progress(randint(51, 59))
        html = browser.find_element_by_tag_name('html').get_attribute('outerHTML')
        send_progress(randint(63, 79))
        filename = settings.BASE_DIR / 'media' / consumer.crawl_id / f'{site_id}.html'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        send_progress(randint(82, 93))
        with open(filename, 'w') as f:
            f.write(html)
        send_progress(100)
        consumer.tasks_status[site_id] = True
    except WebDriverException:
        send_progress(-1)

    if all(consumer.tasks_status.values()):
        asyncio.ensure_future(consumer.send(text_data=json.dumps({
            'id_done': True,
            'crawl_id': consumer.crawl_id
        })), loop=event_loop)


def run_engine(initial_links: list[dict], consumer):
    event_loop = asyncio.get_event_loop()
    for site in initial_links:
        site_id = site['id']
        url = site['link']
        asyncio.ensure_future(consumer.send(text_data=json.dumps({
            'site_id': site_id,
            'progress': randint(7, 19),
        })), loop=event_loop)
        event_loop.run_in_executor(executor, scraper, url, site_id, consumer, event_loop)

    runnable_tasks = asyncio.gather(*asyncio.all_tasks(event_loop))
    asyncio.ensure_future(runnable_tasks, loop=event_loop)
