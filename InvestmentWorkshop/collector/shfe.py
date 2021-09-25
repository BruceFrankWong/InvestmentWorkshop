# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'

"""
    collect public information from SHFE.

    The earliest history data is begin:
                                    Futures,    Option
        Daily Express:              2002-01-07, 2018-09-21
        Daily Rank:                 2002-01-07, N/A
        Daily Warehouse Stocks:     2008-10-06, N/A
"""


from typing import List, Dict
from pathlib import Path
import datetime as dt

import requests
import xlrd

from ..utility import CONFIGS
from .utility import QuoteDaily, make_directory_existed, split_symbol


def download_shfe_history_data(year: int):
    """
    Download history data (yearly) from SHFE.
    :param year:
    :return:
    """

    # Define the url for history data.
    url: str = 'http://www.shfe.com.cn/historyData/MarketData_Year_{year:4d}.zip'

    # Handle the year.
    start_year: int = 2009
    if year < start_year or year > dt.date.today().year:
        raise ValueError(f'The year of SHFE history data should be in range {start_year} ~ {dt.date.today().year}.')

    # Make sure <save_path> existed.
    download_path: Path = Path(CONFIGS['path']['download'])
    make_directory_existed(download_path)

    response = requests.get(url.format(year=year))
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f'Error in downloading <{url.format(year=year)}>.')
    with open(download_path.joinpath(f'SHFE_{year:4d}.zip'), 'wb') as f:
        f.write(response.content)


def download_shfe_history_data_all():
    """
    Download all history data (yearly) from SHFE.
    :return: None
    """

    start_year: int = 2009
    this_year: int = dt.date.today().year
    for year in range(start_year, this_year + 1):
        download_shfe_history_data(year)


def read_shfe_history_data(xls_file: Path) -> List[QuoteDaily]:
    """
    Read quote data from file.
    :param xls_file: a Path-like object.
    :return: a list.
    """
    result: List[QuoteDaily] = []

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
        product, contract = split_symbol(last_symbol)
        result.append(
            {
                'exchange': 'SHFE',
                'symbol': last_symbol,
                'product': product,
                'contract': contract,
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
    return result
