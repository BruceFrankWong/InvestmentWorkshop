# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path

from InvestmentWorkshop.collector.utility import (
    make_directory_existed,
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
