# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path
from enum import Enum
import zipfile
import re

from ..database import db, FuturesQuoteDaily


QuoteDaily = Dict[str, Any]


class QuoteType(Enum):
    Stock = 'Stock'
    Futures = 'Futures'
    Option = 'Option'


def uncompress_zip_file(zipped_file: Path, unzip_path: Path, keep: bool = False) -> List[Path]:
    """
    解压单个 zip 文件。

    :param zipped_file: Path，待解压文件的路径。
    :param unzip_path:  Path，保存被解压出来的文件的路径。
    :param keep:        bool，取值 True 意味着保留待解压文件的话，否则解压完成后删除待解压文件。
    :return:            list，被解压出来的文件的路径（Path）的列表。
    """
    # 如果参数 <zipped_file> 不存在，引发异常。
    if not zipped_file.exists():
        raise FileNotFoundError(f'<{zipped_file}> 不存在。')

    # 如果参数 <unzip_path> 不存在，引发异常。
    if not unzip_path.exists():
        raise FileNotFoundError(f'<{unzip_path}> 不存在。')

    # 用 zipfile 模块的 ZipFile 打开待解压文件。
    zip_file = zipfile.ZipFile(zipped_file, 'r')

    # 生成解压文件列表
    result: List[Path] = [unzip_path.joinpath(filename) for filename in zip_file.namelist()]

    # 解压文件。
    zip_file.extractall(unzip_path)

    # 关闭文件。
    zip_file.close()

    # 删除待解压文件
    if not keep:
        zipped_file.unlink()

    # 返回解压出来的文件列表
    return result


def split_symbol(symbol: str, pattern: str) -> Optional[Sequence[str]]:
    """
    将代码分解为品种、到期年月、方向（期权）和行权价（期权）。

    :param symbol: str，交易代码。
    :param pattern: str，用于分解交易代码的正则表达式。
    :return:
    """
    result = re.match(pattern, symbol)
    if result:
        return result.groups()
    else:
        return None


def write_to_database(quote: List[QuoteDaily], type_: QuoteType):
    data_list: List[Any] = []
    if type_ == QuoteType.Stock:
        pass
    elif type_ == QuoteType.Futures:
        FuturesQuoteDaily.create_table()
        [
            data_list.append(
                FuturesQuoteDaily(
                    exchange=item['exchange'],
                    product=item['symbol'][:-4],
                    contract=item['symbol'][-4:],
                    date=item['date'],
                    open=item['open'],
                    high=item['high'],
                    low=item['low'],
                    close=item['close'],
                    volume=item['volume'],
                    open_interest=item['open_interest'],
                    amount=item['amount'],
                    settlement=item['settlement'],
                )
            ) for item in quote
        ]
        with db.atomic():
            FuturesQuoteDaily.bulk_create(data_list, batch_size=100)
    elif type_ == QuoteType.Option:
        pass
    else:
        raise ValueError('Unknown QuoteType value.')
