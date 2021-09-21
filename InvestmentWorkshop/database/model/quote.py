# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from peewee import (
    AutoField,
    CharField,
    DateField,
    FixedCharField,
    FloatField,
    IntegerField,
    BigIntegerField,
)

from .base import BasicModel


class FuturesQuoteTick(BasicModel):
    """
    Quote of futures, tick.
    """
    id = AutoField(primary_key=True)

    exchange = CharField(verbose_name='交易所')
    product = FixedCharField(verbose_name='品种', max_length=2)
    contract = FixedCharField(verbose_name='合约', max_length=4)

    datetime = DateField(verbose_name='日期及时间，按照 北京时间 20:00 为新交易日开始计算')
    local_datetime = DateField(verbose_name='日期及时间，北京时间')
    datetime_nano = BigIntegerField(verbose_name='日期及时间，nano')

    last_price = FloatField(verbose_name='最新价')
    high_price = FloatField(verbose_name='最高价')
    low_price = FloatField(verbose_name='最低价')

    volume = IntegerField(verbose_name='成交量')
    amount = FloatField(verbose_name='成交额')
    open_interest = IntegerField(verbose_name='持仓量')

    bid_price_1 = FloatField(verbose_name='买一价')
    bid_price_2 = FloatField(verbose_name='买二价', null=True)
    bid_price_3 = FloatField(verbose_name='买三价', null=True)
    bid_price_4 = FloatField(verbose_name='买四价', null=True)
    bid_price_5 = FloatField(verbose_name='买五价', null=True)

    ask_price_1 = FloatField(verbose_name='卖一价')
    ask_price_2 = FloatField(verbose_name='卖二价', null=True)
    ask_price_3 = FloatField(verbose_name='卖三价', null=True)
    ask_price_4 = FloatField(verbose_name='卖四价', null=True)
    ask_price_5 = FloatField(verbose_name='卖五价', null=True)

    bid_volume_1 = IntegerField(verbose_name='买一量')
    bid_volume_2 = IntegerField(verbose_name='买二量', null=True)
    bid_volume_3 = IntegerField(verbose_name='买三量', null=True)
    bid_volume_4 = IntegerField(verbose_name='买四量', null=True)
    bid_volume_5 = IntegerField(verbose_name='买五量', null=True)

    ask_volume_1 = IntegerField(verbose_name='卖一量')
    ask_volume_2 = IntegerField(verbose_name='卖二量', null=True)
    ask_volume_3 = IntegerField(verbose_name='卖三量', null=True)
    ask_volume_4 = IntegerField(verbose_name='卖四量', null=True)
    ask_volume_5 = IntegerField(verbose_name='卖五量', null=True)

    open_price = FloatField(verbose_name='开盘价')
    pre_close = FloatField(verbose_name='前收盘价')
    limit_up = FloatField(verbose_name='涨停价')
    limit_down = FloatField(verbose_name='跌停价')


class FuturesQuoteBase(BasicModel):
    """
    Quote of futures, base.
    """
    exchange = CharField(verbose_name='交易所')
    product = FixedCharField(verbose_name='品种', max_length=2)
    contract = FixedCharField(verbose_name='合约', max_length=4)
    date = DateField(verbose_name='日期')
    open = FloatField(verbose_name='开盘价')
    high = FloatField(verbose_name='最高价')
    low = FloatField(verbose_name='最低价')
    close = FloatField(verbose_name='收盘价')
    volume = IntegerField(verbose_name='成交量')
    open_interest = IntegerField(verbose_name='持仓量')


class FuturesQuoteDaily(FuturesQuoteBase):
    """
    Quote of futures, daily.
    """
    id = AutoField(primary_key=True)
    amount = FloatField(verbose_name='成交额')
    settlement = FloatField(verbose_name='结算价')
