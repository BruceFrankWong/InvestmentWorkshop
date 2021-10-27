# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import Dict, List
from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.utility import uncompress_zip_file
from InvestmentWorkshop.collector.dce import (
    fetch_dce_history_index,
    download_dce_history_data,
    download_dce_history_data_all,
    correct_format,
    read_dce_history_data,
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


def _download_list_yearly(download_path: Path, download_year: int) -> List[Path]:
    """
    Generate a yearly download list.
    :return: List[Path].
    """
    result: List[Path] = []
    dce_data_index: Dict[int, Dict[str, str]] = fetch_dce_history_index()
    download_filename_pattern: str = 'DCE_{product}_{year}.{extension_name}'
    for product in dce_data_index[download_year].keys():
        result.append(
            download_path.joinpath(
                download_filename_pattern.format(
                    product=product,
                    year=download_year,
                    extension_name=dce_data_index[download_year][product].split('.')[-1]
                )
            )
        )
    return result


def _download_list_fully(download_path: Path, start_year: int, this_year: int) -> List[Path]:
    """
    Generate a fully download list.
    :return: List[Path].
    """
    result: List[Path] = []
    for year in range(start_year, this_year):
        result.extend(_download_list_yearly(download_path, year))
    return result


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
    # Generate download list.
    download_file_list: List[Path] = _download_list_yearly(download_path, download_year)

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


def test_download_dce_history_data_all(download_path, start_year, this_year):
    # Generate download list.
    download_file_list: List[Path] = _download_list_fully(download_path, start_year, this_year)

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
    download_file_list: List[Path] = _download_list_fully(download_path, start_year, this_year)

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


def test_read_dce_history_data(download_path, start_year, this_year):
    """
    A fully test.
    :param download_path:
    :param start_year:
    :param this_year:
    :return:
    """
    for year in range(start_year, this_year):
        # Generate download list.
        download_file_list: List[Path] = _download_list_yearly(download_path, year)

        # Make sure files in <download_file_list> not existed.
        for download_file in download_file_list:
            if download_file.exists():
                download_file.unlink()
            assert download_file.exists() is False

        # Download all data.
        download_dce_history_data(year)

        # Test file existed.
        for download_file in download_file_list:
            assert download_file.exists() is True

        # Get zip file list and test file list.
        test_file_list: List[Path] = []
        zip_list: List[Path] = []
        for download_file in download_file_list:
            if download_file.suffix == '.zip':
                zip_list.append(download_file)
            else:
                test_file_list.append(download_file)

        # Unzip (and rename the last unzipped file to void name repeat error).
        unzipped_file_list: List[Path] = []
        for zip_file in zip_list:
            yyyy: str = zip_file.stem.split('_')[-1]
            for unzipped_file in uncompress_zip_file(zip_file):
                new_file_path: Path = download_path.joinpath(
                    f'{unzipped_file.stem}_{yyyy}{unzipped_file.suffix}'
                )
                unzipped_file.rename(new_file_path)
                unzipped_file_list.append(new_file_path)
            zip_file.unlink()
            assert zip_file.exists() is False

        # Union file lists.
        test_file_list.extend(unzipped_file_list)

        # Correct extension name.
        corrected_test_file_list: List[Path] = []
        for test_file in test_file_list:
            if test_file.suffix == '.csv':
                extension: str = correct_format(test_file)
                if extension == '.xls' or extension == '.xlsx':
                    new_file_path = test_file.parent.joinpath(f'{test_file.stem}{extension}')
                    test_file.rename(new_file_path)
                    corrected_test_file_list.append(new_file_path)
                else:
                    corrected_test_file_list.append(test_file)
            else:
                corrected_test_file_list.append(test_file)

        # Test file existed.
        for test_file in corrected_test_file_list:
            assert test_file.exists() is True

        # Do the test.
        for test_file in corrected_test_file_list:
            result = read_dce_history_data(test_file)
            assert isinstance(result, list)
            if '期权' in test_file.stem:
                try:
                    for item in result:
                        assert isinstance(item, dict)
                        # assert len(item.keys()) == 16
                        assert isinstance(item['symbol'], str)
                        assert isinstance(item['date'], dt.date)
                        if item['open'] is not None:
                            assert isinstance(item['open'], float)
                        if item['high'] is not None:
                            assert isinstance(item['high'], float)
                        if item['low'] is not None:
                            assert isinstance(item['low'], float)
                        assert isinstance(item['close'], float)
                        assert isinstance(item['previous_settlement'], float)
                        assert isinstance(item['settlement'], float)
                        assert isinstance(item['change_on_close'], float)
                        assert isinstance(item['change_on_settlement'], float)
                        if item['delta'] is not None:
                            assert isinstance(item['delta'], float)
                        assert isinstance(item['volume'], int)
                        assert isinstance(item['open_interest'], int)
                        assert isinstance(item['change_on_open_interest'], int)
                        assert isinstance(item['amount'], float)
                        assert isinstance(item['exercise'], int)

                except RuntimeError as e:
                    print(f'Error in {test_file}, cause {e}')
            else:
                try:
                    for item in result:
                        assert isinstance(item, dict)
                        # assert len(item.keys()) == 17
                        assert isinstance(item['symbol'], str)
                        assert isinstance(item['product'], str)
                        assert len(item['product']) <= 2
                        assert isinstance(item['contract'], str)
                        assert len(item['contract']) == 4
                        assert isinstance(item['date'], dt.date)
                        if item['previous_close'] is not None:
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
                except RuntimeError as e:
                    print(f'Error in {test_file}, cause {e}.')

            test_file.unlink()
            assert test_file.exists() is False
