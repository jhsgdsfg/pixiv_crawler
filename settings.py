PROXY: str = 'http://127.0.0.1:1081'

USER_ID: int = 44898022
X_USER_ID: str = '71413581'

BASE_URL: str = 'https://www.pixiv.net'
INDEX_URL: str = BASE_URL + '/ajax/top/illust'

USER_INFO_URL: str = BASE_URL + '/ajax/user/{user_id}'
USER_ARTWORK_URL: str = BASE_URL + '/ajax/user/{user_id}/profile/{mode}'

IMG_INFO_URL: str = BASE_URL + '/ajax/illust/{img_id}'

BASE_HEADERS: dict = {
    "x-user-id": X_USER_ID,
    "referer": BASE_URL,
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

BASE_PARAMS: dict = {
    'lang': 'zh',
    'version': 'a48f2f681629909b885608393916b81989accf5b',
}
