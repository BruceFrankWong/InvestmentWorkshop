# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


"""
    collect public information from CFFEX.

"""


from typing import Dict, List, Tuple, Any
from pathlib import Path
import datetime as dt
import csv

import requests

from .utility import split_symbol


# 常量定义

# 中金所历史数据开始提供日期
CFFEX_HISTORY_DATA_START_YEAR: int = 2010
CFFEX_HISTORY_DATA_START_MONTH: int = 4
CFFEX_HISTORY_DATA_START_DAY: int = 16

# 中金所交易代码的正则表达式
CFFEX_PATTERN_FUTURES: str = r'([A-Z]{1,2})([0-9]{3,4})'
CFFEX_PATTERN_OPTION: str = r'([A-Z]{1,2})([0-9]{3,4})\-([CP])\-([0-9]+)'


def check_cffex_parameter(year: int, month: int) -> None:
    """
    校验参数<year>（年份）、<month>（月份）的有效性，无效抛出异常。

    :param year:  int，年份。
    :param month: int，月份。
    :return:
    """
    # 今天的日期。
    today: dt.date = dt.date.today()

    # 如果 <month> 小于 1 或者大于 12，抛出异常。
    if month < 1 or month > 12:
        raise ValueError(f'参数 <month> 取值范围在 [1, 12]。')

    # 如果 <year> 与 <month> 早于 HISTORY_DATA_START_YEAR 与 HISTORY_DATA_START_MONTH，抛出异常。
    if year < CFFEX_HISTORY_DATA_START_YEAR or (year == CFFEX_HISTORY_DATA_START_YEAR and month < CFFEX_HISTORY_DATA_START_MONTH):
        raise ValueError(f'中金所历史数据自{CFFEX_HISTORY_DATA_START_YEAR:4d}年{CFFEX_HISTORY_DATA_START_MONTH:02d}月起开始提供。')

    # 如果 <year> 与 <month> 晚于当前年月，抛出异常。
    if year > today.year or (year == today.year and month > today.month):
        raise ValueError(f'{year:4d}年{month:02d}月是未来日期。')


def get_all_cffex_history_data_parameters() -> List[Tuple[int, int]]:
    """
    返回全部中金所历史数据的参数列表。

    :return: 一个 list，每一项都是一个 tuple。tuple 有两项，均为 int，前者是年份，后者是月份。
    """
    today: dt.date = dt.date.today()

    result: List[Tuple[int, int]] = []
    for year in range(CFFEX_HISTORY_DATA_START_YEAR, today.year + 1):
        for month in range(1, 12 + 1):
            if year == CFFEX_HISTORY_DATA_START_YEAR and month < CFFEX_HISTORY_DATA_START_MONTH:
                continue
            if year == today.year and month > today.month:
                break
            result.append((year, month))

    return result


def get_cffex_history_data_local_filename(year: int, month: int) -> str:
    """
    返回中金所历史数据文件的本地文件名字符串，避免在项目各处硬编码中金所历史数据文件名（或文件名模板）。

    参数<year>（年份）、<month>（月份）会经过校验，不再有效范围中将抛出异常。

    :param year:  int, 数据年份。
    :param month: int, 数据月份
    :return: str, local filename.
    """
    # 确认参数有效。
    check_cffex_parameter(year=year, month=month)
    return f'CFFEX_{year:4d}-{month:02d}.zip'


def download_cffex_history_data(save_path: Path, year: int, month: int) -> None:
    """
    下载中国金融期货交易所（中金所，CFFEX）的历史数据。

    :param save_path: Path，保存的位置。
    :param year: int，需要下载数据的年份。
    :param month: int，需要下载数据的月份。
    :return: None.
    """

    # 中金所历史数据 url 模板。
    url_pattern: str = 'http://www.cffex.com.cn/sj/historysj/{year:4d}{month:02d}/zip/{year:4d}{month:02d}.zip'

    # 确认参数有效。
    check_cffex_parameter(year=year, month=month)

    # 如果参数 <save_path> 不存在，引发异常。
    if not save_path.exists():
        raise FileNotFoundError(f'目录 {save_path} 不存在。')

    # 下载。
    url: str = url_pattern.format(year=year, month=month)
    response = requests.get(url)

    # 如果下载不顺利，引发异常。
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f'下载 <{url}> 时发生错误。')

    # 保存文件。
    with open(save_path.joinpath(
            get_cffex_history_data_local_filename(year=year, month=month)
    ), 'wb') as f:
        f.write(response.content)


def read_cffex_history_data(data_file: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    读取中国金融期货交易所（中金所，CFFEX）的历史交易数据 (csv 文件)。

    :param data_file: Path, 待读取的文件。
    :return: tuple, 共两项, 每一项都是一个 list，前者是期货数据, 后者是期权数据。
             list 的每一项都是一个 dict。
             dict 的 key 是 str 类型, value 是任意类型。
    """
    result_futures: List[Dict[str, Any]] = []
    result_option: List[Dict[str, Any]] = []

    # 从文件名中获得日期。
    filename: str = data_file.name[:8]
    date: dt.date = dt.date(
        year=int(filename[:4]),
        month=int(filename[4:6]),
        day=int(filename[6:8])
    )

    # 打开 <data_file> 读取数据。
    with open(data_file, mode='r', encoding='gbk') as csv_file:
        reader = csv.DictReader(csv_file)

        # 按行循环读取。
        for row in reader:
            # 忽略 <合约代码> 列为 <小计>、<合计> 的行。
            if row['合约代码'] == '小计' or row['合约代码'] == '合计':
                continue

            # 捕捉异常并打印出错的 row。
            try:
                # 合约代码，去除两端的空白（空格）
                symbol = row['合约代码'].strip()

                # 合约代码长度不超过6，期货
                if len(symbol) <= 6:
                    # 分解代码
                    symbol_tuple = split_symbol(symbol, CFFEX_PATTERN_FUTURES)

                    result_futures.append(
                        {
                            'exchange': 'CFFEX',
                            'date': date,
                            'symbol': symbol,
                            'product': symbol_tuple[0],
                            'expiration': symbol_tuple[1],
                            'open': float(row['今开盘']) if len(row['今开盘']) > 0 else 0.0,
                            'high': float(row['最高价']) if len(row['最高价']) > 0 else 0.0,
                            'low': float(row['最低价']) if len(row['最低价']) > 0 else 0.0,
                            'close': float(row['今收盘']) if len(row['今收盘']) > 0 else 0.0,
                            'settlement': float(row['今结算']),
                            'previous_settlement': float(row['前结算']),
                            'volume': int(row['成交量']) if len(row['成交量']) > 0 else 0,
                            'amount': float(row['成交金额']) if len(row['成交金额']) > 0 else 0.0,
                            'open_interest': int(float(row['持仓量'])),
                            'change_on_close': float(row['涨跌1']),
                            'change_on_settlement': float(row['涨跌2']),
                            'change_on_open_interest': int(float(row['持仓变化'])),
                        }
                    )
                # 合约代码长度超过6，期权
                else:
                    # 分解代码
                    symbol_tuple = split_symbol(symbol, CFFEX_PATTERN_OPTION)

                    result_option.append(
                        {
                            'exchange': 'CFFEX',
                            'date': date,
                            'symbol': symbol,
                            'product': symbol_tuple[0],
                            'expiration': symbol_tuple[1],
                            'offset': symbol_tuple[2],
                            'exercise_price': symbol_tuple[3],
                            'open': float(row['今开盘']) if len(row['今开盘']) > 0 else 0.0,
                            'high': float(row['最高价']) if len(row['最高价']) > 0 else 0.0,
                            'low': float(row['最低价']) if len(row['最低价']) > 0 else 0.0,
                            'close': float(row['今收盘']) if len(row['今收盘']) > 0 else 0.0,
                            'settlement': float(row['今结算']),
                            'previous_settlement': float(row['前结算']),
                            'volume': int(row['成交量']) if len(row['成交量']) > 0 else 0,
                            'amount': float(row['成交金额']) if len(row['成交金额']) > 0 else 0.0,
                            'open_interest': int(float(row['持仓量'])),
                            'change_on_close': float(row['涨跌1']),
                            'change_on_settlement': float(row['涨跌2']),
                            'change_on_open_interest': int(float(row['持仓变化'])),
                            'delta': 0.0 if row['Delta'] == '--' else float(row['Delta']),
                        }
                    )
            except ValueError:
                print(f'读取文件 {csv_file} 时发生错误。发生错误的行内容为：\n\t{row}')

    return result_futures, result_option
