# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Dict

import requests
from lxml import etree


def fetch_czce_history_index() -> Dict[str, Dict[int, str]]:
    result: Dict[str, Dict[int, str]] = {
        'futures': {},
        'option': {},
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
    url_list: List[str] = []
    year_list: List[str] = []
    node_list: List[etree._Element] = html.xpath('//li/span[@class="hidden-xs"]')
    for node in node_list:
        url_list.append(node.xpath('./a[@target="_blank"]/@href')[0])
        year_list.append(node.xpath('../text()')[0])
    assert len(url_list) == len(year_list)

    # Get result.
    for i in range(len(url_list)):
        year = int(year_list[i][:4])
        if 'Option' in url_list[i]:
            result['option'][year] = f'{url_czce}{url_list[i]}'
        else:
            result['futures'][year] = f'{url_czce}{url_list[i]}'
    return result
