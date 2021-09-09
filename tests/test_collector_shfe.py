# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List
from pathlib import Path
import datetime as dt
import random

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.shfe import (
    download_shfe_history_data,
    download_shfe_history_data_all,
    make_directory_existed,
    unzip_quote_file,
)


def test_download_shfe_history_data():
    """
    Test for <InvestmentWorkshop.collector.shfe.download_shfe_history_data>.

    1) Assert downloading a new file succeed, if variable <year> is in range [2009, <Current-Year>].
    2) Assert exception raised if variable <year> is in range [2009, <Current-Year>].

    :return: None
    """

    download_path: Path = Path(CONFIGS['path']['download'])

    year: int = 2020
    download_file: Path = download_path.joinpath(f'SHFE_{year:4d}.zip')
    backup_file: Path = download_path.joinpath(f'SHFE_{year:4d}.zip.backup')

    # Make sure <download_file> does not exist.
    if download_file.exists():
        download_file.rename(backup_file)
    assert download_file.exists() is False

    # Do download and test.
    download_shfe_history_data(year)
    assert download_file.exists() is True

    # Clean up and restore.
    download_file.unlink()
    if backup_file.exists():
        backup_file.rename(download_file)


def test_download_shfe_history_data_all():
    """
    Test for <InvestmentWorkshop.collector.shfe.download_shfe_history_data_all>.

    Assert all files downloaded succeed.

    :return: None
    """

    start_year: int = 2009
    this_year: int = dt.date.today().year

    download_path: Path = Path(CONFIGS['path']['download'])
    download_file_name: str = 'SHFE_{year:4d}.zip'
    backup_file_name: str = 'SHFE_{year:4d}.zip.backup'
    download_file_list: List[Path] = []
    backup_file_list: List[Path] = []

    # Generate file list, and rename the existed file.
    for year in range(start_year, this_year + 1):
        download_file: Path = download_path.joinpath(download_file_name.format(year=year))
        backup_file: Path = download_path.joinpath(backup_file_name.format(year=year))
        if download_file.exists():
            download_file.rename(backup_file)
            backup_file_list.append(backup_file)
        assert download_file.exists() is False
        download_file_list.append(download_file)

    # Do download..
    download_shfe_history_data_all()

    # Test and clean up.
    for download_file in download_file_list:
        # Test.
        assert download_file.exists() is True
        # Clean up
        download_file.unlink()

    # Restore.
    for backup_file in backup_file_list:
        backup_file.rename(download_path.joinpath(backup_file.stem))


def test_make_directory_existed():
    """
    Test for <InvestmentWorkshop.collector.shfe.make_directory_existed>.

    :return: None.
    """
    test_path: Path = Path('E:\\a_temporary_test_path')
    if test_path.exists():
        test_path.rmdir()
    assert test_path.exists() is False

    make_directory_existed(test_path)
    assert test_path.exists() is True

    test_path.rmdir()
    assert test_path.exists() is False


def test_unzip_quote_file():
    """
    Test for <InvestmentWorkshop.collector.shfe.unzip_quote_file>.

    :return: None.
    """
    # Generate year to download.
    year: int = random.randint(2009, dt.date.today().year)

    # Fill the variables.
    download_path: Path = Path(CONFIGS['path']['download'])
    unzip_directory: Path = download_path.joinpath('unzip')
    download_file: Path = download_path.joinpath(f'SHFE_{year:4d}.zip')
    backup_file: Path = download_path.joinpath(f'SHFE_{year:4d}.zip.backup')

    # Make sure <download_file> does not exist.
    if download_file.exists():
        download_file.rename(backup_file)
    assert download_file.exists() is False

    # make sure <unzip_directory> existed and empty.
    if unzip_directory.exists():
        [x.unlink() for x in unzip_directory.iterdir()]
    else:
        unzip_directory.mkdir()
    assert unzip_directory.exists() is True

    # Download from SHFE.
    download_shfe_history_data(year)
    assert download_file.exists() is True

    # Unzip
    file_list = unzip_quote_file(download_file)

    # Test.
    for file in file_list:
        assert file.exists() is True

    # Make clean up.
    for file in file_list:
        file.unlink()
        assert file.exists() is False
    download_file.unlink()
    assert download_file.exists() is False
