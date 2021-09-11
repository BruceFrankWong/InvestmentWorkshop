# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.cffex import (
    download_cffex_history_data,
)


@pytest.fixture()
def download_path() -> Path:
    """
    Return download path which configured in <CONFIGS>.
    :return: a Path-like object.
    """
    return Path(CONFIGS['path']['download'])


@pytest.fixture()
def download_date() -> dt.date:
    """
    Generate a random year and month to download.
    :return: int.
    """
    today: dt.date = dt.date.today()
    year: int = random.randint(2010, today.year)
    month: int
    if year == 2010:
        month = random.randint(4, 12)
    elif year == today.year:
        month = random.randint(1, today.month)
    else:
        month = random.randint(1, 12)
    return dt.date(
        year=year,
        month=month,
        day=1
    )


def test_download_cffex_history_data(download_path, download_date):
    """
    Test <InvestmentWorkshop.collector.shfe.download_shfe_history_data(year: int, save_path: Path)>.

    :param download_path: Test fixture. A Path-like object, where tester save downloaded files.
    :param download_date: Test fixture. A datetime.date object, which month to be downloaded to test.
    :return: None
    """
    # Test for normal.
    year: int = download_date.year
    month: int = download_date.month

    download_file: Path = download_path.joinpath(f'CFFEX_{year:4d}-{month:02d}.zip')
    if download_file.exists():
        download_file.unlink()
    assert download_file.exists() is False

    download_cffex_history_data(download_date, download_path)
    assert download_file.exists() is True

    # Test for <directory> is None.
    download_file = download_path.joinpath(f'CFFEX_{year:4d}-{month:02d}.zip')
    if download_file.exists():
        download_file.unlink()
    assert download_file.exists() is False
    download_cffex_history_data(download_date)
    assert download_file.exists()

    # Test for impossible date.
    with pytest.raises(ValueError):
        download_cffex_history_data(dt.date(year=1999, month=5, day=1))
