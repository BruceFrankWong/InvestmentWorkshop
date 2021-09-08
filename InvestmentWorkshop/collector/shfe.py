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


from pathlib import Path
import datetime as dt

import requests

from ..utility import CONFIGS


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
    save_path: Path = Path(CONFIGS['path']['download'])
    if not save_path.exists():
        save_path.mkdir()

    response = requests.get(url.format(year=year))
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f'Error in downloading <{url.format(year=year)}>.')
    with open(save_path.joinpath(f'SHFE_{year:4d}.zip'), 'wb') as f:
        f.write(response.content)
