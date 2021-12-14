# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


"""
    Import quote data from wh6/wh7.
"""


from typing import Dict, List, Any, Generator
from enum import Enum
from pathlib import Path
import configparser
import struct
import datetime as dt

import pandas as pd

from ..difinition import (
    WhQuote,
    WhPeriod,
    WH_PERIOD_GROUP,
)


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


def read_contract_code(market_config_file: Path):
    config = configparser.ConfigParser(comment_prefixes=('#', ';', '；', '\\'))
    config.read(market_config_file)
    print(config.sections())
    for k, v in config['config'].items():
        print(k, v)


def read_wh_data(data_file: Path) -> Generator:
    """
    Read WH quote data.

    :param data_file: Python Path. the wh quote data file path.
    :return:
    """
    assert data_file.exists() is True

    path_string: str = str(data_file)
    data_pattern: struct.Struct
    length_fix: int
    if WhPeriod.Month.value['directory'] in path_string or \
            WhPeriod.Week.value['directory'] in path_string or \
            WhPeriod.Day.value['directory'] in path_string:
        # 周期：日、周、月
        data_pattern = struct.Struct(r'<Lfffffff5x')
        length_fix = 0
    else:
        # 周期：日内
        data_pattern = struct.Struct(r'<4xLfffffff')
        length_fix = 4

    with open(data_file, 'rb') as f:
        raw = f.read()

    offset: int
    for offset in range(0, len(raw) - length_fix, data_pattern.size):
        unpack = data_pattern.unpack_from(raw, offset)
        yield WhQuote(
            datetime=dt.datetime.fromtimestamp(unpack[0]),
            open=int(unpack[1] * 100 + 0.5) / 100,
            close=int(unpack[2] * 100 + 0.5) / 100,
            high=int(unpack[3] * 100 + 0.5) / 100,
            low=int(unpack[4] * 100 + 0.5) / 100,
            volume=int(unpack[5]),
            open_interest=int(unpack[6]),
            settlement=int(unpack[7] * 100 + 0.5) / 100
        )


def read_wh_data_as_dataframe(data_file: Path) -> pd.DataFrame:
    assert data_file.exists() is True

    path_string: str = str(data_file)
    data_pattern: struct.Struct
    length_fix: int
    if WhPeriod.Month.value['directory'] in path_string or \
            WhPeriod.Week.value['directory'] in path_string or \
            WhPeriod.Day.value['directory'] in path_string:
        # 周期：日、周、月
        data_pattern = struct.Struct(r'<Lfffffff5x')
        length_fix = 0
    else:
        # 周期：日内
        data_pattern = struct.Struct(r'<4xLfffffff')
        length_fix = 4

    with open(data_file, 'rb') as f:
        raw = f.read()

    datetime: List[dt.datetime] = []
    data: Dict[str, List[Any]] = {
        'open': [],
        'close': [],
        'high': [],
        'low': [],
        'volume': [],
        'open_interest': [],
        'settlement': []
    }
    offset: int
    for offset in range(0, len(raw) - length_fix, data_pattern.size):
        unpack = data_pattern.unpack_from(raw, offset)
        datetime.append(dt.datetime.fromtimestamp(unpack[0]))
        data['open'].append(int(unpack[1] * 100 + 0.5) / 100)
        data['close'].append(int(unpack[2] * 100 + 0.5) / 100)
        data['high'].append(int(unpack[3] * 100 + 0.5) / 100)
        data['low'].append(int(unpack[4] * 100 + 0.5) / 100)
        data['volume'].append(int(unpack[5]))
        data['open_interest'].append(int(unpack[6]))
        data['settlement'].append(int(unpack[7] * 100 + 0.5) / 100)

    result: pd.DataFrame = pd.DataFrame(data, index=datetime)

    return result
