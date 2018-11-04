"""Ftcbz utils."""

import os
import shutil


class FtcbzError(Exception):
    """Base exception class of this module."""


def delete_object_path(object_path):
    """Delete object path, whether it is file or dir."""
    if os.path.isdir(object_path):
        shutil.rmtree(object_path)

    elif os.path.isfile(object_path):
        os.remove(object_path)

    dirname = os.path.dirname(object_path)

    try:
        os.removedirs(dirname)

    except OSError:
        pass
