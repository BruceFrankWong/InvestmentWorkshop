# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import List, Dict
from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.czce import (
    fetch_czce_history_index,
    download_czce_history_data,
)


@pytest.fixture()
def download_path() -> Path:
    """
    Return download path which configured in <CONFIGS>.
    :return: a Path-like object.
    """
    # Make sure the path existed.
    test_path: Path = Path(CONFIGS['path']['download'])
    if not test_path.exists():
        test_path.mkdir()
    return test_path


@pytest.fixture()
def czce_start_year() -> int:
    """
    Year when CZCE history data begin.
    :return: int.
    """
    return 2006


@pytest.fixture()
def this_year() -> int:
    """
    This year.
    :return: int.
    """
    return dt.date.today().year


@pytest.fixture()
def download_year(czce_start_year, this_year) -> int:
    """
    Generate a random year to download.
    :return: int.
    """
    return random.randint(czce_start_year, this_year - 1)


def test_fetch_czce_history_index():
    result = fetch_czce_history_index()
    assert isinstance(result, dict)

    assert len(result.keys()) == 2
    assert 'futures' in result.keys()
    assert 'option' in result.keys()

    for k1, v1 in result.items():
        assert isinstance(v1, dict)
        for k2, v2 in v1.items():
            assert isinstance(k2, int)
            assert isinstance(v2, str)


def test_download_czce_history_data(download_path, download_year):
    # Futures.
    download_file: Path = download_path.joinpath(f'CZCE_futures_{download_year:4d}.zip')

    # Make sure <download_file_list> not existed.
    if download_file.exists():
        download_file.unlink()
    assert download_file.exists() is False

    # Download.
    download_czce_history_data(download_year, 'futures')

    # Test and make clean.
    assert download_file.exists() is True
    download_file.unlink()
    assert download_file.exists() is False

    # Option.
    download_file: Path = download_path.joinpath(f'CZCE_option_{download_year:4d}.zip')

    # Make sure <download_file_list> not existed.
    if download_file.exists():
        download_file.unlink()
    assert download_file.exists() is False

    # Download.
    download_czce_history_data(download_year, 'option')

    # Test and make clean.
    assert download_file.exists() is True
    download_file.unlink()
    assert download_file.exists() is False
