# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


"""
    Chan Theory
    
        procedure module
"""


from typing import List, Tuple
from pathlib import Path
import datetime as dt

import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf


def get_available_datafile_path(data_path: Path) -> Tuple[Path]:
    """
    返回可用的 <.csv> 文件。
    :param data_path:
    :return:
    """
    assert data_path.exists() is True
    result: List[Path] = [x for x in data_path.iterdir() if x.suffix == '.csv']
    return tuple(result)


def get_available_datafile_name(data_path: Path, period: 'str') -> Tuple[Tuple[str, str]]:
    """
    返回可用的 <.csv> 文件。
    :param data_path:
    :param period:
    :return:
    """
    assert data_path.exists() is True

    result: List[Tuple[str, str]] = []
    for item in data_path.iterdir():
        if item.suffix == '.csv':
            symbol, period_x = item.stem.split('_')
            if period_x == period:
                result.append((symbol, period_x))

    return tuple(result)


def load_csv_as_dataframe(data_file: Path,
                          datetime_index: bool = True) -> pd.DataFrame:
    """
    从 <.csv> 文件加载数据为 pandas.DataFrame。

    :param data_file:
    :param datetime_index:

    ----
    :return: pandas DataFrame.
    """
    if not data_file.exists():
        raise FileNotFoundError(f'{data_file} not found.')

    if datetime_index:
        return pd.read_csv(data_file, parse_dates=['datetime'], index_col=['datetime'])
    else:
        return pd.read_csv(data_file, parse_dates=['datetime'])


def save_dataframe_to_csv(csv_file_path: Path, df: pd.DataFrame):
    """

    :param csv_file_path:
    :param df:
    :return:
    """
    df.to_csv(csv_file_path, index=True)


def get_saved_filename(symbol: str, start: str, end: str) -> str:
    """
    生成保存图像的文件名
    :return:
    """
    now: dt.datetime = dt.datetime.now()
    return f'{symbol}_{start}_{end}_@{now}.png'.replace(' ', 'T').replace(':', '#')


print('Load succeed.')
