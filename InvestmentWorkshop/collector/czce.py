# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Dict
from pathlib import Path

import requests
from lxml import etree

from ..utility import CONFIGS
from .utility import make_directory_existed


CZCE_DATA_INDEX = Dict[str, Dict[int, str]]


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


def download_czce_history_data(year: int, type_: str = 'futures'):
    # Parameters handle.
    url_mapper: CZCE_DATA_INDEX = fetch_czce_history_index()
    url_list: Dict[int, str]
    if type_ == 'futures':
        url_list = url_mapper['futures']
    elif type_ == 'option':
        url_list = url_mapper['option']
    else:
        raise ValueError('<type_> should be "Futures" or "Option".')

    if year not in url_list.keys():
        raise ValueError('<year> is beyond possible range.')

    # Make sure <download_path> existed.
    download_path: Path = Path(CONFIGS['path']['download'])
    make_directory_existed(download_path)

    # Download index page.
    url: str = url_list[year]
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f'Error in downloading <{url.format(year=year)}>.')
    with open(download_path.joinpath(f'CZCE_{type_}_{year:4d}.zip'), 'wb') as f:
        f.write(response.content)
