# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import Dict, List, Tuple, Any
from pathlib import Path
import datetime as dt
import os.path

from InvestmentWorkshop.collector.shfe import (
    SHFE_HISTORY_DATA_START_YEAR,
    check_shfe_parameter,
    get_all_shfe_history_data_parameters,
    get_shfe_history_data_local_filename,
    download_shfe_history_data,
    read_shfe_history_data,
)
from InvestmentWorkshop.collector.utility import uncompress_zip_file


@pytest.mark.parametrize(
    'year',
    [
        dt.date.today().year,  # 当前测试运行时间的年、月
        2009,   # 数据开始提供的年、月
        2019,   # 常规日期
        2008,   # 早于有效时间范围，应抛出异常
        2030,   # 晚于有效时间范围，应抛出异常
    ]
)
def test_check_parameter(year):
    """
    测试 collector.shfe.check_parameter()。

    上期所的数据从2009年开始提供，至当前测试时间的年份。如果参数无效，抛出 ValueError 异常。

    :param year:  int，待下载数据的年份。
    :return: None。
    """
    # 当前日期
    today: dt.date = dt.date.today()

    # 如果给定的年份数字超出时间范围，应该抛出异常。
    if year < SHFE_HISTORY_DATA_START_YEAR or year > today.year:
        with pytest.raises(ValueError):
            check_shfe_parameter(year)


def test_get_all_history_data_parameters():
    """
    测试 collector.shfe.get_all_history_data_parameters()。

    get_all_history_data_parameters() 应返回一个 list，每一项均为 int 类型，表示年份。

    :return: None。
    """
    result = get_all_shfe_history_data_parameters()
    assert isinstance(result, list)

    # 排序
    result.sort()

    today: dt.date = dt.date.today()

    assert result[0] == SHFE_HISTORY_DATA_START_YEAR
    assert result[-1] == today.year
    assert len(set(result)) == (today.year - SHFE_HISTORY_DATA_START_YEAR + 1)


def test_get_local_history_data_filename():
    """
    测试 collector.shfe.get_local_history_data_filename()。

    get_local_history_data_filename() 应返回一个 str，长度为 17。
    格式为 <SHFE_{year:4d}.zip>。

    :return: None。
    """
    for year in get_all_shfe_history_data_parameters():
        result = get_shfe_history_data_local_filename(year)
        assert isinstance(result, str)
        assert len(result) == 13
        assert result[:5] == 'SHFE_'
        assert result[5:9] == str(f'{year:4d}')
        assert result[9:] == '.zip'


def test_download_history_data(path_for_test):
    """
    测试 collector.shfe.download_history_data()。

    download_history_data() 应生成命名为 <SHFE_<yyyy>.zip> 的新文件，且容量大于 0。

    :param path_for_test: Path，测试固件。测试期间临时文件的路径。
    :return: None。
    """
    for year in get_all_shfe_history_data_parameters():
        # 应该被下载的文件。
        file_to_be_downloaded: Path = path_for_test.joinpath(
            get_shfe_history_data_local_filename(year)
        )

        # 如果已经有了这个文件，删除它。
        if file_to_be_downloaded.exists():
            file_to_be_downloaded.unlink()

        # 确保本地不存在这个文件。
        assert file_to_be_downloaded.exists() is False

        # 下载
        download_shfe_history_data(path_for_test, year)

        # 新文件存在
        assert file_to_be_downloaded.exists() is True

        # 新文件容量不为 0。
        assert os.path.getsize(file_to_be_downloaded) > 0

        # 清理文件。
        file_to_be_downloaded.unlink()
        assert file_to_be_downloaded.exists() is False


def test_read_history_data(path_for_test):
    """
    Test for <collector.shfe.read_shfe_history_data>.

    :param path_for_test: Test fixture. A Path-like object, where tester save downloaded files.
    :return:
    """
    for year in get_all_shfe_history_data_parameters():
        # 应该被下载的文件。
        file_to_be_downloaded: Path = path_for_test.joinpath(
            get_shfe_history_data_local_filename(year)
        )

        # 如果已经有了这个文件，删除它。
        if file_to_be_downloaded.exists():
            file_to_be_downloaded.unlink()

        # 确保本地不存在这个文件。
        assert file_to_be_downloaded.exists() is False

        # 下载
        download_shfe_history_data(path_for_test, year)

        # Unzip.
        file_list = uncompress_zip_file(file_to_be_downloaded, path_for_test)

        for xls_file in file_list:
            assert xls_file.exists() is True
            result: Tuple[List[Dict[str, Any]], List[Dict[str, Any]]] = read_shfe_history_data(xls_file)
            assert isinstance(result, tuple)

            # 转写变量
            date_futures: List[Dict[str, Any]] = result[0]
            date_option: List[Dict[str, Any]] = result[1]

            for item in date_futures:
                assert isinstance(item, dict)
                assert isinstance(item['symbol'], str)
                assert isinstance(item['product'], str)
                assert len(item['product']) <= 2
                assert isinstance(item['expiration'], str)
                assert len(item['expiration']) == 4
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

            for item in date_option:
                assert isinstance(item, dict)
                assert isinstance(item['symbol'], str)
                assert isinstance(item['product'], str)
                assert len(item['product']) <= 2
                assert isinstance(item['expiration'], str)
                assert len(item['expiration']) == 4
                assert isinstance(item['offset'], str)
                assert isinstance(item['exercise_price'], str)
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

        assert file_to_be_downloaded.exists() is False
