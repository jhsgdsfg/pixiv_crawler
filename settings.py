PROXY = 'http://127.0.0.1:1081'

BASE_URL = 'https://www.pixiv.net'

BASE_HEADERS = {
    "x-user-id": "71413581",
    "referer": BASE_URL,
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

COOKIES = {
    r'first_visit_datetime_pc': r'2023-11-18%2011%3A12%3A02',
    r'p_ab_id': r'1',
    r'p_ab_id_2': r'7',
    r'p_ab_d_id': r'1998664397',
    r'yuid_b': r'Nol5hEI',
    r'privacy_policy_agreement': r'6',
    r'c_type': r'25',
    r'privacy_policy_notification': r'0',
    r'a_type': r'0',
    r'b_type': r'1',
    r'cc1': r'2023-12-31%2014%3A31%3A19',
    r'PHPSESSID': r'71413581_RyfISggheVah8XYb9RVrtX7RH4P07Glw',
    r'device_token': r'005512354981313ceeae9c0ab4ce963d',
    r'login_ever': r'yes',
    r'_ga_MZ1NL4PHH0': r'GS1.1.1704000768.2.1.1704000840.0.0.0',
    r'QSI_S_ZN_5hF4My7Ad6VNNAi': r'v:100:0',
    r'_gid': r'GA1.2.707870221.1704000861',
    r'_gcl_au': r'1.1.533837655.1704000877',
    r'__cf_bm': r'2K6Bw59FKzXFoWn1L29TbCs228mIb3W4HTAgoelhH7g-1704083574-1-AWMNXuLb/8SzoEhiIeR5b5nV0SCerELrZMN3IgPO8ppYYmdN93OG8D6vlUx/61D7sFrU8p4ePmcVKm1mko99R9VPeM8cJpEtKG80vd9Zcz0W',
    r'_ga': r'GA1.1.39146621.1700273527',
    r'_ga_75BBYNYN9J': r'GS1.1.1704083577.6.0.1704083577.0.0.0',
    r'cf_clearance': r'uf1cNNA_3PDrF.LJfB_W5mYqjfVwd6lMb69SKa9WLgQ-1704083580-0-2-27740560.b5379676.70755a80-0.2.1704083580'
}


def build_index_headers(base_headers):
    index_headers = {
        "accept": "application/json",
    }
    index_headers.update(base_headers)
    return index_headers

def build_image_headers(base_headers):
    image_headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    image_headers.update(base_headers)
    return image_headers
    

def build_index_url(base_url):
    index_path = '/ajax/top/illust?mode=all&lang=zh&version=a48f2f681629909b885608393916b81989accf5b'
    return base_url + index_path


INDEX_HEADERS = build_index_headers(BASE_HEADERS)

IMAGE_HEADERS = build_image_headers(BASE_HEADERS)

INDEX_URL = build_index_url(BASE_URL)