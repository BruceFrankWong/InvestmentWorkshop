# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict
from pathlib import Path

from peewee import (
    SqliteDatabase,
)


def create_sqlite_database(settings: Dict[str, str]) -> SqliteDatabase:
    return SqliteDatabase(
        Path(settings['database']),
        pragmas={
            'journal_mode': 'wal',
            'encoding': 'utf8',
            'cache_size': -640000,  # 64MB
            'foreign_keys': 1,  # Enforce foreign-key constraints
        }
    )
