# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from typing import List
from pathlib import Path
import datetime as dt

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.shfe import (
    download_shfe_history_data,
    download_shfe_history_data_all,
)


def test_download_shfe_history_data():
    download_path: Path = Path(CONFIGS['path']['download'])

    year: int = 2021
    download_file: Path = download_path.joinpath(f'SHFE_{year:4d}.zip')
    if download_file.exists():
        download_file.unlink()
    assert download_file.exists() is False
    download_shfe_history_data(year)
    assert download_file.exists() is True


def test_download_shfe_history_data_all():
    start_year: int = 2009
    this_year: int = dt.date.today().year
    download_path: Path = Path(CONFIGS['path']['download'])
    download_file_list: List[Path] = []
    for year in range(start_year, this_year + 1):
        download_file = download_path.joinpath(f'SHFE_{year:4d}.zip')
        if download_file.exists():
            download_file.unlink()
        assert download_file.exists() is False
        download_file_list.append(download_file)
    download_shfe_history_data_all()
    for download_file in download_file_list:
        assert download_file.exists() is True
