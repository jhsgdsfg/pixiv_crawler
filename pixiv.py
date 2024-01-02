import time, json, os
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


def build_cookies() -> dict:
    try:
        with open('cookies.json', 'r') as f:
            return json.load(f)
    except:
        return save_and_return_cookies() 


COOKIES: dict = build_cookies()

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


class Index(object):
    def __init__(self):
        global AJAX_HEADERS, BASE_PARAMS
        self.headers = AJAX_HEADERS
        self.params = {
          'mode': 'all',
        }.update(BASE_PARAMS)


    def __post_init__(self):
        res = scrape(INDEX_URL, self.headers, self.params).json()

        illusts = res['body']['thumbnails']['illust']
        img_ids = [ int(illust['id']) for illust in illusts ]

        self.illusts = []
        for img_id in img_ids: self.illusts.append(Img.from_id(img_id)); time.sleep(1)


class User(object):
    def __init__(self, user_id: int, user_name: str, illusts: list['Img'] | None = None):
        global AJAX_HEADERS, BASE_PARAMS
        self.headers = AJAX_HEADERS
        self.params = BASE_PARAMS

        self.id: int = user_id
        self.name: str = user_name
        # attribute illusts is not necessary
        self.illusts: list[Img] | None = illusts


    def get_illusts(self):
        if self.illusts is None:
            res = scrape(USER_ARTWORK_URL.format(user_id=self.id, mode='all'), self.headers, self.params).json()

            self.illusts = []
            img_ids = res['body']['illusts']
            for img_id in img_ids: self.illusts.append(Img.from_id(img_id)); time.sleep(1)
        
        return self.illusts


    @staticmethod
    def from_id(user_id: int):
        global AJAX_HEADERS, BASE_PARAMS
        res = scrape(USER_INFO_URL.format(user_id=user_id), AJAX_HEADERS, BASE_PARAMS).json()

        name = res['body']['name']
        instance = User(user_id, name)

        res = scrape(USER_ARTWORK_URL.format(user_id=user_id, mode='all'), AJAX_HEADERS, BASE_PARAMS).json()

        illusts: list[Img] = []
        img_ids = res['body']['illusts']
        for img_id in img_ids: illusts.append(Img.from_id(img_id)); time.sleep(1)

        instance.illusts = illusts

        return instance
        


class Img(object):
    def __init__(self, title: str, author: User, urls: Iterable[str]):
        global BASE_HEADERS, BASE_PARAMS
        self.headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }.update(BASE_HEADERS)
        self.params = BASE_PARAMS

        self.title: str = title
        self.author: User = author
        self.urls: Iterable[str] = urls
        self.cover: bytes | None = None
        self.original: list[bytes] | None = None
        self.format: str | None = None
    
    def __post_init__(self):
        self.cover_url = self.urls['thumb']

        if type(self.original_url) == str:
            self.original_url = [ self.urls['original'] ]
        else:
            self.original_url = self.urls['original']
        
        self.format = self.original_url[0].split('.')[-1]


    def get_binary(self) -> None:
        self.get_cover()
        self.get_original()

    def get_cover(self) -> None:
        self.cover = scrape(self.cover_url, self.headers, self.params).content


    def get_original(self) -> None:
        self.original = [ scrape(url, self.headers, self.params).content for url in self.original_url ]


    def save(self) -> None:
        if self.cover:
            with open(f'./pixiv_images/cover/{self.title} - {self.author}.jpg', 'wb') as image_file:
                image_file.write(self.cover)
            logger.info(f'Saved cover: {self.title} - {self.author}')
        
        if self.original:
            for i in range(0, len(self.original)):
                with open(f'./pixiv_images/illusts/{self.title} - {self.author}_p{i}.{self.format}', 'wb') as image_file:
                    image_file.write(self.original[i])
            logger.info(f'Saved original: {self.title} - {self.author}')


    @staticmethod
    def from_id(img_id: int) -> 'Img':
        global BASE_HEADERS, BASE_PARAMS
        res = scrape(IMG_INFO_URL.format(img_id=img_id), BASE_HEADERS, BASE_PARAMS).json()

        title = res['body']['title']
        user_name = res['body']['userName']
        user_id = res['body']['userId']
        urls = res['body']['urls']

        return Img(title, User(user_id, user_name), urls)



def main():
    user = User.from_id(USER_ID)
    illusts = user.get_illusts()
    for illust in illusts:
        illust.get_binary()
        illust.save()


if __name__ == '__main__':
    main()