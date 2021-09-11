# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Dict, Any
from pathlib import Path
import datetime as dt
import csv

import requests

from ..utility import CONFIGS
from .utility import make_directory_existed


def download_cffex_history_data(month_required: dt.date) -> None:
    """
    Download history data (monthly) from CFFEX.
    :param month_required:
    :return:
    """
    url: str = 'http://www.cffex.com.cn/sj/historysj/{year:4d}{month:02d}/zip/{year:4d}{month:02d}.zip'

    # Make sure <year> in possible range.
    start_year: int = 2010
    start_month: int = 4
    today: dt.date = dt.date.today()

    # Make sure <year> and <month> in possible range.
    year: int = month_required.year
    month: int = month_required.month
    if year < start_year or (year == start_year and month < start_month):
        raise ValueError(f'CFFEX history data is begin from {start_year}={start_month}.')
    if year > today.year or (year == today.year and month > today.month):
        raise ValueError(f'The data your required is not existed.')

    # Handle <save_path>.
    download_path: Path = Path(CONFIGS['path']['download'])
    make_directory_existed(download_path)

    # Do download.
    response = requests.get(url.format(year=year, month=month))
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f'Something wrong in downloading <{url.format(year=year, month=month)}>.'
        )

    # Write to file.
    with open(download_path.joinpath(f'CFFEX_{year:4d}-{month:02d}.zip'), 'wb') as f:
        f.write(response.content)


def download_cffex_history_data_all() -> None:
    """
    Download all history data (monthly) from CFFEX.
    :return:
    """
    start_year: int = 2010
    start_month: int = 4
    today: dt.date = dt.date.today()

    require_list: List[dt.date] = []
    for year in range(start_year, today.year + 1):
        for month in range(1, 12 + 1):
            if year == 2010 and month < start_month:
                continue
            if year == today.year and month > today.month:
                break
            require_list.append(dt.date(year=year, month=month, day=1))
    for item in require_list:
        download_cffex_history_data(item)


def read_cffex_history_data(csv_file: Path) -> List[Dict[str, Any]]:
    """
    Read quote data from file (csv).
    :param csv_file:
    :return:
    """
    result: List[Dict[str, Any]] = []

    # Handle date.
    filename: str = csv_file.name[:8]
    date: dt.date = dt.date(
        year=int(filename[:4]),
        month=int(filename[4:6]),
        day=int(filename[6:8])
    )

    # Read .csv files.
    with open(csv_file, mode='r', encoding='gbk') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['合约代码'] == '小计' or row['合约代码'] == '合计' or '-' in row['合约代码']:
                continue
            try:
                result.append(
                    {
                        'date': date,
                        'symbol': row['合约代码'].strip(),
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
            except ValueError as e:
                print(f'ERROR: in file {csv_file}.')
                print(f'Content: \n\t{row}.')
                print(e)
    return result
