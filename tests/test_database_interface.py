# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict

import peewee

from InvestmentWorkshop.utility import PACKAGE_PATH
from InvestmentWorkshop.database.interface import create_sqlite_database


def test_create_sqlite_database():
    parameter: Dict[str, str] = {
        'database': str(PACKAGE_PATH.joinpath('test_database.sqlite'))
    }
    result = create_sqlite_database(parameter)
    assert isinstance(result, peewee.SqliteDatabase) is True
