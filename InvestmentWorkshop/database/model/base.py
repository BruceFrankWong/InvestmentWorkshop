# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from peewee import Model

from ..interface import db


class BasicModel(Model):
    """
    The base of all the models.
    It declares the database connection, and the table name style.
    """
    class Meta:
        database = db
        legacy_table_names = False
