# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from pathlib import Path
import os


@pytest.fixture()
def path_for_test() -> Path:
    """
    测试固件（Test Fixture），测试期间临时文件的路径。

    :return: Path，测试期间临时文件的路径。
    """
    result: Path = Path(os.path.abspath('')).joinpath('temp')
    if not result.exists():
        result.mkdir()
    return result
