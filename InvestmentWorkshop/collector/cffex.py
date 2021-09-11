# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Optional
from pathlib import Path
import datetime as dt

import requests

from ..utility import CONFIGS
from .utility import make_directory_existed


def download_cffex_history_data(month_required: dt.date, directory: Optional[Path] = None) -> None:
    """
    Download history data (monthly) from CFFEX.
    :param month_required:
    :param directory:
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
    if directory is None:
        directory = Path(CONFIGS['path']['download'])

    # Make sure <save_path> is a directory.
    make_directory_existed(directory)

    # Do download.
    response = requests.get(url.format(year=year, month=month))
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f'Something wrong in downloading <{url.format(year=year, month=month)}>.'
        )

    # Write to file.
    with open(directory.joinpath(f'CFFEX_{year:4d}-{month:02d}.zip'), 'wb') as f:
        f.write(response.content)
