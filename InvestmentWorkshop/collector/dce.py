# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Any, Optional
import datetime as dt
from pathlib import Path
import csv

import requests
from lxml import etree
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet.dimensions import SheetDimension
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string

from ..utility import CONFIGS
from .utility import unzip_quote_file


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


def download_dce_history_data_all() -> None:
    start_year: int = 2006
    this_year: int = dt.date.today().year
    for year in range(start_year, this_year):
        download_dce_history_data(year)


def correct_format(file_path: Path) -> str:
    """
    Return the correct file format.
    :param file_path: a Path-like object.
    :return: str.
    """
    if file_path.suffix == '.csv':
        with open(file=file_path, mode='rb') as csv_file:
            header = csv_file.read(4)
        # .xlsx
        if header == b'\x50\x4B\x03\x04':
            return '.xlsx'
        # .xls
        if header == b'\x3C\x3F\x78\x6D':
            return '.xls'
    return '.csv'


def read_dce_history_data_xlsx(xlsx_file: Path) -> List[Dict[str, Any]]:
    """
    Read quote data from .xlsx file.
    :param xlsx_file: a Path-like object.
    :return: a list object, each item is a dict, and the keys is:
        'symbol',
        'date',
        'previous_close',
        'previous_settlement',
        'open',
        'high',
        'low',
        'close',
        'settlement',
        'change_on_close',
        'change_on_settlement',
        'volume',
        'amount',
        'open_interest',
    """
    result: List[Dict[str, Any]] = []
    assert xlsx_file.exists() is True
    workbook: Workbook = load_workbook(filename=xlsx_file)
    worksheet: Worksheet = workbook.active
    column_max: str
    row_max: int
    column_max, row_max = coordinate_from_string(worksheet.dimensions.split(':')[1])
    for row in range(2, row_max):
        day: str = str(worksheet[f'D{row}'].value)
        if day is None:
            break
        price_open: float = float(worksheet[f'G{row}'].value)
        price_high: float = float(worksheet[f'H{row}'].value)
        price_low: float = float(worksheet[f'I{row}'].value)
        result.append(
            {
                'symbol': worksheet[f'C{row}'].value,
                'date': dt.date(
                    year=int(day[:4]),
                    month=int(day[4:6]),
                    day=int(day[6:8]),
                ),
                'previous_close': float(worksheet[f'E{row}'].value),
                'previous_settlement': float(worksheet[f'F{row}'].value),
                'open': price_open if price_open != 0.0 else None,
                'high': price_high if price_high != 0.0 else None,
                'low': price_low if price_low != 0.0 else None,
                'close': float(worksheet[f'J{row}'].value),
                'settlement': float(worksheet[f'K{row}'].value),
                'change_on_close': float(worksheet[f'L{row}'].value),
                'change_on_settlement': float(worksheet[f'M{row}'].value),
                'volume': int(float(worksheet[f'N{row}'].value)),
                'amount': float(worksheet[f'O{row}'].value),
                'open_interest': int(float(worksheet[f'P{row}'].value)),
            }
        )
    return result


def read_dce_history_data_csv(csv_file: Path) -> List[Dict[str, Any]]:
    assert csv_file.exists() is True
    result: List[Dict[str, Any]] = []
    with open(csv_file, mode='r', encoding='gbk') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            result.append(
                {
                    'date': dt.date(
                        year=int(row['日期'][:4]),
                        month=int(row['日期'][4:6]),
                        day=int(row['日期'][6:8])
                    ),
                    'symbol': row['合约'].strip(),
                    'open': None if row['开盘价'] == '0' else float(row['开盘价']),
                    'high': None if row['最高价'] == '0' else float(row['最高价']),
                    'low': None if row['最低价'] == '0' else float(row['最低价']),
                    'close': float(row['收盘价']),
                    'settlement': float(row['结算价']),
                    'previous_close': float(row['前收盘价']),
                    'previous_settlement': float(row['前结算价']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交金额']),
                    'open_interest': int(float(row['持仓量'])),
                    'change_on_close': float(row['涨跌1']),
                    'change_on_settlement': float(row['涨跌2']),
                }
            )
    return result


def read_dce_history_data(data_file: Path) -> List[Dict[str, Any]]:
    assert data_file.exists() is True
    extension: str = data_file.suffix
    if extension == '.csv':
        if correct_format(data_file) == 'csv':
            return read_dce_history_data_csv(data_file)
        elif correct_format(data_file) == 'xlsx':
            return read_dce_history_data_xlsx(data_file)
        else:
            raise RuntimeError(f'Unknown file type. {data_file}')
    elif extension == '.xlsx':
        return read_dce_history_data_xlsx(data_file)
    else:
        raise RuntimeError(f'Unknown file type. {data_file}')
