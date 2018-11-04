"""Ftcbz compressor."""

import os
import shutil
import abc
import zipfile

from .utils import delete_object_path


class Compressor(metaclass=abc.ABCMeta):
    """ABC which to compress a folder."""

    id = 'Compressor ID'
    description = 'Compressor description'

    @classmethod
    @abc.abstractmethod
    def get_final_path(cls, new_comic_folder, volume_name):
        """Calculate final path of the volumefile."""

    @classmethod
    @abc.abstractmethod
    def compress(cls, source_folder, new_comic_folder, volume_name):
        """Compress inputfolder to outputpath.

        If outputpath exists, always replace it:

        Args:
            source_folder    = A folder need to compress.
            new_comic_folder = A result container folder.
            volume_name      = A filename without extension.
            return  => compressed file path
        """


class CbzCompressor(Compressor):
    """Cbz compressor."""

    id = 'cbz'
    description = 'standard comic book archive format.'

    @classmethod
    def get_final_path(cls, new_comic_folder, volume_name):
        """Calculate final path of the volumefile."""
        return os.path.join(new_comic_folder, volume_name + '.cbz')

    @classmethod
    def compress(cls, source_folder, new_comic_folder, volume_name):
        """Compress inputfolder to outputpath."""
        final_path = cls.get_final_path(new_comic_folder, volume_name)
        with zipfile.ZipFile(final_path, 'w') as zfile:
            for path, dirs, filenames in os.walk(source_folder):
                for filename in filenames:
                    abs_filename = os.path.join(path, filename)
                    rel_filename = os.path.relpath(
                        abs_filename, source_folder)
                    filename_in_zip = os.path.join(volume_name, rel_filename)
                    zfile.write(abs_filename, filename_in_zip)
        return final_path


class FolderCompressor(Compressor):
    """folder compressor, do nothing but move the data."""

    id = 'dir'
    description = 'directories, useful for rollback.'

    @classmethod
    def get_final_path(cls, new_comic_folder, volume_name):
        """Calculate final path of the volumefile."""
        return os.path.join(new_comic_folder, volume_name)

    @classmethod
    def compress(cls, source_folder, new_comic_folder, volume_name):
        """Compress inputfolder to outputpath."""
        def new_source_folder(source_folder):
            """Avoid packing only one folder by another folder."""
            paths = os.listdir(source_folder)
            if len(paths) == 1:
                path0 = os.path.join(source_folder, paths[0])
                if os.path.isdir(path0):
                    source_folder = os.path.join(source_folder, path0)
            return source_folder

        final_path = cls.get_final_path(new_comic_folder, volume_name)
        if os.path.exists(final_path):
            delete_object_path(final_path)

        source_folder = new_source_folder(source_folder)

        shutil.copytree(source_folder, final_path)
        return final_path
