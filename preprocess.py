import json, os
from typing import Mapping

import httpx

from settings import BASE_HEADERS, BASE_PARAMS, PROXY

from simu_login import save_and_return_cookies

def build_index_headers(base_headers: Mapping) -> dict:
    index_headers = {
        "accept": "application/json",
    }
    index_headers.update(base_headers)
    return index_headers

def build_index_params(base_params: Mapping) -> dict:
    index_params = {
        'mode': 'all',
    }
    index_params.update(base_params)
    return index_params

def build_user_index_params(base_params: Mapping, ids: list[int], is_first_page: str) -> dict:
    user_index_params = {
        r'ids%5B%5D': ids,
        'work_category': 'illustManga',
        'is_first_page': is_first_page,
    }
    user_index_params.update(base_params)
    return user_index_params

def build_image_headers(base_headers: Mapping) -> dict:
    image_headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    image_headers.update(base_headers)
    return image_headers

def build_cookies() -> dict:
    try:
        with open('cookies.json', 'r') as f:
            return json.load(f)
    except:
        return save_and_return_cookies() 


INDEX_HEADERS: dict = build_index_headers(BASE_HEADERS)

INDEX_PARAMS: dict = build_index_params(BASE_PARAMS)

IMAGE_HEADERS: dict = build_image_headers(BASE_HEADERS)

COOKIES: dict = build_cookies()

CLIENT = httpx.Client(proxy=PROXY, cookies=COOKIES)

os.makedirs('./pixiv_images/covers', exist_ok=True)
os.makedirs('./pixiv_images/illusts', exist_ok=True)

class Image(object):
    def __init__(self, title: str, author: str, cover_url: str, src_url: str):
        self.title: str = title
        self.author: str = author
        self.cover_url: str = cover_url
        self.src_url: str = src_url
        self.cover: bytes | None = None
        self.src: bytes | None = None
