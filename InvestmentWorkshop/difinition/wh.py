# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Any
from enum import Enum
from pathlib import Path
import configparser
from dataclasses import dataclass
import datetime as dt

from ..utility import CONFIGS


WH_PATH: Path = Path(CONFIGS['path']['wh'])
WH_MARKET_PATH: Path = WH_PATH.joinpath('sys', 'MarketIni')
WH_DATA_PATH: Path = WH_PATH.joinpath('Data')
WH_MARKET_FILE: Path = WH_PATH.joinpath('sys', 'MarketIndex.ini')


SUPPORTED_EXCHANGE: List[str] = [
    '上证股票',
    '深证股票',
    '郑州商品',
    '大连商品',
    '上期所一',
    '上期所二',
    '上海能源',
    '中金所',
]


class WhExchange(Enum):
    CZCE = {
        'market_ini': WH_MARKET_PATH.joinpath('Market2.ini'),
    }
    PATH_CONTRACT_DCE: Path = WH_MARKET_PATH.joinpath('Market3.ini')
    PATH_CONTRACT_SHFE1: Path = WH_MARKET_PATH.joinpath('Market4.ini')
    PATH_CONTRACT_SHFE2: Path = WH_MARKET_PATH.joinpath('Market5.ini')
    PATH_CONTRACT_INE: Path = WH_MARKET_PATH.joinpath('Market30.ini')
    PATH_CONTRACT_CFFEX: Path = WH_MARKET_PATH.joinpath('Market47.ini')


class WhPeriod(Enum):
    Month = {
        'name': '月',
        'directory': 'month',
        'draft': '8_0',
    }
    Week = {
        'name': '周',
        'directory': 'week',
        'draft': '7_0',
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


WH_PERIOD_GROUP: List[WhPeriod] = [
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
               f'open={self.open:.2f}, ' \
               f'high={self.high:.2f}, ' \
               f'low={self.low:.2f}, ' \
               f'close={self.close:.2f}, ' \
               f'volume={self.volume}, ' \
               f'open_interest={self.open_interest}, ' \
               f'settlement={self.settlement:.2f}' \
               f')>'


@dataclass
class WhLinearBase:
    identify: int
    lock: int
    save_time: int
    rectangle_bk: int
    color: int
    width: int
    style: int
    start_pos: int
    start_time: int
    start_value: float
    stop_pos: int
    stop_time: int
    stop_value: float

    def save(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'Color': self.color,
            'Identify': self.identify,
            'LinesLock': self.lock,
            'PenStyle': self.style,
            'RectangleBK': self.rectangle_bk,
            'SaveTime': self.save_time,
            'StartPos': self.start_pos,
            'StartTime': self.start_time,
            'StartValue': self.start_value,
            'StopPos': self.stop_pos,
            'StopTime': self.stop_time,
            'StopValue': self.stop_value,
            'Width': self.width
        }
        return result


@dataclass
class WhSegment(WhLinearBase):
    """
    线段。
    """
    check_hor_mark: int

    def __init__(self,
                 start_time: int,
                 start_value: float,
                 stop_time: int,
                 stop_value: float,
                 style: int = 0,
                 width: int = 1,
                 color: int = 65535
                 ) -> None:
        super().__init__(
            identify=25,
            lock=1,
            rectangle_bk=0,
            start_pos=0,
            start_time=start_time,
            start_value=start_value,
            stop_pos=0,
            stop_time=stop_time,
            stop_value=stop_value,
            style=style,
            width=width,
            color=color
        )
        self.check_mark = 0

    def save(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'CHECKHORMARK': self.check_mark,
            'Color': self.color,
            'Identify': self.identify,
            'LinesLock': self.lock,
            'PenStyle': self.style,
            'RectangleBK': self.rectangle_bk,
            'SaveTime': self.save_time,
            'StartPos': self.start_pos,
            'StartTime': self.start_time,
            'StartValue': self.start_value,
            'StopPos': self.stop_pos,
            'StopTime': self.stop_time,
            'StopValue': self.stop_value,
            'Width': self.width
        }
        return result


class WhRectangle(WhLinearBase):
    """
    矩形。
    """
    def __init__(self,
                 start_time: int,
                 start_value: float,
                 stop_time: int,
                 stop_value: float,
                 style: int = 0,
                 width: int = 1,
                 color: int = 65535
                 ) -> None:
        super().__init__(
            identify=45,
            lock=1,
            rectangle_bk=0,
            start_pos=0,
            start_time=start_time,
            start_value=start_value,
            stop_pos=0,
            stop_time=stop_time,
            stop_value=stop_value,
            style=style,
            width=width,
            color=color
        )
        self.check_mark = 0


@dataclass
class WhHorizontalLine(WhLinearBase):
    """
    横线。
    """
    check_mark: int         # 在水平线右侧标注文字（水平线位置处的价格）
    parameter_number: int

    def __init__(self,
                 time: int,
                 value: float,
                 check_mark: int = 0,
                 style: int = 0,
                 width: int = 1,
                 color: int = 65535
                 ) -> None:
        super().__init__(
            identify=39,
            lock=1,
            rectangle_bk=0,
            start_pos=0,
            start_time=time,
            start_value=value,
            stop_pos=0,
            stop_time=time,
            stop_value=value,
            style=style,
            width=width,
            color=color
        )
        self.check_mark = check_mark
        self.parameter_number = 5

    def save(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'CHECKHORMARK': self.check_mark,
            'Checks': [],
            'Color': self.color,
            'Identify': self.identify,
            'LinesLock': self.lock,
            'ParamNum': self.parameter_number,
            'PenStyle': self.style,
            'RectangleBK': self.rectangle_bk,
            'SaveTime': self.save_time,
            'StartPos': self.start_pos,
            'StartTime': self.start_time,
            'StartValue': self.start_value,
            'StopPos': self.stop_pos,
            'StopTime': self.stop_time,
            'StopValue': self.stop_value,
            'Width': self.width
        }
        return result

    def __str__(self) -> str:
        return f'<WhHorizontalLine(' \
               f'style={self.style}, ' \
               f'width={self.width}, ' \
               f'color={self.color}, ' \
               f'time={dt.datetime.fromtimestamp(self.start_time)}, ' \
               f'value={self.start_value}' \
               f')>'


@dataclass
class WhVerticalLine(WhLinearBase):
    """
    竖线。
    """

    def __init__(self,
                 time: int,
                 value: int,
                 style: int = 0,
                 width: int = 1,
                 color: int = 65535
                 ) -> None:
        super().__init__(
            identify=40,
            lock=1,
            rectangle_bk=0,
            start_pos=0,
            start_time=time,
            start_value=value,
            stop_pos=0,
            stop_time=time,
            stop_value=value,
            style=style,
            width=width,
            color=color
        )

    def __str__(self) -> str:
        return f'<WhVerticalLine(' \
               f'style={self.style}, ' \
               f'width={self.width}, ' \
               f'color={self.color}, ' \
               f'time={dt.datetime.fromtimestamp(self.start_time)}, ' \
               f'value={self.start_value}' \
               f')>'


class WhRay(WhLinearBase):
    """
    射线。
    """
    def __init__(self,
                 start_time: int,
                 start_value: float,
                 stop_time: int,
                 stop_value: float,
                 style: int = 0,
                 width: int = 1,
                 color: int = 65535
                 ) -> None:
        super().__init__(
            identify=70,
            lock=1,
            rectangle_bk=0,
            start_pos=0,
            start_time=start_time,
            start_value=start_value,
            stop_pos=0,
            stop_time=stop_time,
            stop_value=stop_value,
            style=style,
            width=width,
            color=color
        )
        self.check_mark = 0


class WhArrow(WhLinearBase):
    """
    指引线。
    """
    def __init__(self,
                 start_time: int,
                 start_value: float,
                 stop_time: int,
                 stop_value: float,
                 style: int = 0,
                 width: int = 1,
                 color: int = 65535
                 ) -> None:
        super().__init__(
            identify=71,
            lock=1,
            rectangle_bk=0,
            start_pos=0,
            start_time=start_time,
            start_value=start_value,
            stop_pos=0,
            stop_time=stop_time,
            stop_value=stop_value,
            style=style,
            width=width,
            color=color
        )


def wh_exchange():
    if not WH_MARKET_FILE.exists():
        raise FileExistsError(f'file <{WH_MARKET_FILE}> not found.')

    config = configparser.ConfigParser(comment_prefixes=('#', ';', '；', '//'))
    config.read(WH_MARKET_FILE)
    print(config.sections())


def get_wh_security_data_path(exchange: str,
                              symbol: str,
                              period: WhPeriod
                              ) -> Path:
    wh_data_path: Path
    if exchange == 'SHSE' or exchange == 'SZSE':
        wh_data_path = Path('C:\\文华6模拟版x64\\Data')
    else:
        wh_data_path = WH_DATA_PATH
    result: Path = wh_data_path.joinpath(
        exchange,
        period.value['directory'],
        f'{symbol}.dat'
    )
    return result
