# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Dict
from pathlib import Path
import datetime as dt

import requests
from lxml import etree

from ..utility import CONFIGS
from .utility import make_directory_existed, QuoteDaily, split_symbol


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


def download_czce_history_data_all():
    # Make sure <download_path> existed.
    download_path: Path = Path(CONFIGS['path']['download'])
    make_directory_existed(download_path)

    # Parameters handle.
    url_mapper: CZCE_DATA_INDEX = fetch_czce_history_index()
    url_list: Dict[int, str]
    type_list: List[str] = ['futures', 'option']
    for type_ in type_list:
        url_list = url_mapper[type_]
        for year in url_list.keys():
            url = url_list[year]
            # Download index page.
            response = requests.get(url)
            if response.status_code != 200:
                raise requests.exceptions.HTTPError(f'Error in downloading <{url.format(year=year)}>.')
            with open(download_path.joinpath(f'CZCE_{type_}_{year:4d}.zip'), 'wb') as f:
                f.write(response.content)


def read_czce_history_data(data_file: Path) -> List[QuoteDaily]:
    assert data_file.exists() is True

    result: List[QuoteDaily] = []

    try:
        with open(data_file, mode='r', encoding='gbk') as txt_file:
            lines = txt_file.readlines()
    except UnicodeDecodeError:
        try:
            with open(data_file, mode='r', encoding='utf-8') as txt_file:
                lines = txt_file.readlines()
        except UnicodeDecodeError:
            raise

    year: str = data_file.stem.split('_')[-1]
    for line in lines[2:]:
        data = line.split('|')
        data = [x.strip() for x in data]
        if len(data[0]) == 0:
            break
        if 'option' in data_file.stem:
            result.append(
                {
                    # 交易所
                    'exchange': 'CZCE',
                    # 交易日期
                    'date': dt.date.fromisoformat(data[0]),
                    # 合约代码
                    'symbol': data[1],
                    # 昨结算
                    'previous_settlement': float(data[2].replace(',', '')),
                    # 今开盘
                    'open': None if data[3] == '0.00' else float(data[3].replace(',', '')),
                    # 最高价
                    'high': None if data[4] == '0.00' else float(data[4].replace(',', '')),
                    # 最低价
                    'low': None if data[5] == '0.00' else float(data[5].replace(',', '')),
                    # 今收盘
                    'close': float(data[6].replace(',', '')),
                    # 今结算
                    'settlement': float(data[7].replace(',', '')),
                    # 涨跌1
                    'change_on_close': float(data[8].replace(',', '')),
                    # 涨跌2
                    'change_on_settlement': float(data[9].replace(',', '')),
                    # 成交量(手)
                    'volume': int(data[10].replace(',', '')),
                    # 持仓量
                    'open_interest': int(data[11].replace(',', '')),
                    # 增减量
                    'change_on_open_interest': int(data[12].replace(',', '')),
                    # 成交额(万元)
                    'amount': float(data[13].replace(',', '')) * 10000,
                    # DELTA
                    'delta': float(data[14].replace(',', '')),
                    # 隐含波动率
                    'implied_volatility': float(data[15].replace(',', '')),
                    # 行权量
                    'exercise': int(data[16].replace(',', '')),
                }
            )
        else:
            symbol = data[1]
            product, contract = split_symbol(symbol)
            contract = f'{year[2]}{contract}'
            result.append(
                {
                    # 交易所
                    'exchange': 'CZCE',
                    # 交易日期
                    'date': dt.date.fromisoformat(data[0]),
                    # 合约代码
                    'symbol': symbol,
                    'product': product,
                    'contract': contract,
                    # 昨结算
                    'previous_settlement': float(data[2].replace(',', '')),
                    # 今开盘
                    'open': None if data[3] == '0.00' else float(data[3].replace(',', '')),
                    # 最高价
                    'high': None if data[4] == '0.00' else float(data[4].replace(',', '')),
                    # 最低价
                    'low': None if data[5] == '0.00' else float(data[5].replace(',', '')),
                    # 今收盘
                    'close': float(data[6].replace(',', '')),
                    # 今结算
                    'settlement': float(data[7].replace(',', '')),
                    # 涨跌1
                    'change_on_close': float(data[8].replace(',', '')),
                    # 涨跌2
                    'change_on_settlement': float(data[9].replace(',', '')),
                    # 成交量(手)
                    'volume': int(data[10].replace(',', '')),
                    # 持仓量
                    'open_interest': int(data[11].replace(',', '')),
                    # 增减量
                    'change_on_open_interest': int(data[12].replace(',', '')),
                    # 成交额(万元)
                    'amount': float(data[13].replace(',', '')) * 10000,
                    # 交割结算价
                    'delivery_settlement': None
                    if data[14] == '0.00' or len(data[14]) == 0 else float(data[14].replace(',', '')),
                }
            )

    return result
