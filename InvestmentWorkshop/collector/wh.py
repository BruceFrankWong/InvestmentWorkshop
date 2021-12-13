# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


"""
    Import quote data from wh6/wh7.
"""


from typing import Dict, List, Any
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import configparser
import struct
import datetime as dt


PATH_WH: Path = Path('C:\\宏源期货')

PATH_WH_DATA: Path = PATH_WH.joinpath('Data')
PATH_WH_DRAFT: Path = PATH_WH.joinpath('sys', 'CustomLine')
PATH_WH_MARKET: Path = PATH_WH.joinpath('sys', 'MarketIni')

PATH_CONTRACT_CZCE: Path = PATH_WH_MARKET.joinpath('Market2.ini')
PATH_CONTRACT_DCE: Path = PATH_WH_MARKET.joinpath('Market3.ini')
PATH_CONTRACT_SHFE1: Path = PATH_WH_MARKET.joinpath('Market4.ini')
PATH_CONTRACT_SHFE2: Path = PATH_WH_MARKET.joinpath('Market5.ini')
PATH_CONTRACT_INE: Path = PATH_WH_MARKET.joinpath('Market30.ini')
PATH_CONTRACT_CFFEX: Path = PATH_WH_MARKET.joinpath('Market47.ini')


class WhExchange(Enum):
    CFFEX = 'CFFEX'
    DCE = 'DCE'
    CZCE = 'CZCE'

    def __str__(self) -> str:
        return self.value


class WhPeriod(Enum):
    Week = {
        'name': '周',
        'directory': 'week',
        'draft': '6_0',
    }
    Day = {
        'name': '日',
        'directory': 'day',
        'draft': '6_0',
    }
    Hour2 = {
        'name': '2时',
        'directory': 'hour2',
        'draft': '55_0',
    }
    Hour1 = {
        'name': '1时',
        'directory': 'hour',
        'draft': '5_0',
    }
    Minute30 = {
        'name': '30分',
        'directory': 'min30',
        'draft': '4_0',
    }
    Minute15 = {
        'name': '15分',
        'directory': 'min15',
        'draft': '3_0',
    }
    Minute5 = {
        'name': '5分',
        'directory': 'min5',
        'draft': '2_0',
    }
    Minute3 = {
        'name': '3分',
        'directory': 'min3',
        'draft': '14_0',
    }
    Minute1 = {
        'name': '1分',
        'directory': 'min1',
        'draft': '1_0',
    }
    Second30 = {
        'name': '30秒',
        'directory': 'sec30',
        'draft': '42_0',
    }
    Second15 = {
        'name': '15秒',
        'directory': 'sec15',
        'draft': '41_0',
    }

    def __str__(self) -> str:
        return self.value['name']


PERIOD_GROUP: List[WhPeriod] = [
    WhPeriod.Week,
    WhPeriod.Day,
    WhPeriod.Hour1,
    WhPeriod.Minute30,
    WhPeriod.Minute15,
    WhPeriod.Minute5,
    WhPeriod.Minute3,
    WhPeriod.Minute1,
    WhPeriod.Second30,
    WhPeriod.Second15,
]


@dataclass
class WhQuote:
    datetime: dt.datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_interest: int
    settlement: float

    def __str__(self) -> str:
        return f'<WhQuote(' \
               f'datetime={str(self.datetime)}, ' \
               f'open={self.open}, ' \
               f'high={self.high}, ' \
               f'low={self.low}, ' \
               f'close={self.close}, volume={self.volume}, ' \
               f'open_interest={self.open_interest}, ' \
               f'settlement={self.settlement}' \
               f')>'


@dataclass
class WhLinearBase:
    identify: int
    lock: bool
    save_time: int
    rectangle_bk: int
    width: int
    color: int
    style: int
    start_pos: int
    start_time: int
    start_value: float
    stop_pos: int
    stop_time: int
    stop_value: float


@dataclass
class WhSegment(WhLinearBase):
    identify = 25
    check_hor_mark: int


@dataclass
class WhRectangle(WhLinearBase):
    identify = 45


def read_contract_code(market_config_file: Path):
    config = configparser.ConfigParser(comment_prefixes=('#', ';', '；', '\\'))
    config.read(market_config_file)
    print(config.sections())
    for k, v in config['config'].items():
        print(k, v)


def read_day_or_longer(data_file: Path):
    """
    Read WH quote data (day and more larger).

    :param data_file:
    :return:
    """
    data_pattern: struct.Struct = struct.Struct(r'<Lfffffff5x')

    assert data_file.exists() is True

    with open(data_file, 'rb') as f:
        raw = f.read()

    offset: int
    for offset in range(0, len(raw), data_pattern.size):
        unpack = data_pattern.unpack_from(raw, offset)
        yield WhQuote(
            datetime=dt.datetime.fromtimestamp(unpack[0]),
            open=unpack[1],
            close=unpack[2],
            high=unpack[3],
            low=unpack[4],
            volume=int(unpack[5]),
            open_interest=int(unpack[6]),
            settlement=unpack[7]
        )


def read_in_day(data_file: Path):
    """
    Read WH quote data (less than day).

    :param data_file:
    :return:
    """
    data_pattern: struct.Struct = struct.Struct(r'<4xLfffffff')

    assert data_file.exists() is True

    with open(data_file, 'rb') as f:
        raw = f.read()
    print(data_pattern.size)

    offset: int
    for offset in range(0, len(raw) - 4, data_pattern.size):
        unpack = data_pattern.unpack_from(raw, offset)
        x = unpack[0]
        # seconds = x / 52428800
        print(dt.datetime.fromtimestamp(x))
    print((len(raw)-4) / data_pattern.size)


def generate_watch_list() -> Dict[str, Dict[str, Any]]:
    watch_list: Dict[str, Dict[str, Any]] = {
        # 铁矿石
        'i': {
            'name': '铁矿',
            'symbol': 'rb',
            'exchange': 'SHFE',
            'directory': 'SHME',
            'contract_list': {
                '01': '57001',
                '05': '57005',
                '09': '57009',
            }
        },
        # 螺纹
        'rb': {
            'name': '螺纹',
            'symbol': 'rb',
            'exchange': 'SHFE',
            'directory': 'SHME',
            'contract_list': {
                '01': '63571',
                '05': '63575',
                '10': '63580',
            }
        },
        # 热卷
        'hc': {
            'name': '螺纹',
            'symbol': 'rb',
            'exchange': 'SHFE',
            'directory': 'SHME',
            'contract_list': {
                '01': '63571',
                '05': '63575',
                '10': '63580',
            }
        },
        # 白银
        'ag': {
            'name': '白银',
            'symbol': 'ag',
            'exchange': 'SHFE',
            'directory': 'SHME',
            'contract_list': {
                '01': '63451',
                '02': '63452',
                '06': '63456',
                '12': '63462',
            },
        },
    }
    return watch_list


def test_watch_list():
    watch_list: Dict[str, Dict[str, Any]] = generate_watch_list()
    contract_code: str = watch_list['ag']['contract_list']['12']  # 白银12

    print(f'{contract_code:>08s}.dat')

    contract_file: Path
    for period in PERIOD_GROUP:
        contract_file = PATH_WH_DATA.joinpath(
            watch_list['ag']['directory'],
            period.value['directory'],
            f'{contract_code:>08s}.dat'
        )
        # if period == WhPeriod.Week or period == WhPeriod.Day:
        #     for x in read_big(contract_file):
        #         print(x)
        # else:
        #     try_to_read(contract_file)
        print(f'{period.value["name"]:>3s}', contract_file, contract_file.exists())


def read_ag12():
    ag12_code: str = '63462'
    ag12: Path = PATH_WH_DATA.joinpath(
            'SHME',
            WhPeriod.Day.value['directory'],
            f'{ag12_code:>08s}.dat'
        )

    assert ag12.exists()

    for quote in read_day_or_longer(ag12):
        print(quote)


def generate_merged_candles_with_quote(quotes: List[WhQuote]):
    pass


if __name__ == '__main__':
    read_ag12()
    # print(dt.datetime.fromtimestamp(1607929200))
