import time, os
from typing import Mapping

import httpx
from loguru import logger

from settings import PROXY, COOKIES, INDEX_URL, INDEX_HEADERS, IMAGE_HEADERS

CLIENT = httpx.Client(proxy=PROXY, cookies=COOKIES)

os.makedirs('./pixiv_images', exist_ok=True)

class Image(object):
    def __init__(self, title, author, url):
        self.title = title
        self.author = author
        self.url = url
        self.content = None

def scrape(url: str, headers: Mapping):
    global CLIENT
    res = CLIENT.get(url, headers=headers)
    res.raise_for_status()
    return res

def scrape_index():
    logger.info('Scraping index...')
    return scrape(INDEX_URL, INDEX_HEADERS)

def parse_index(res: httpx.Response):
    res = res.json()
    illusts = res['body']['thumbnails']['illust']
    logger.info(f'Found {len(illusts)} images...')
    titles = [ illust['title'] for illust in illusts ]
    authors = [ illust['userName'] for illust in illusts ]
    urls = [ illust['url'] for illust in illusts ]
    images = [ Image(title, author, url) for title, author, url in zip(titles, authors, urls) ]
    return images

def scrape_image(image: Image):
    logger.info(f'Scraping image: {image.title} - {image.author}...')
    image.content = scrape(image.url, IMAGE_HEADERS).content
    return image

def save_image(image: Image):
    with open(f'./pixiv_images/{image.title} - {image.author}.jpg', 'wb') as image_file:
        image_file.write(image.content)
    logger.info(f'Saved image: {image.title} - {image.author}.jpg')

def main():
    res = scrape_index()
    images = parse_index(res)
    for image in images:
        image = scrape_image(image)
        save_image(image)
        time.sleep(1)

if __name__ == '__main__':
    main()