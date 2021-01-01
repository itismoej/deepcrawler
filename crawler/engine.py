import asyncio
import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

from qaes import aes
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from config import settings

executor = ThreadPoolExecutor(10)

options = Options()
options.page_load_strategy = 'normal'
options.headless = True


def scraper(depth: int, url: str, consumer, event_loop):
    try:
        browser = webdriver.Chrome(
            executable_path=settings.BASE_DIR / 'chromedriver',
            chrome_options=options,
        )
        directory = settings.BASE_DIR / 'media' / consumer.crawl_id
        scrape_url(browser, consumer, depth, 0, url, directory)
    except WebDriverException as e:
        print('web driver exception:', e)

    if all(consumer.tasks_status.values()):
        asyncio.ensure_future(consumer.send(text_data=json.dumps({
            'id_done': True,
            'crawl_id': consumer.crawl_id
        })), loop=event_loop)


def make_safe(b64_encoded: str):
    return b64_encoded.replace('/', '_')


def make_b64(safe_str: str):
    return safe_str.replace('_', '/')


def scrape_url(browser, consumer, depth, current_depth, url, directory: Path):
    browser.get(url)
    html_tag = browser.find_element_by_tag_name('html')
    html = html_tag.get_attribute('outerHTML')
    site_id = make_safe(aes.encrypt(url))
    filename = directory / f'{site_id}.html'
    os.makedirs(f'{os.path.dirname(filename)}/children', exist_ok=True)
    with open(filename, 'w') as f:
        f.write(html)
    consumer.tasks_status[site_id] = True

    if current_depth < depth:
        for link in html_tag.find_elements_by_tag_name('a'):
            child_url = link.get_attribute('href')
            children_directory = directory / 'children'
            scrape_url(browser, consumer, depth, current_depth + 1, child_url, children_directory)


def run_engine(data, consumer):
    initial_links, depth = data['initial_links'], data['depth']
    consumer.tasks_status = {}
    event_loop = asyncio.get_event_loop()
    for site in initial_links:
        url = site['link']
        site_id = make_safe(aes.encrypt(url))
        consumer.tasks_status[site_id] = False
        # asyncio.ensure_future(consumer.send(text_data=json.dumps({
        #     'site_id': site_id,
        #     'progress': randint(7, 19),
        # })), loop=event_loop)
        event_loop.run_in_executor(executor, scraper, depth, url, consumer, event_loop)

    runnable_tasks = asyncio.gather(*asyncio.all_tasks(event_loop))
    asyncio.ensure_future(runnable_tasks, loop=event_loop)
