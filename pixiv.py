import time, json, os
from pathlib import Path
from typing import Mapping, Iterable

import httpx
from loguru import logger
from tqdm import tqdm

from settings import INDEX_URL, USER_INFO_URL, USER_ARTWORK_URL, IMG_INFO_URL
from settings import USER_ID
from settings import BASE_HEADERS, BASE_PARAMS, PROXY
from simu_login import save_and_return_cookies


os.makedirs('./pixiv_images/covers', exist_ok=True)
os.makedirs('./pixiv_images/illusts', exist_ok=True)


def build_record() -> dict:
    try:
        with open('record.json', 'r') as f:
            return json.load(f)
    except:
        return {}


def build_cookies() -> dict:
    try:
        with open('cookies.json', 'r') as f:
            return json.load(f)
    except:
        return save_and_return_cookies() 


COOKIES: dict = build_cookies()

RECORD: dict = build_record()

CLIENT = httpx.Client(proxy=PROXY, cookies=COOKIES)


def build_ajax_headers(base_headers: Mapping) -> dict:
    index_headers = {
        "accept": "application/json",
    }
    index_headers.update(base_headers)
    return index_headers

AJAX_HEADERS: dict = build_ajax_headers(BASE_HEADERS)


def scrape(url: str, headers: Mapping, params: Mapping) -> httpx.Response:
    global CLIENT
    res = CLIENT.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res

def update_record(img: 'Img') -> None:
    RECORD.update({
        img.title: {
            'cover_saved': img.cover_saved,
            'original_saved': img.original_saved
        }
    })

def update_records(imgs: Iterable['Img']) -> None:
    for img in imgs: update_record(img)
    
    with open('record.json', 'w') as f:
        json.dump(RECORD, f, ensure_ascii=False, indent=2)


class Index(object):
    def __init__(self):
        global AJAX_HEADERS, BASE_PARAMS
        self.headers = AJAX_HEADERS
        self.params = {
          'mode': 'all',
        }
        self.params.update(BASE_PARAMS)

        self.__post_init__()


    def __post_init__(self):
        res = scrape(INDEX_URL, self.headers, self.params).json()
        logger.info('Scraping index')

        illusts = res['body']['thumbnails']['illust']
        img_ids = [ int(illust['id']) for illust in illusts ]

        self.illusts = []
        for img_id in img_ids:
            self.illusts.append(Img.from_id(img_id))
            time.sleep(1)


class User(object):
    def __init__(self, user_id: int, user_name: str, illusts: list['Img'] | None = None):
        global AJAX_HEADERS, BASE_PARAMS
        self.headers = AJAX_HEADERS
        self.params = BASE_PARAMS

        self.id: int = user_id
        self.name: str = user_name.replace('/', '_')
        # attribute illusts is not necessary
        self.illusts: list[Img] | None = illusts


    def get_illusts(self) -> list['Img']:
        if self.illusts is None:
            res = scrape(USER_ARTWORK_URL.format(user_id=self.id, mode='all'), self.headers, self.params).json()
            logger.info(f'Scraping user: {self.name}')

            self.illusts = []
            img_ids = res['body']['illusts']
            for img_id in img_ids:
                self.illusts.append(Img.from_id(img_id))
                time.sleep(1)
        
        return self.illusts


    @staticmethod
    def from_id(user_id: int) -> 'User':
        global AJAX_HEADERS, BASE_PARAMS
        res = scrape(USER_INFO_URL.format(user_id=user_id), AJAX_HEADERS, BASE_PARAMS).json()

        name = res['body']['name']
        instance = User(user_id, name)
        logger.info(f'Scraping user: {name}')

        res = scrape(USER_ARTWORK_URL.format(user_id=user_id, mode='all'), AJAX_HEADERS, BASE_PARAMS).json()

        illusts: list[Img] = []
        img_ids = res['body']['illusts']
        logger.info(f'Found {len(img_ids)} illusts')
        for img_id in img_ids:
            illusts.append(Img.from_id(img_id))
            time.sleep(1)

        instance.illusts = illusts
        logger.info(f'Loaded user: {name}')

        return instance


class Img(object):
    def __init__(self, title: str, author: User, urls: Iterable[str]):
        global BASE_HEADERS, BASE_PARAMS, RECORD
        self.headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        self.headers.update(BASE_HEADERS)
        self.params = BASE_PARAMS

        self.title: str = title.replace('/', '_')
        self.author: User = author
        self.urls: Iterable[str] = urls
        self.cover: bytes | None = None
        self.original: list[bytes] | None = None
        self.cover_saved: bool = False
        self.original_saved: bool = False
        self.format: str | None = None

        self.__post_init__()


    def __post_init__(self):
        self.cover_url = self.urls['thumb']

        if type(self.urls['original']) == str:
            self.original_url = [ self.urls['original'] ]
        else:
            self.original_url = self.urls['original']
        
        self.format = self.original_url[0].split('.')[-1]

        if RECORD.get(self.title) is None:
            update_record(self)


    def get_binary(self) -> None:
        if not RECORD[self.title]['cover_saved']:
            self.get_cover()
        if not RECORD[self.title]['original_saved']:
            self.get_original()

    def get_cover(self) -> None:
        self.cover = scrape(self.cover_url, self.headers, self.params).content
        logger.info(f'Got cover: {self.title} - {self.author.name}')

    def get_original(self) -> None:
        self.original = [ scrape(url, self.headers, self.params).content for url in self.original_url ]
        logger.info(f'Got original: {self.title} - {self.author.name}')


    def save(self) -> None:
        if not RECORD[self.title]['cover_saved']:
            self.save_cover()
        if not RECORD[self.title]['original_saved']:
            self.save_original()

    def save_cover(self) -> None:
        if self.cover:
            filename = f'./pixiv_images/covers/{self.title} - {self.author.name}.jpg'
            Path(filename).write_bytes(self.cover) # avoid illegal filenames

            self.cover_saved = True
            logger.info(f'Saved cover: {self.title} - {self.author.name}')

    def save_original(self) -> None:
        if self.original:
            for i in range(0, len(self.original)):
                filename = f'./pixiv_images/illusts/{self.title} - {self.author.name}_p{i}.{self.format}'
                Path(filename).write_bytes(self.original[i]) # avoid illegal filenames
            
            self.original_saved = True
            logger.info(f'Saved original: {self.title} - {self.author.name}')


    @staticmethod
    def from_id(img_id: int) -> 'Img':
        global BASE_HEADERS, BASE_PARAMS
        res = scrape(IMG_INFO_URL.format(img_id=img_id), BASE_HEADERS, BASE_PARAMS).json()

        title = res['body']['title']
        user_name = res['body']['userName']
        user_id = res['body']['userId']
        urls = res['body']['urls']

        logger.info(f'Loaded image: {title} - {user_name}')

        return Img(title, User(user_id, user_name), urls)


def main():
    try:
        user = User.from_id(USER_ID)
        illusts = user.get_illusts()
        logger.debug(RECORD)
        for illust in tqdm(illusts):
            illust.get_binary()
            illust.save()
            if not RECORD[illust.title]['original_saved']:
                logger.info(f'Waiting 4 seconds...')
                time.sleep(4)
    finally:
        update_records(illusts)


if __name__ == '__main__':
    main()
    # pass