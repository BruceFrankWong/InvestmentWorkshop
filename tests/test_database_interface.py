# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict

import peewee

from InvestmentWorkshop.utility import PACKAGE_PATH, CONFIGS
from InvestmentWorkshop.database.interface import (
    create_sqlite_database,
    create_mysql_database,
    create_postgresql_database,
    create_database,
)


def test_create_sqlite_database():
    parameter: Dict[str, str] = {
        'database': str(PACKAGE_PATH.joinpath('test_database.sqlite'))
    }
    result = create_sqlite_database(parameter)
    assert isinstance(result, peewee.SqliteDatabase) is True


def test_create_mysql_database():
    """
    Test for create_mysql_database.
    """
    result = create_mysql_database(
        {
            'host': 'localhost',
            'port': '3306',
            'database': 'test_database',
            'user': 'user',
            'password': 'password'
        }
    )
    assert isinstance(result, peewee.MySQLDatabase) is True


def test_postgresql_database():
    """
    Test for create_postgresql_database.
    """
    result = create_postgresql_database(
        {
            'host': 'localhost',
            'port': '5432',
            'database': 'test_database',
            'user': 'user',
            'password': 'password'
        }
    )
    assert isinstance(result, peewee.PostgresqlDatabase) is True


def test_database_interface():
    """
    Test for database interface.
    """
    CONFIGS['database'] = {
        'driver': 'sqlite',
        'database': 'test_database.sqlite',
    }
    result = create_database()
    assert isinstance(result, peewee.SqliteDatabase)

    CONFIGS['database'] = {
        'driver': 'mysql',
        'host': 'localhost',
        'port': '3306',
        'database': 'test_database',
        'user': 'user',
        'password': 'password',
    }
    result = create_database()
    assert isinstance(result, peewee.MySQLDatabase)

    CONFIGS['database'] = {
        'driver': 'postgresql',
        'host': 'localhost',
        'port': '5432',
        'database': 'test_database',
        'user': 'user',
        'password': 'password',
    }
    result = create_database()
    assert isinstance(result, peewee.PostgresqlDatabase)