# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'

"""
    collect public information from SHFE.
"""


from typing import Dict, List, Tuple, Any
from pathlib import Path
import datetime as dt

import requests
import xlrd

from .utility import split_symbol


# 常量定义

# 历史数据开始提供日期
SHFE_HISTORY_DATA_START_YEAR: int = 2009

# 期货交易日报
SHFE_FUTURES_DAILY_EXPRESS_START: dt.date = dt.date.fromisoformat('2002-01-07')
# 期权交易日报
SHFE_OPTION_DAILY_EXPRESS_START: dt.date = dt.date.fromisoformat('2018-09-21')

# 期货持仓排名
SHFE_FUTURES_POSITION_RANK_START: dt.date = dt.date.fromisoformat('2002-01-07')

# 仓单
SHFE_WAREHOUSE_STOCKS_START: dt.date = dt.date.fromisoformat('2008-10-06')

# 交易代码的正则表达式
SHFE_PATTERN_FUTURES: str = r'([a-z]{1,2})([0-9]{3,4})'
SHFE_PATTERN_OPTION: str = r'([a-z]{1,2})([0-9]{3,4})([CP])([0-9]+)'


def check_shfe_parameter(year: int) -> None:
    """
    校验参数<year>（年份）的有效性，无效抛出异常。

    :param year:  int，年份。
    :return:
    """
    # 今天的日期。
    today: dt.date = dt.date.today()

    # 如果 <year> 早于 HISTORY_DATA_START_YEAR，抛出异常。
    if year < SHFE_HISTORY_DATA_START_YEAR or year > today.year:
        raise ValueError(f'上期所历史数据自{SHFE_HISTORY_DATA_START_YEAR:4d}年起开始提供。')

    # 如果 <year> 晚于当前年月，抛出异常。
    if year > today.year:
        raise ValueError(f'{year:4d}年是未来日期。')


def get_all_shfe_history_data_parameters() -> List[int]:
    """
    返回全部上期所历史数据的参数列表。

    :return: 一个 list，每一项都是一个 int，表示年份。
    """
    today: dt.date = dt.date.today()
    return [year for year in range(SHFE_HISTORY_DATA_START_YEAR, today.year + 1)]


def get_shfe_history_data_local_filename(year: int) -> str:
    """
    返回上期所历史数据文件的本地文件名字符串，避免在项目各处硬编码历史数据文件名（或文件名模板）。

    参数<year>（年份）、<month>（月份）会经过校验，不再有效范围中将抛出异常。

    :param year:  int, 数据年份。
    :return: str, local filename.
    """
    # 确认参数有效。
    check_shfe_parameter(year=year)
    return f'SHFE_{year:4d}.zip'


def download_shfe_history_data(save_path: Path, year: int):
    """
    下载上期所的历史数据。

    :param save_path: Path，保存的位置。
    :param year: int，需要下载数据的年份。
    :return: None.
    """

    # 上期所历史数据 url 模板。
    url_pattern: str = 'http://www.shfe.com.cn/historyData/MarketData_Year_{year:4d}.zip'

    # 校验参数。
    check_shfe_parameter(year)

    # 如果参数 <save_path> 不存在，引发异常。
    if not save_path.exists():
        raise FileNotFoundError(f'目录 {save_path} 不存在。')

    # 下载。
    url: str = url_pattern.format(year=year)
    response = requests.get(url)

    # 如果下载不顺利，引发异常。
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f'下载 <{url}> 时发生错误。')

    # 保存文件。
    with open(save_path.joinpath(
            get_shfe_history_data_local_filename(year=year)
    ), 'wb') as f:
        f.write(response.content)


def read_shfe_history_data(xls_file: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Read history quote data from file.
    :param xls_file: a Path-like object.
    :return: a list.
    """
    result_futures: List[Dict[str, Any]] = []
    result_option: List[Dict[str, Any]] = []

    # Read .xls files.
    workbook = xlrd.open_workbook(xls_file)
    data_sheet = workbook.sheet_by_index(0)

    xls_column_list: List[str] = [x.value for x in data_sheet.row(2)]
    mapper: Dict[str, int] = {
        'symbol': xls_column_list.index('合约'),
        'date': xls_column_list.index('日期'),
        'previous_close': xls_column_list.index('前收盘'),
        'previous_settlement': xls_column_list.index('前结算'),
        'open': xls_column_list.index('开盘价'),
        'high': xls_column_list.index('最高价'),
        'low': xls_column_list.index('最低价'),
        'close': xls_column_list.index('收盘价'),
        'settlement': xls_column_list.index('结算价'),
        'change_on_close': xls_column_list.index('涨跌1'),
        'change_on_settlement': xls_column_list.index('涨跌2'),
        'volume': xls_column_list.index('成交量'),
        'amount': xls_column_list.index('成交金额'),
        'open_interest': xls_column_list.index('持仓量'),
    }

    i: int
    last_symbol: str = ''
    for i in range(3, data_sheet.nrows - 5):
        row = data_sheet.row(i)
        if row[mapper['date']].value == 'Date':
            continue
        if row[mapper['symbol']].ctype != 0:
            last_symbol = row[mapper['symbol']].value

        if len(last_symbol) <= 6:
            symbol_dict = split_symbol(last_symbol, SHFE_PATTERN_FUTURES)
            result_futures.append(
                {
                    'exchange': 'SHFE',
                    'symbol': last_symbol,
                    'product': symbol_dict[0],
                    'expiration': symbol_dict[1],
                    'date': dt.date(
                        year=int(row[mapper['date']].value[:4]),
                        month=int(row[mapper['date']].value[4:6]),
                        day=int(row[mapper['date']].value[6:8])
                    ),

                    'previous_close': row[mapper['previous_close']].value
                    if row[mapper['settlement']].ctype != 0 else None,

                    'previous_settlement': row[mapper['previous_settlement']].value
                    if row[mapper['settlement']].ctype != 0 else None,

                    'open': row[mapper['open']].value if row[mapper['open']].ctype != 0 else None,
                    'high': row[mapper['high']].value if row[mapper['high']].ctype != 0 else None,
                    'low': row[mapper['low']].value if row[mapper['low']].ctype != 0 else None,
                    'close': row[mapper['close']].value if row[mapper['close']].ctype != 0 else None,
                    'settlement': row[mapper['settlement']].value if row[mapper['settlement']].ctype != 0 else None,

                    'change_on_close': row[mapper['change_on_close']].value
                    if row[mapper['change_on_close']].ctype != 0 else None,
                    'change_on_settlement': row[mapper['change_on_settlement']].value
                    if row[mapper['change_on_settlement']].ctype != 0 else None,

                    'volume': int(row[mapper['volume']].value)
                    if row[mapper['volume']].ctype != 0 else None,

                    'amount': row[mapper['amount']].value
                    if row[mapper['amount']].ctype != 0 else None,

                    'open_interest': int(row[mapper['open_interest']].value)
                    if row[mapper['open_interest']].ctype != 0 else None,
                }
            )
        else:
            symbol_dict = split_symbol(last_symbol, SHFE_PATTERN_OPTION)
            result_option.append(
                {
                    'exchange': 'SHFE',
                    'symbol': last_symbol,
                    'product': symbol_dict[0],
                    'expiration': symbol_dict[1],
                    'offset': symbol_dict[2],
                    'exercise_price': symbol_dict[3],
                    'date': dt.date(
                        year=int(row[mapper['date']].value[:4]),
                        month=int(row[mapper['date']].value[4:6]),
                        day=int(row[mapper['date']].value[6:8])
                    ),

                    'previous_close': row[mapper['previous_close']].value
                    if row[mapper['settlement']].ctype != 0 else None,

                    'previous_settlement': row[mapper['previous_settlement']].value
                    if row[mapper['settlement']].ctype != 0 else None,

                    'open': row[mapper['open']].value if row[mapper['open']].ctype != 0 else None,
                    'high': row[mapper['high']].value if row[mapper['high']].ctype != 0 else None,
                    'low': row[mapper['low']].value if row[mapper['low']].ctype != 0 else None,
                    'close': row[mapper['close']].value if row[mapper['close']].ctype != 0 else None,
                    'settlement': row[mapper['settlement']].value if row[mapper['settlement']].ctype != 0 else None,

                    'change_on_close': row[mapper['change_on_close']].value
                    if row[mapper['change_on_close']].ctype != 0 else None,
                    'change_on_settlement': row[mapper['change_on_settlement']].value
                    if row[mapper['change_on_settlement']].ctype != 0 else None,

                    'volume': int(row[mapper['volume']].value)
                    if row[mapper['volume']].ctype != 0 else None,

                    'amount': row[mapper['amount']].value
                    if row[mapper['amount']].ctype != 0 else None,

                    'open_interest': int(row[mapper['open_interest']].value)
                    if row[mapper['open_interest']].ctype != 0 else None,
                }
            )
    return result_futures, result_option
