# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import List
from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.shfe import (
    download_shfe_history_data,
    download_shfe_history_data_all,
    read_shfe_history_data,
)
from InvestmentWorkshop.collector.utility import unzip_quote_file


@pytest.fixture()
def download_path() -> Path:
    """
    Return download path which configured in <CONFIGS>.
    :return: a Path-like object.
    """
    return Path(CONFIGS['path']['download'])


@pytest.fixture()
def download_year() -> int:
    """
    Generate a random year to download.
    :return: int.
    """
    return random.randint(2009, dt.date.today().year)


def test_download_shfe_history_data(download_path, download_year):
    """
    Test for <InvestmentWorkshop.collector.shfe.download_shfe_history_data>.

    1) Assert downloading a new file succeed, if variable <year> is in range [2009, <Current-Year>].
    2) Assert exception raised if variable <year> is in range [2009, <Current-Year>].

    :param download_path: Test fixture. A Path-like object, where tester save downloaded files.
    :param download_year: Test fixture. A random year to download, int.
    :return: None
    """

    # Fill the variables.
    download_file: Path = download_path.joinpath(f'SHFE_{download_year:4d}.zip')
    backup_file: Path = download_path.joinpath(f'SHFE_{download_year:4d}.zip.backup')

    # Make sure <download_file> does not exist.
    if download_file.exists():
        download_file.rename(backup_file)
    assert download_file.exists() is False

    # Do download and test.
    download_shfe_history_data(download_year)
    assert download_file.exists() is True

    # Clean up and restore.
    download_file.unlink()
    if backup_file.exists():
        backup_file.rename(download_file)


def test_download_shfe_history_data_all(download_path):
    """
    Test for <InvestmentWorkshop.collector.shfe.download_shfe_history_data_all>.

    Assert all files downloaded succeed.

    :param download_path: Test fixture. A Path-like object, where tester save downloaded files.
    :return: None
    """

    start_year: int = 2009
    this_year: int = dt.date.today().year

    download_file_name: str = 'SHFE_{year:4d}.zip'
    backup_file_name: str = 'SHFE_{year:4d}.zip.backup'
    download_file_list: List[Path] = []
    backup_file_list: List[Path] = []

    # Generate file list, and rename the existed file.
    for year in range(start_year, this_year + 1):
        download_file: Path = download_path.joinpath(download_file_name.format(year=year))
        backup_file: Path = download_path.joinpath(backup_file_name.format(year=year))
        if download_file.exists():
            download_file.rename(backup_file)
            backup_file_list.append(backup_file)
        assert download_file.exists() is False
        download_file_list.append(download_file)

    # Do download..
    download_shfe_history_data_all()

    # Test and clean up.
    for download_file in download_file_list:
        # Test.
        assert download_file.exists() is True
        # Clean up
        download_file.unlink()

    # Restore.
    for backup_file in backup_file_list:
        backup_file.rename(download_path.joinpath(backup_file.stem))


def test_read_shfe_history_data(download_path, download_year):
    """
    Test for <InvestmentWorkshop.collector.shfe.read_shfe_history_data>.

    :param download_path: Test fixture. A Path-like object, where tester save downloaded files.
    :param download_year: Test fixture. A random year to download, int.
    :return:
    """
    # Download random history quote file.
    download_file: Path = download_path.joinpath(f'SHFE_{download_year:4d}.zip')
    download_shfe_history_data(download_year)

    # Unzip.
    file_list = unzip_quote_file(download_file)

    for xls_file in file_list:
        assert xls_file.exists() is True
        result = read_shfe_history_data(xls_file)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dict)
            assert isinstance(item['symbol'], str)
            assert isinstance(item['date'], dt.date)
            assert isinstance(item['previous_close'], float)
            assert isinstance(item['previous_settlement'], float)
            if item['open'] is not None:
                assert isinstance(item['open'], float)
            if item['high'] is not None:
                assert isinstance(item['high'], float)
            if item['low'] is not None:
                assert isinstance(item['low'], float)
            assert isinstance(item['close'], float)
            assert isinstance(item['settlement'], float)
            assert isinstance(item['change_on_close'], float)
            assert isinstance(item['change_on_settlement'], float)
            assert isinstance(item['volume'], int)
            assert isinstance(item['amount'], float)
            assert isinstance(item['open_interest'], int)

        # Make clean.
        xls_file.unlink()
        assert xls_file.exists() is False

    download_file.unlink()
    assert download_file.exists() is False
