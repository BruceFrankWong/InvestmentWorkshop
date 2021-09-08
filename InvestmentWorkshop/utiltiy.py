# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path


# The package name.
PACKAGE_NAME: str = 'InvestmentWorkshop'


# The package path <InvestmentWorkshop>
PACKAGE_PATH: Path = Path(__file__).parent


# Tha path of the user custom config file.
CONFIG_PATH: Path = Path.home().joinpath(f'.{PACKAGE_NAME}')
if not CONFIG_PATH.exists():
    CONFIG_PATH.mkdir()
