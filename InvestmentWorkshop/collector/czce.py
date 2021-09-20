# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Dict

import requests
from lxml import etree


def fetch_czce_history_index() -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {
        'futures': [],
        'option': [],
    }
    url_czce: str = 'http://www.czce.com.cn'
    url: str = f'{url_czce}/cn/jysj/lshqxz/H770319index_1.htm'

    # Download index page.
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f'Something wrong in downloading <{url}>.'
        )
    response.encoding = 'utf-8'

    # Parse.
    html: etree._Element = etree.HTML(response.text)
    data_url_list: List[etree._Element] = html.xpath(
        '//li/span[@class="hidden-xs"]/a[@target="_blank"]/@href'
    )
    for data_url in data_url_list:
        if 'Option' in data_url:
            result['option'].append(f'{url_czce}{data_url}')
        else:
            result['futures'].append(f'{url_czce}{data_url}')
    return result
