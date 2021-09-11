# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path


def make_directory_existed(directory: Path) -> None:
    """
    Make sure <directory> is existed.
    :param directory: a Path-like object.
    :return: None
    """
    if not directory.exists():
        directory.mkdir()
