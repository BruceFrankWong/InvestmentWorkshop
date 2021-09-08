# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path


from InvestmentWorkshop.utility import (
    PACKAGE_NAME,
    PACKAGE_PATH,
    CONFIG_PATH,
)


def test_package_name():
    assert isinstance(PACKAGE_NAME, str)
    assert PACKAGE_NAME == 'InvestmentWorkshop'


def test_package_path():
    from InvestmentWorkshop import utility
    assert PACKAGE_PATH == Path(utility.__file__).parent


def test_config_path():
    config_path: Path = Path.home().joinpath(f'.{PACKAGE_NAME}')
    assert config_path.exists() is True
    assert config_path == CONFIG_PATH
