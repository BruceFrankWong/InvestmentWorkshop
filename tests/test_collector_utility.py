# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import List, Tuple
from pathlib import Path

from InvestmentWorkshop.collector.utility import (
    uncompress_zip_file,
    split_symbol,
)
from InvestmentWorkshop.collector.cffex import (
    CFFEX_PATTERN_FUTURES,
    CFFEX_PATTERN_OPTION,
    get_all_cffex_history_data_parameters,
    get_cffex_history_data_local_filename,
    download_cffex_history_data,
)
from InvestmentWorkshop.collector.shfe import (
    SHFE_PATTERN_FUTURES,
    SHFE_PATTERN_OPTION,
    get_all_shfe_history_data_parameters,
    get_shfe_history_data_local_filename,
    download_shfe_history_data,
)


@pytest.mark.parametrize(
    'symbol, pattern, should_be',
    [
        ('IF2112', CFFEX_PATTERN_FUTURES, ('IF', '2112')),     # 中金所，期货
        ('T2012',  CFFEX_PATTERN_FUTURES, ('T',  '2012')),     # 中金所，期货
        ('IO2004-P-3700', CFFEX_PATTERN_OPTION, ('IO', '2004', 'P', '3700')),   # 中金所，期权

        ('cu1806', SHFE_PATTERN_FUTURES, ('cu', '1806')),     # 上期所，期货
        ('rb1907', SHFE_PATTERN_FUTURES, ('rb', '1907')),     # 上期所，期货
        ('cu1912C49000', SHFE_PATTERN_OPTION, ('cu', '1912', 'C', '49000')),   # 上期所，期权
    ]
)
def test_split_symbol(symbol: str, pattern: str, should_be: tuple):
    """
    将代码分解为品种、到期年月、方向（期权）和行权价（期权）。

    :param symbol: str，交易代码。
    :param pattern: str，用于分解交易代码的正则表达式。
    :param should_be: tuple，预计的结果。
    :return:
    """
    result = split_symbol(symbol, pattern)
    assert len(result) == len(should_be)
    for i in range(len(result)):
        assert result[i] == should_be[i]


def test_uncompress_zip_file_with_cffex(path_for_test):
    """
    Test for <collector.utility.uncompress_zip_file()>, with CFFEX。
    :param path_for_test: Path，测试固件。测试期间临时文件的路径。
    :return:
    """
    # 用中金所数据进行测试。
    parameter_list: List[Tuple[int, int]] = get_all_cffex_history_data_parameters()

    for parameter in parameter_list:
        # 转写参数。
        year: int = parameter[0]
        month: int = parameter[1]

        # 待下载文件的本地路径。
        download_file: Path = path_for_test.joinpath(
            get_cffex_history_data_local_filename(year, month)
        )

        # 确认待下载文件不存在。
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False

        # 下载。
        download_cffex_history_data(path_for_test, year, month)

        # 确认文件存在。
        assert download_file.exists() is True

        # 解压缩。
        file_list = uncompress_zip_file(download_file, path_for_test)

        # 测试
        # 确认文件被删除。
        assert download_file.exists() is False

        # Test.
        assert isinstance(file_list, list)
        for file in file_list:
            assert isinstance(file, Path)
            assert file.exists() is True

        # 清理
        for file in file_list:
            file.unlink()
            assert file.exists() is False


def test_uncompress_zip_file_with_shfe(path_for_test):
    """
    Test for <collector.utility.uncompress_zip_file()>, with SHFE。
    :param path_for_test: Path，测试固件。测试期间临时文件的路径。
    :return:
    """
    # 用上期所数据进行测试。
    parameter_list: List[int] = get_all_shfe_history_data_parameters()

    for year in parameter_list:

        # 待下载文件的本地路径。
        download_file: Path = path_for_test.joinpath(
            get_shfe_history_data_local_filename(year)
        )

        # 确认待下载文件不存在。
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False

        # 下载。
        download_shfe_history_data(path_for_test, year)

        # 确认文件存在。
        assert download_file.exists() is True

        # 解压缩。
        file_list = uncompress_zip_file(download_file, path_for_test)

        # 测试
        # 确认文件被删除。
        assert download_file.exists() is False

        # Test.
        assert isinstance(file_list, list)
        for file in file_list:
            assert isinstance(file, Path)
            assert file.exists() is True

        # 清理
        for file in file_list:
            file.unlink()
            assert file.exists() is False
