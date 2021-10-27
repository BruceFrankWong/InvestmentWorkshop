# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Tuple
from pathlib import Path
import datetime as dt

import requests
from lxml import etree

from .utility import QuoteDaily, split_symbol, QuoteType


CZCE_FUTURES_HISTORY_DATA_START_YEAR: int = 2010
CZCE_OPTION_HISTORY_DATA_START_YEAR: int = 2017

CZCE_DATA_INDEX = Tuple[Dict[int, str], Dict[int, str]]


def check_czce_parameter(year: int, type_: QuoteType) -> None:
    """
    校验参数<year>（年份）、<month>（月份）的有效性，无效抛出异常。

    :param year:  int，年份。
    :param type_:  QuoteType, 数据类型。
    :return:
    """
    # 今天的日期。
    today: dt.date = dt.date.today()

    # 如果 <year> 晚于当前年份，抛出异常。
    if year > today.year:
        raise ValueError(f'{year:4d}年是未来日期。')

    if type_ == QuoteType.Stock:
        raise ValueError(f'郑商所不支持股票交易。')
    elif type_ == QuoteType.Futures:
        # 如果 <type_> 是 <QuoteType.Futures> 且 <year> 早于 CZCE_FUTURES_HISTORY_DATA_START_YEAR，抛出异常。
        if year < CZCE_FUTURES_HISTORY_DATA_START_YEAR:
            raise ValueError(f'郑商所期货历史数据自{CZCE_FUTURES_HISTORY_DATA_START_YEAR:4d}年起开始提供。')
    elif type_ == QuoteType.Option:
        # 如果 <type_> 是 <QuoteType.Option> 且 <year> 早于 CZCE_OPTION_HISTORY_DATA_START_YEAR，抛出异常。
        if year < CZCE_OPTION_HISTORY_DATA_START_YEAR:
            raise ValueError(f'郑商所期权历史数据自{CZCE_OPTION_HISTORY_DATA_START_YEAR:4d}年起开始提供。')
    else:
        raise ValueError(f'未知行情类型。')


def fetch_czce_history_index() -> CZCE_DATA_INDEX:
    result_futures: Dict[int, str] = {}
    result_option: Dict[int, str] = {}

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
            result_option[year] = f'{url_czce}{url_list[i]}'
        else:
            result_futures[year] = f'{url_czce}{url_list[i]}'
    return result_futures, result_option


def get_czce_history_data_local_filename(year: int, type_: QuoteType) -> str:
    """
    返回郑商所历史数据文件的本地文件名字符串，避免在项目各处硬编码历史数据文件名（或文件名模板）。

    参数<year>（年份）、<month>（月份）会经过校验，不再有效范围中将抛出异常。

    :param year:  int, 数据年份。
    :param type_:  QuoteType, 数据类型。
    :return: str, local filename.
    """
    # 确认参数有效。
    check_czce_parameter(year=year, type_=type_)
    return f'CZCE_{type_.value}_{year:4d}.zip'


def download_czce_history_data(save_path: Path, year: int, type_: QuoteType):
    # Parameters handle.
    url_list = fetch_czce_history_index()

    # 确认参数有效。
    check_czce_parameter(year=year, type_=type_)

    # 如果参数 <save_path> 不存在，引发异常。
    if not save_path.exists():
        raise FileNotFoundError(f'目录 {save_path} 不存在。')

    # Download index page.
    if type_ == QuoteType.Futures:
        url: str = url_list[0][year]
    else:
        url: str = url_list[1][year]

    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f'下载 <{url}> 时发生错误。')
    with open(save_path.joinpath(
            get_czce_history_data_local_filename(year=year, type_=type_)
    ), 'wb') as f:
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
