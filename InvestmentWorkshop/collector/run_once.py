# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Tuple, Any
from pathlib import Path
import datetime as dt
import csv

from .utility import uncompress_zip_file
from .cffex import download_cffex_history_data, read_cffex_history_data
from ..database import db, FuturesQuoteDaily, OptionQuoteDaily


def collect_cffex_history_data(save_path: Path) -> None:
    """
    收集中国金融期货交易所（中金所，CFFEX）的全部历史数据。
    :param save_path: 保存的位置。
    :return: None.
    """
    start_year: int = 2010
    start_month: int = 4
    today: dt.date = dt.date.today()

    # 在数据库中创建表 FuturesQuoteDaily 和 OptionQuoteDaily。
    db.create_tables([FuturesQuoteDaily, OptionQuoteDaily])

    # 按年份循环。
    for year in range(start_year, today.year + 1):
        # 按月份循环。
        for month in range(1, 12 + 1):
            # 如果是2010年4月之前（1~3月），进行下一次循环。
            if year == 2010 and month < start_month:
                continue
            # 如果超出了现在的年月，终止循环
            if year == today.year and month > today.month:
                break

            # 下载
            download_cffex_history_data(save_path=save_path, year=year, month=month)

            # 下载后保存的文件
            download_file = save_path.joinpath(f'CFFEX_{year:4d}-{month:02d}.zip')

            # 确保文件存在
            assert download_file.exists()

            # 解压缩文件，解压后删除。
            upzipped_file_list = uncompress_zip_file(zipped_file=download_file, unzip_path=save_path, keep=False)

            # 排序解压文件列表
            upzipped_file_list.sort()

            # 循环解压文件列表。
            for upzipped_file in upzipped_file_list:
                # 读取数据
                quote_futures, quote_option = read_cffex_history_data(upzipped_file)

                # 期货。
                for item in quote_futures:
                    FuturesQuoteDaily.insert(
                        symbol=item['symbol'],
                        date=item['date'],
                        open=item['open'],
                        high=item['high'],
                        low=item['low'],
                        close=item['close'],
                        settlement=item['settlement'],
                        volume=item['volume'],
                        amount=item['amount'],
                        open_interest=item['open_interest']
                    ).execute()

                # 期权。
                for item in quote_option:
                    OptionQuoteDaily.insert(
                        symbol=item['symbol'],
                        date=item['date'],
                        open=item['open'],
                        high=item['high'],
                        low=item['low'],
                        close=item['close'],
                        settlement=item['settlement'],
                        volume=item['volume'],
                        amount=item['amount'],
                        open_interest=item['open_interest'],
                        delta=item['delta']
                    ).execute()

                # 删除文件
                upzipped_file.unlink()
