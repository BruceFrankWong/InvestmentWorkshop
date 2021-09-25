# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path
import random
import datetime as dt

from InvestmentWorkshop.utility import CONFIGS
from InvestmentWorkshop.collector.shfe import download_shfe_history_data
from InvestmentWorkshop.collector.utility import (
    make_directory_existed,
    unzip_file,
)


def test_make_directory_existed():
    """
    Test for <make_directory_existed>.
    :return: None.
    """
    test_directory: Path = Path('E:\\Temporary')

    # Make sure <test_directory> not existed.
    if test_directory.exists():
        # Remove files in <test_directory> if existed.
        [file.unlink() for file in test_directory.iterdir()]
        test_directory.rmdir()
    assert test_directory.exists() is False

    # Run <make_directory_existed>.
    make_directory_existed(test_directory)

    # Test.
    assert test_directory.exists() is True

    # Make clean.
    test_directory.rmdir()
    assert test_directory.exists() is False


def test_unzip_file():
    """
    Test for <InvestmentWorkshop.collector.utility.unzip_file>.

    :return:
    """
    # Fill the variables.
    download_path: Path = Path(CONFIGS['path']['download'])
    unzip_directory: Path = download_path.joinpath('unzip')

    # ------------------------------------------------------------
    # Test with zip file from SHFE.
    # ------------------------------------------------------------
    download_year: int = random.randint(2009, dt.date.today().year)
    download_file: Path = download_path.joinpath(f'SHFE_{download_year:4d}.zip')
    backup_file: Path = download_path.joinpath(f'SHFE_{download_year:4d}.zip.backup')

    # Make sure <download_file> does not exist.
    if download_file.exists():
        download_file.rename(backup_file)
    assert download_file.exists() is False

    # make sure <unzip_directory> existed and empty.
    if unzip_directory.exists():
        [file.unlink() for file in unzip_directory.iterdir()]
    else:
        unzip_directory.mkdir()
    assert unzip_directory.exists() is True

    # Download from SHFE.
    download_shfe_history_data(download_year)
    assert download_file.exists() is True

    # Unzip
    file_list = unzip_file(download_file)

    # Test.
    assert isinstance(file_list, list)
    for file in file_list:
        assert isinstance(file, Path)
        assert file.exists() is True

    # Make clean up.
    for file in file_list:
        file.unlink()
        assert file.exists() is False
    download_file.unlink()
    assert download_file.exists() is False
