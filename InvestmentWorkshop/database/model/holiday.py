# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from peewee import (
    AutoField,
    CharField,
    DateField,
    FixedCharField,
)

from .base import BasicModel


class Holiday(BasicModel):
    """
    Holiday.
    """
    id = AutoField()
    country = FixedCharField(verbose_name='国家或地区', max_length=3)
    begin = DateField(verbose_name='开始日期')
    end = DateField(verbose_name='结束日期')
    name = FixedCharField(verbose_name='节假日名称', max_length=16)
    url = CharField(verbose_name='发文URL', null=True)

    def __str__(self):
        return f'<Holiday(' \
               f'country={self.country}' \
               f'name={self.name}, ' \
               f'begin={self.begin}, ' \
               f'end={self.end}, ' \
               f'url={self.url}, ' \
               f')>'
