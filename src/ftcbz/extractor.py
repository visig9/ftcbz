"""Ftcbz extractor."""

import os
import abc
import shutil
import zipfile
import sys
import subprocess

from .utils import FtcbzError


class ExtractError(FtcbzError):
    """Extract operation failed."""


class Extractor(metaclass=abc.ABCMeta):
    """ABC which to extract a input target."""

    id = 'Extractor ID'
    description = 'Extractor description'

    def __init__(self, *args, **kwargs):
        """Init."""

    @classmethod
    def check_requirement(cls):
        """Test requirement, if failed, print message and exit."""

    @classmethod
    @abc.abstractmethod
    def fit(cls, input_path):
        """Test the target can be process by this class."""

    @abc.abstractmethod
    def extract(self, input_path, extract_folder):
        """Extract input to a folder, extract_folder are already exists."""


class FolderExtractor(Extractor):
    """Folder input dealer."""

    id = 'dir'
    description = 'directories'

    @classmethod
    def fit(cls, input_path):
        """Test the target can be process by this class."""
        return os.path.isdir(input_path)

    def extract(self, input_path, extract_folder):
        """Extract input to a folder, extract_folder are already exists."""
        def copytree_to_exists(src, dst):
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

        copytree_to_exists(input_path, extract_folder)


class ZipExtractor(Extractor):
    """Zip Extractor."""

    id = 'zip'
    description = 'zip & cbz data files'

    def __init__(self, passwords=None, **kwargs):
        """Init."""
        self.passwords = [] if passwords is None else passwords

    @classmethod
    def fit(cls, input_path):
        """Test the target can be process by this class."""
        if not os.path.isfile(input_path):
            return False
        trash, ext = os.path.splitext(input_path)
        if ext not in ('.zip', '.cbz'):
            return False
        return True

    def extract(self, input_path, extract_folder):
        """Extract input to a folder, extract_folder are already exists."""
        with zipfile.ZipFile(input_path, 'r') as zfile:
            pwd_list = [None]
            pwd_list.extend([p.encode() for p in self.passwords])
            for pwd in pwd_list:
                try:
                    zfile.extractall(extract_folder, pwd=pwd)
                    return
                except RuntimeError:
                    continue


class RarExtractor(Extractor):
    """Zip Extractor."""

    id = 'rar'
    description = 'rar & cbr data files (require unrar)'

    def __init__(self, passwords=None, **kwargs):
        """Init."""
        super().__init__()
        self.passwords = [] if passwords is None else passwords

    @classmethod
    def check_requirement(cls):
        """Test requirement, if failed, print message and exit."""
        if not shutil.which('unrar'):
            print('Program "unrar" not found. Cancel')
            sys.exit()

    @classmethod
    def fit(cls, input_path):
        """Test the target can be process by this class."""
        if not os.path.isfile(input_path):
            return False
        trash, ext = os.path.splitext(input_path)
        if ext not in ('.rar', '.cbr'):
            return False
        return True

    def extract(self, input_path, extract_folder):
        """Extract input to a folder, extract_folder are already exists."""
        def get_cmd(input_path, extract_folder, password=None):
            """Generate one command."""
            unrar = shutil.which('unrar')
            cmd = [unrar, 'x', '-inul']
            if password:
                cmd.append('-p' + password)
            else:
                cmd.append('-p-')
            cmd.append(input_path)
            cmd.append(extract_folder + '/')
            return cmd

        def get_cmds(input_path, extract_folder):
            """Generate all commands."""
            yield get_cmd(input_path, extract_folder)  # no password version
            for password in self.passwords:
                yield get_cmd(input_path, extract_folder, password)

        # try every passwords for unrar operation
        for cmd in get_cmds(input_path, extract_folder):
            rtn = subprocess.call(cmd)
            if rtn not in (10, 3):  # password error code == 10, 3
                break

        # varify operation success.
        if rtn != 0:
            info = '"{}" unrar failed.'.format(input_path)
            if rtn == 10:
                info = ' '.join([info, 'Passwords not match.'])
            else:
                info = ' '.join([info, 'unrar error code => {}'.format(rtn)])
            raise ExtractError(info)
