# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from enum import Enum


class Exchange(Enum):
    SHSE = 'SHSE'
    SZSE = 'SZSE'
    HKEX = 'HKEX'
    CZCE = 'CZCE'
    DCE = 'DCE'
    SHFE = 'SHFE'
    CFFEX = 'CFFEX'
    INE = 'INE'


class Symbol:
    exchange: Exchange
