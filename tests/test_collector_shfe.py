# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from pathlib import Path

from InvestmentWorkshop.collector.shfe import (
    download_shfe_history_data,
)


def test_download_shfe_history_data():
    temp_path: Path = Path.cwd().parent.joinpath('temp')
    year: int = 2021
    download_shfe_history_data(year, temp_path)
    assert temp_path.joinpath(f'SHFE_{year:4d}.zip').exists()
