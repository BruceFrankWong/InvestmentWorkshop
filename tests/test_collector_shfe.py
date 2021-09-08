# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from pathlib import Path

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.shfe import (
    download_shfe_history_data,
)


def test_download_shfe_history_data():
    save_path: Path = Path(CONFIGS['path']['download'])

    year: int = 2021
    download_file: Path = save_path.joinpath(f'SHFE_{year:4d}.zip')
    if download_file.exists():
        download_file.unlink()
    assert download_file.exists() is False
    download_shfe_history_data(year)
    assert download_file.exists() is True
