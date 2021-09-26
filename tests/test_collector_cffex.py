# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import List
from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.utility import unzip_file
from InvestmentWorkshop.collector.cffex import (
    download_cffex_history_data,
    download_cffex_history_data_all,
    read_cffex_history_data,
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

    download_cffex_history_data(download_date)
    assert download_file.exists() is True

    # Test for impossible date.
    with pytest.raises(ValueError):
        download_cffex_history_data(dt.date(year=1999, month=5, day=1))

    # make clean.
    download_file.unlink()
    assert download_file.exists() is False


def test_download_cffex_history_data_all():
    """
    Test for <download_cffex_history_data_all>.
    :return:
    """
    # Generate files.
    start_year: int = 2010
    start_month: int = 4
    today: dt.date = dt.date.today()

    download_path = Path(CONFIGS['path']['download'])
    file_list: List[Path] = []
    require_list: List[dt.date] = []
    for year in range(start_year, today.year + 1):
        for month in range(1, 12 + 1):
            if year == 2010 and month < start_month:
                continue
            if year == today.year and month > today.month:
                break
            require_list.append(dt.date(year=year, month=month, day=1))
            file_list.append(
                download_path.joinpath(
                    f'CFFEX_{year:4d}-{month:02d}.zip'
                )
            )

    # Make sure file not existed.
    for download_file in file_list:
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False

    # Download.
    download_cffex_history_data_all()

    # Assert download succeed.
    for download_file in file_list:
        assert download_file.exists() is True

    # make clean.
    for download_file in file_list:
        download_file.unlink()
        assert download_file.exists() is False


def test_read_cffex_history_data(download_date, download_path):
    """
    Test for <read_cffex_history_data>.
    :return:
    """
    # Generate a random CFFEX history data file.
    year: int = download_date.year
    month: int = download_date.month

    # Assert <download_file> not existed.
    download_file: Path = download_path.joinpath(f'CFFEX_{year:4d}-{month:02d}.zip')
    assert download_file.exists() is False

    # Download.
    download_cffex_history_data(download_date)

    # Assert <download_file> existed.
    assert download_file.exists() is True

    # Unzip <download_file>.
    unzip_file_list: List[Path] = list(unzip_file(download_file))
    csv_file: Path
    for csv_file in unzip_file_list:
        assert csv_file.exists() is True

        result = read_cffex_history_data(csv_file)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dict)
            assert isinstance(item['symbol'], str)
            assert isinstance(item['product'], str)
            assert len(item['product']) <= 2
            assert isinstance(item['contract'], str)
            assert len(item['contract']) == 4
            assert isinstance(item['date'], dt.date)
            assert isinstance(item['previous_settlement'], float)
            assert isinstance(item['open'], float)
            assert isinstance(item['high'], float)
            assert isinstance(item['low'], float)
            assert isinstance(item['close'], float)
            assert isinstance(item['settlement'], float)
            assert isinstance(item['change_on_close'], float)
            assert isinstance(item['change_on_settlement'], float)
            assert isinstance(item['volume'], int)
            assert isinstance(item['amount'], float)
            assert isinstance(item['open_interest'], int)
            assert isinstance(item['change_on_open_interest'], int)

    # make clean.
    for csv_file in unzip_file_list:
        csv_file.unlink()
        assert csv_file.exists() is False
    download_file.unlink()
    assert download_file.exists() is False
