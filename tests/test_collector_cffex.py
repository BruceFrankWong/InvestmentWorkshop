# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import Dict, List, Tuple, Any
from pathlib import Path
import datetime as dt
import os.path

from InvestmentWorkshop.collector.cffex import (
    CFFEX_HISTORY_DATA_START_YEAR,
    CFFEX_HISTORY_DATA_START_MONTH,
    check_cffex_parameter,
    get_all_cffex_history_data_parameters,
    get_cffex_history_data_local_filename,
    download_cffex_history_data,
    read_cffex_history_data,
)
from InvestmentWorkshop.collector.utility import uncompress_zip_file


@pytest.mark.parametrize(
    'year, month',
    [
        (dt.date.today().year, dt.date.today().month),  # 当前测试运行时间的年、月
        (2010, 4),      # 数据开始提供的年、月
        (2019, 8),      # 常规日期
        (2008, 12),     # 早于有效时间范围，应抛出异常
        (2030, 3),      # 晚于有效时间范围，应抛出异常
        (2020, 15),     # 月份数字无效，应抛出异常
        (2020, -3),     # 月份数字无效，应抛出异常
    ]
)
def test_check_cffex_parameter(year, month):
    """
    测试 collector.cffex.check_cffex_parameter()。

    中金所的数据从2010年4月开始提供（股指期货上市），至当前测试时间的年份、月份。如果参数无效，抛出 ValueError 异常。

    :param year:  int，待下载数据的年份。
    :param month: int，待下载数据的月份。
    :return: None。
    """
    # 当前日期
    today: dt.date = dt.date.today()

    # 如果给定的月份数字无效（小于 1 或者大于 12），应该抛出异常。
    if month < 1 or month > 12:
        with pytest.raises(ValueError):
            check_cffex_parameter(year, month)

    # 如果给定的年份数字超出时间范围，应该抛出异常。
    elif year < CFFEX_HISTORY_DATA_START_YEAR or year > today.year:
        with pytest.raises(ValueError):
            check_cffex_parameter(year, month)

    # 如果给定的年份、月份数字组合起来超出时间范围（指的是2010年1~3月，当前运行测试的年份中剩余的月份），应该抛出异常。
    elif (year == CFFEX_HISTORY_DATA_START_YEAR and month < CFFEX_HISTORY_DATA_START_MONTH) or (
            year == today.year and month > today.month):
        with pytest.raises(ValueError):
            check_cffex_parameter(year, month)


def test_get_all_cffex_history_data_parameters():
    """
    测试 collector.cffex.get_all_cffex_history_data_parameters()。

    get_all_cffex_history_data_parameters() 应返回一个 list，其中每一项均为一个 tuple。
    tuple 有两项，均为 int，前者是年份，后者是月份。

    :return: None。
    """
    result = get_all_cffex_history_data_parameters()
    assert isinstance(result, list)

    # 排序
    result.sort(key=lambda x: (x[0], x[1]))

    today: dt.date = dt.date.today()

    assert result[0][0] == CFFEX_HISTORY_DATA_START_YEAR and result[0][1] == CFFEX_HISTORY_DATA_START_MONTH
    assert result[-1][0] == today.year and result[-1][1] == today.month

    count: int = 9          # HISTORY_DATA_START_YEAR (2010) 年，4月~12月，共9个。
    count += today.month    # 当前年份的数量，至当前月份。
    count += (today.year - CFFEX_HISTORY_DATA_START_YEAR - 1) * 12    # 中间相差的年份，每一年都有12个月。
    assert len(set(result)) == count


def test_get_cffex_history_data_local_filename():
    """
    测试 collector.cffex.get_cffex_history_data_local_filename()。

    get_cffex_history_data_local_filename() 应返回一个 str，长度为 17。
    格式为 <CFFEX_{year:4d}-{month:02d}.zip>。

    :return: None。
    """
    for parameter in get_all_cffex_history_data_parameters():
        year: int = parameter[0]
        month: int = parameter[1]
        result = get_cffex_history_data_local_filename(year, month)
        assert isinstance(result, str)
        assert len(result) == 17
        assert result[:6] == 'CFFEX_'
        assert result[6:10] == str(f'{year:4d}')
        assert result[10] == '-'
        assert result[11:13] == str(f'{month:02d}')
        assert result[13:] == '.zip'


def test_download_cffex_history_data(path_for_test):
    """
    测试 collector.cffex.download_cffex_history_data()。

    download_cffex_history_data() 应生成命名为 <CFFEX_<yyyy>-<mm>.zip> 的新文件，且容量大于 0。

    :param path_for_test: Path，测试固件。测试期间临时文件的路径。
    :return: None。
    """
    for parameter in get_all_cffex_history_data_parameters():
        year: int = parameter[0]
        month: int = parameter[1]

        # 应该被下载的文件。
        file_to_be_downloaded: Path = path_for_test.joinpath(
            get_cffex_history_data_local_filename(year, month)
        )

        # 如果已经有了这个文件，删除它。
        if file_to_be_downloaded.exists():
            file_to_be_downloaded.unlink()

        # 确保本地不存在这个文件。
        assert file_to_be_downloaded.exists() is False

        # 下载
        download_cffex_history_data(path_for_test, year, month)

        # 新文件存在
        assert file_to_be_downloaded.exists() is True

        # 新文件容量不为 0。
        assert os.path.getsize(file_to_be_downloaded) > 0

        # 清理文件。
        file_to_be_downloaded.unlink()
        assert file_to_be_downloaded.exists() is False


def test_read_cffex_history_data(path_for_test):
    """
    测试 collector.cffex.read_cffex_history_data()。

    :param path_for_test: Path，测试固件。测试期间临时文件的路径。
    :return: None。
    """
    for parameter in get_all_cffex_history_data_parameters():
        year: int = parameter[0]
        month: int = parameter[1]

        # 应该被下载的文件。
        file_to_be_downloaded: Path = path_for_test.joinpath(
            get_cffex_history_data_local_filename(year, month)
        )

        # 如果已经有了这个文件，删除它。
        if file_to_be_downloaded.exists():
            file_to_be_downloaded.unlink()

        # 确保本地不存在这个文件。
        assert file_to_be_downloaded.exists() is False

        # 下载
        download_cffex_history_data(path_for_test, year, month)

        # Unzip <download_file>.
        unzip_file_list: List[Path] = list(
            uncompress_zip_file(file_to_be_downloaded, path_for_test)
        )
        csv_file: Path
        for csv_file in unzip_file_list:
            assert csv_file.exists() is True

            result: Tuple[List[Dict[str, Any]], List[Dict[str, Any]]] = read_cffex_history_data(csv_file)
            assert isinstance(result, tuple)

            # 转写变量
            date_futures: List[Dict[str, Any]] = result[0]
            date_option: List[Dict[str, Any]] = result[1]

            # 期货
            for item in date_futures:
                assert isinstance(item, dict)

                assert isinstance(item['exchange'], str)
                assert item['exchange'] == 'CFFEX'

                assert isinstance(item['date'], dt.date)

                assert isinstance(item['symbol'], str)

                assert isinstance(item['product'], str)
                assert len(item['product']) <= 2

                assert isinstance(item['expiration'], str)
                assert len(item['expiration']) == 4

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

            # 期权
            for item in date_option:
                assert isinstance(item, dict)

                assert isinstance(item['exchange'], str)
                assert item['exchange'] == 'CFFEX'

                assert isinstance(item['date'], dt.date)

                assert isinstance(item['symbol'], str)

                assert isinstance(item['product'], str)
                assert len(item['product']) <= 2

                assert isinstance(item['expiration'], str)
                assert len(item['expiration']) == 4

                assert isinstance(item['offset'], str)
                assert len(item['offset']) == 1

                assert isinstance(item['exercise_price'], str)

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

            # 清理文件。
            csv_file.unlink()
            assert csv_file.exists() is False

        assert file_to_be_downloaded.exists() is False
