# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List
import datetime as dt
from pathlib import Path

import requests
from lxml import etree

from ..utility import CONFIGS


def fetch_dce_history_index() -> Dict[int, Dict[str, str]]:
    """
    Download history data (monthly) from DCE.
    :return: Dict[int, Dict[str, str]].
    """
    result: Dict[int, Dict[str, str]] = {}
    url_dce: str = 'http://www.dce.com.cn'
    url: str = f'{url_dce}/dalianshangpin/xqsj/lssj/index.html'

    # Make sure <year> in possible range.
    year_list: List[int] = [year for year in range(2006, dt.date.today().year)]
    year_list.reverse()
    for year in year_list:
        result[year] = {}

    # Download index page.
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f'Something wrong in downloading <{url}>.'
        )
    response.encoding = 'utf-8'

    # Parse.
    html: etree._Element = etree.HTML(response.text)
    history_data_list: List[etree._Element] = html.xpath('//ul[@class="cate_sel clearfix"]')

    for i in range(len(year_list)):
        product_list = history_data_list[i].xpath('./li/label/text()')
        url_list = history_data_list[i].xpath('./li/label/input/@rel')
        assert len(product_list) == len(url_list)
        for j in range(len(product_list)):
            result[year_list[i]][product_list[j]] = f'{url_dce}/{url_list[j]}'

    return result


def download_dce_history_data(year: int) -> None:
    data_index: Dict[int, Dict[str, str]] = fetch_dce_history_index()
    download_path: Path = Path(CONFIGS['path']['download'])
    extension_name: str
    for product, url in data_index[year].items():
        extension_name = url.split('.')[-1]
        download_file = download_path.joinpath(f'DCE_{product}_{year}.{extension_name}')
        response = requests.get(url)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f'Something wrong in downloading <{url}>.'
            )
        with open(download_file, 'wb') as f:
            f.write(response.content)

