# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import Dict, List
from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.dce import (
    fetch_dce_history_index,
    download_dce_history_data,
    download_dce_history_data_all,
    correct_format,
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
def start_year() -> int:
    """
    Year when DCE history data begin.
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
def download_year(start_year, this_year) -> int:
    """
    Generate a random year to download.
    :return: int.
    """
    return random.randint(start_year, this_year - 1)


def test_fetch_dce_history_index():
    result = fetch_dce_history_index()
    assert isinstance(result, dict)
    assert len(result) == (dt.date.today().year - 2006)

    for year, content in result.items():
        assert isinstance(year, int)
        assert isinstance(content, dict)
        for product, url in content.items():
            assert isinstance(product, str)
            assert isinstance(url, str)


def test_download_dce_history_data(download_path, download_year):
    dce_data_index: Dict[int, Dict[str, str]] = fetch_dce_history_index()
    download_filename_pattern: str = 'DCE_{product}_{year}.{extension_name}'
    download_file_list: List[Path] = [
        download_path.joinpath(
            download_filename_pattern.format(
                product=product,
                year=download_year,
                extension_name=dce_data_index[download_year][product].split('.')[-1]
            )
        ) for product in dce_data_index[download_year].keys()
    ]

    # Make sure <download_file_list> not existed.
    for download_file in download_file_list:
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False

    # Download.
    download_dce_history_data(download_year)

    # Test and make clean.
    for download_file in download_file_list:
        assert download_file.exists() is True
        download_file.unlink()
        assert download_file.exists() is False


def generate_download_list(download_path: Path, start_year: int, this_year: int) -> List[Path]:
    result: List[Path] = []
    dce_data_index: Dict[int, Dict[str, str]] = fetch_dce_history_index()
    download_filename_pattern: str = 'DCE_{product}_{year}.{extension_name}'
    for year in range(start_year, this_year):
        for product in dce_data_index[year].keys():
            result.append(
                download_path.joinpath(
                    download_filename_pattern.format(
                        product=product,
                        year=year,
                        extension_name=dce_data_index[year][product].split('.')[-1]
                    )
                )
            )
    return result


def test_download_dce_history_data_all(download_path, start_year, this_year):
    # Generate download list.
    download_file_list: List[Path] = generate_download_list(download_path, start_year, this_year)

    # Make sure files in <download_file_list> not existed.
    for download_file in download_file_list:
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False

    # Download.
    download_dce_history_data_all()

    # Test and make clean.
    for download_file in download_file_list:
        assert download_file.exists() is True
        download_file.unlink()
        assert download_file.exists() is False


def test_correct_format(download_path, start_year, this_year):
    # Generate download list.
    download_file_list: List[Path] = generate_download_list(download_path, start_year, this_year)

    # Make sure files in <download_file_list> not existed.
    for download_file in download_file_list:
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False

    # Download.
    download_dce_history_data_all()

    # Correct
    for file in download_file_list:
        if file.suffix == '.csv':
            with open(file=file, mode='rb') as f:
                header = f.read(4)
            result = correct_format(file)
            if result == '.xls':
                assert header == b'\x3C\x3F\x78\x6D'
            elif result == '.xlsx':
                assert header == b'\x50\x4B\x03\x04'
            elif result == '.csv':
                assert (header != b'\x3C\x3F\x78\x6D') and (header != b'\x50\x4B\x03\x04')
            else:
                raise 'Error!'
        file.unlink()
        assert file.exists() is False
