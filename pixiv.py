import time, os, re
from typing import Mapping

import httpx
from loguru import logger
from tqdm import tqdm

from settings import PROXY, INDEX_URL, USER_URL, IMAGE_SRC_URL, TIME_PATTERN
from preprocess import INDEX_HEADERS, INDEX_PARAMS, IMAGE_HEADERS, CLIENT, Image, build_user_index_params


def scrape(url: str, headers: Mapping, params: Mapping | None = None) -> httpx.Response:
    global CLIENT
    res = CLIENT.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res

def parse_works(works: list[Mapping]) -> list[Image]:
    page_counts: list[int] = [ illust['pageCount'] for illust in works ]
    ids: list[str] = [ illust['id'] for illust in works ]
    times: list[str] = [ '/'.join(TIME_PATTERN.findall(illust['updateDate'])[:-2])
                         for illust in works ]
    
    titles: list[str] = [ illust['title'] for illust in works ]
    authors: list[str] = [ illust['userName'] for illust in works ]

    cover_urls: list[str] = [ illust['url'] for illust in works ]
    src_urls: list[tuple[str]] = [ IMAGE_SRC_URL.format(time=time, id=id)
                                   for time, id in zip(times, ids) ]
    for page_count in page_counts:
        if page_count > 1:
            src_urls = [ [ src_url + f'_p{i}' for i in range(0, page_count) ]
                             for src_url in src_urls ]
        else:
            src_urls = [ [ src_url + '_p0' ] for src_url in src_urls ]
    
    images = [ Image(title, author, cover_url, src_url) 
              for title, author, cover_url, src_url 
              in zip(titles, authors, cover_urls, src_urls) ]
    return images


def scrape_index() -> httpx.Response:
    logger.info('Scraping index...')
    return scrape(INDEX_URL, INDEX_HEADERS, INDEX_PARAMS)

def parse_index(res: httpx.Response) -> list[Image]:
    res = res.json()
    works = res['body']['thumbnails']['illust']
    total = len(works)
    logger.info(f'Found {total} images...')

    return parse_works(works)

def scrape_user(user_id: int) -> httpx.Response:
    return scrape(USER_URL.format(user_id=user_id, mode='all'), INDEX_HEADERS)

def parse_user(res: httpx.Response) -> list[int]:
    res = res.json()
    illusts: list[int] = res['body']['illusts'].keys()
    total = len(illusts)
    logger.info(f'Found {total} images...')

    return illusts

def scrape_user_index(user_id: int, ids: list[int]) -> httpx.Response:
    return scrape(USER_URL.format(user_id=user_id, mode='illusts'),
                  INDEX_HEADERS,
                  params=build_user_index_params(INDEX_PARAMS, ids, '1'))

def parse_user_index(res: httpx.Response) -> list[Image]:
    res = res.json()
    works = res['body']['works'].values()

    return parse_works(works)

def scrape_image(image: Image) -> Image:
    logger.info(f'Scraping image: {image.title} - {image.author}...')
    image.cover = scrape(image.cover_url, IMAGE_HEADERS).content
    image.src = scrape(image.src_url, IMAGE_HEADERS).content
    return image

def save_image(image: Image) -> None:
    with open(f'./pixiv_images/cover/{image.title} - {image.author}.jpg', 'wb') as image_file:
        image_file.write(image.cover)
    with open(f'./pixiv_images/illusts/{image.title} - {image.author}.png', 'wb') as image_file:
        image_file.write(image.src)
    logger.info(f'Saved image: {image.title} - {image.author}')

def main():
    res = scrape_index()
    images = parse_index(res)
    for image in tqdm(images):
        image = scrape_image(image)
        save_image(image)
        time.sleep(1)

if __name__ == '__main__':
    main()