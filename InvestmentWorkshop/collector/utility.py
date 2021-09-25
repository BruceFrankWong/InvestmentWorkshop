# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Any, Dict, List
from pathlib import Path
import zipfile
from enum import Enum

from ..utility import CONFIGS
from ..database import db, FuturesQuoteDaily


QuoteDaily = Dict[str, Any]


class QuoteType(Enum):
    Stock = 'Stock'
    Futures = 'Futures'
    Option = 'Option'


def make_directory_existed(directory: Path) -> None:
    """
    Make sure <directory> is existed.
    :param directory: a Path-like object.
    :return: None
    """
    if not directory.exists():
        directory.mkdir()


def unzip_file(zip_file: Path) -> List[Path]:
    """
    Unzip a zip file to ten temporary directory defined in <CONFIGS>, and return the unzipped file path.
    :param zip_file:
    :return: a generator.
    """
    result: List[Path] = []
    if not zip_file.exists():
        raise FileNotFoundError('<f> not found.')

    unzip_directory: Path = Path(CONFIGS['path']['temp'])
    make_directory_existed(unzip_directory)

    # Unzip files.
    zip_file = zipfile.ZipFile(zip_file, 'r')
    zip_file.extractall(unzip_directory)

    # Change names with corrected coding.
    unzipped_file: Path
    correct_filename: Path
    for filename in zip_file.namelist():
        unzipped_file = unzip_directory.joinpath(filename)
        correct_filename = unzip_directory.joinpath(filename.encode('CP437').decode('GBK'))
        unzipped_file.rename(correct_filename)
        result.append(correct_filename)

    return result


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
