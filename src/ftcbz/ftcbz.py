#!/usr/bin/env python3

import os.path
import zipfile
import argparse
import os
import sys
import shutil
import subprocess
import abc
import tempfile


VERSION = '2.1.0'


class Error(Exception):
    '''Base exception class of this module'''


# Extractor


class Extractor(metaclass=abc.ABCMeta):
    '''ABC which to extract a input target.'''
    id = 'Extractor ID'
    description = 'Extractor description'

    class ExtractError(Error):
        '''Extract operation failed'''

    def __init__(self, **kwargs):
        pass

    @classmethod
    @abc.abstractmethod
    def check_requirement(cls):
        '''Test requirement, if failed, print message and exit'''

    @classmethod
    @abc.abstractmethod
    def fit(cls, input_path):
        '''Test the target can be process by this class'''

    @abc.abstractmethod
    def extract(self, input_path, extract_folder):
        '''
        Extract input object to a folder, extract_folder are already exists
        '''


class FolderExtractor(Extractor):
    '''Folder input dealer'''
    id = 'dir'
    description = 'process directory'

    @classmethod
    def check_requirement(cls):
        pass

    @classmethod
    def fit(cls, input_path):
        return os.path.isdir(input_path)

    def extract(self, input_path, extract_folder):
        def copytree_to_exists(src, dst):
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

        copytree_to_exists(input_path, extract_folder)


class RarExtractor(Extractor):
    id = 'rar'
    description = 'process rar & cbr data (require unrar)'

    def __init__(self, passwords=[], **kwargs):
        super().__init__()
        self.passwords = passwords

    @classmethod
    def check_requirement(cls):
        if not shutil.which('unrar'):
            print('Program "unrar" not found. Cancel')
            sys.exit()

    @classmethod
    def fit(cls, input_path):
        if not os.path.isfile(input_path):
            return False
        trash, ext = os.path.splitext(input_path)
        if ext not in ('.rar', '.cbr'):
            return False
        return True

    def extract(self, input_path, extract_folder):
        def get_cmd(input_path, extract_folder, password=None):
            '''generate one command'''
            unrar = shutil.which('unrar')
            cmd = [unrar, 'e', '-inul']
            if password:
                cmd.append('-p' + password)
            else:
                cmd.append('-p-')
            cmd.append(input_path)
            cmd.append(extract_folder + '/')
            return cmd

        def get_cmds(input_path, extract_folder):
            '''generate all commands'''
            yield get_cmd(input_path, extract_folder)  # no password version
            for password in self.passwords:
                yield get_cmd(input_path, extract_folder, password)

        # try every passwords for unrar operation
        for cmd in get_cmds(input_path, extract_folder):
            rtn = subprocess.call(cmd)
            if rtn != 10:  # password error code == 10
                break

        # varify operation success.
        if rtn != 0:
            info = '"{}" unrar failed.'.format(input_path)
            if rtn == 10:
                info = ' '.join([info, 'Passwords not match.'])
            else:
                info = ' '.join([info, 'unrar error code => {}'.format(rtn)])
            raise type(self).ExtractError(info)


# Compressor


class Compressor(metaclass=abc.ABCMeta):
    '''ABC which to compress a folder.'''
    # class CompressError(Error):
    #     '''Compress operation failed.'''

    @classmethod
    @abc.abstractmethod
    def get_final_path(cls, new_comic_folder, volume_name):
        '''calculate final path of the volumefile. '''

    @classmethod
    @abc.abstractmethod
    def compress(cls, source_folder, new_comic_folder, volume_name):
        '''compress inputfolder to outputpath

            source_folder    = A folder need to compress.
            new_comic_folder = A result container folder.
            volume_name      = A filename without extension.
            return  => compressed file path
        '''


class CbzCompressor(Compressor):
    '''cbz compressor'''
    @classmethod
    def get_final_path(cls, new_comic_folder, volume_name):
        return os.path.join(new_comic_folder, volume_name + '.cbz')

    @classmethod
    def compress(cls, source_folder, new_comic_folder, volume_name):
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


# Framework


def get_object_paths(comic_folder):
    '''return every files and folders under container folder directly.'''
    object_paths = [os.path.join(comic_folder, obj)
                    for obj in os.listdir(comic_folder)]
    return sorted(object_paths)


def convert(object_path, extractors=[], compressor=CbzCompressor,
            new_comic_folder=None, replace=False):
    '''Convert target in path by extractor and compressor

        object_path      == source path
        extractors       == list of extractor, only the x which
                           "x.fit(objpath) == True" will be used.
        compressor       == compressor
        new_comic_folder == the output comic_folder.
                            if == None, comic_folder == object_path dir
        replace          == replace already exists result files

        return => (status, final_path)
            status will be one of...
                "archived"
                    Everything done.
                "already_exists"
                    final_path already be occupied, do nothing.
                "not_fit"
                    No extractor can fit this path, do nothing.
                "extract_error"
                    Extractor internal error. failed.

    '''
    if new_comic_folder is None:
        new_comic_folder = os.path.dirname(object_path)
    os.makedirs(new_comic_folder, exist_ok=True)
    baseext = os.path.basename(object_path)
    volume_name, ext = os.path.splitext(baseext)

    compress_filepath = compressor.get_final_path(
        new_comic_folder=new_comic_folder,
        volume_name=volume_name)
    if not replace and os.path.exists(compress_filepath):
        return 'already_exists', compress_filepath

    for extractor in extractors:
        if extractor.fit(object_path):
            with tempfile.TemporaryDirectory() as tmp_dirname:
                try:
                    extractor.extract(input_path=object_path,
                                      extract_folder=tmp_dirname)
                except Extractor.ExtractError as e:
                    print(e)
                    return "extract_error", compress_filepath

                compressor.compress(
                    source_folder=tmp_dirname,
                    new_comic_folder=new_comic_folder,
                    volume_name=volume_name)
                return "archived", compress_filepath
        else:
            continue
    return "not_fit", compress_filepath


# Main Logic & User Interface


def get_used_extractors(args):
    extractors = [eclass(passwords=args.passwords)
                  for eclass in Extractor.__subclasses__()
                  if eclass.id in args.itypes]
    return extractors


def get_args():
    '''get command line args'''
    def get_all_extractors_info():
        '''collect extractors info'''
        extractors = Extractor.__subclasses__()
        infos = []
        for e in extractors:
            infos.append('{:>6} - {}'.format(e.id, e.description))
        info = '\n'.join(infos)
        ids = [e.id for e in extractors]
        return (info, ids)

    def extra_varify(args):
        if not sys.version_info >= (3, 3, 0):
            print('ftcbz required running on python>=3.3. Cancel.')
        if not (args.all or args.folders):
            print('Neither "-a ALLDIR" nor "COMICDIR" found. Cancel.\n'
                  'Use "-h" for more detail.')
            sys.exit()
        for e in get_used_extractors(args):
            e.check_requirement()

    def parse_args():
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description='Freezing some comic dirs or files'
                        ' and archive to .cbz format!')

        parser.add_argument(
            'folders', metavar='COMICDIR', type=str, nargs='*',
            help='Comic book directories.'
                 '\nEach COMICDIR contain multiple VOLUME dirs or files.'
                 '\n(which like volume1.rar or vol_1/).')

        parser.add_argument(
            '-a', '--all', metavar='ALLDIR', dest='all', type=str, nargs='+',
            help='All directories under ALLDIR directly'
                 '\nwill become COMICDIRs.')

        parser.add_argument(
            '-o', '--output-alldir', metavar='OUTPUT_ALLDIR',
            dest='output_alldir', type=str,
            help='If not assign, the result data will be generated'
                 '\nin the source dir.')

        parser.add_argument(
            '-r', '--replace', dest='replace',
            action='store_const', const=True, default=False,
            help='Replace target files if the files are already exists.')

        parser.add_argument(
            '-d', '--delete', dest='delete',
            action='store_const', const=True, default=False,
            help='Delete data source when archive complete.')

        info, ids = get_all_extractors_info()
        parser.add_argument(
            '-i', '--input-types', metavar='TYPE', dest='itypes',
            action='store', default=[FolderExtractor.id], nargs="*",
            choices=ids,
            help='\n'.join([
                'Choice some volume types you want to convert.',
                'Available types:',
                info,
                '(default: %(default)s)']))

        parser.add_argument(
            '-p', '--passwords', metavar='PW', dest='passwords',
            action='store', default=[], nargs="*",
            help='One or more unzip passwords for source files.')

        parser.add_argument(
            '-v', '--version', action='version', version=VERSION)

        args = parser.parse_args()
        return args

    args = parse_args()
    extra_varify(args)
    return args


def main():
    '''entry point'''
    def get_ori_comic_folders(args):
        """Extract all comic folders from user input."""
        def get_sub_dirs(folder):
            subdirs = [os.path.join(folder, subdir) for subdir
                       in os.listdir(folder)
                       if os.path.isdir(os.path.join(folder, subdir))]
            return sorted(subdirs)

        comic_folders = {folder for folder in args.folders}
        if args.all:
            for all_folder in args.all:
                for folder in get_sub_dirs(all_folder):
                    comic_folders.add(folder)
        return sorted(comic_folders)

    def get_new_comic_folder(args, ori_comic_folder):
        '''get new_comic_folder for convert() function'''
        if args.output_alldir:
            norm_folder = os.path.normpath(ori_comic_folder)
            basename = os.path.basename(norm_folder)
            new_comic_folder = os.path.join(args.output_alldir, basename)
        else:
            new_comic_folder = ori_comic_folder
        return new_comic_folder

    def delete_object_path(object_path):
        '''delete object path, whether it is file or dir'''
        if os.path.isdir(object_path):
            shutil.rmtree(object_path)
        elif os.path.isfile(object_path):
            os.remove(object_path)
        dirname = os.path.dirname(object_path)
        try:
            os.removedirs(dirname)
        except OSError:
            pass

    def print_info(status, object_path):
        if status != 'not_fit':
            if status == 'archived':
                info = 'Archived OK: {}'.format(object_path)
            if status == 'already_exists':
                info = 'Already Exist: {}'.format(object_path)
            if status == 'extract_error':
                info = 'Extract error: {}'.format(object_path)
            print(info)

    args = get_args()

    extractors = get_used_extractors(args)
    compressor = CbzCompressor()

    for ori_comic_folder in get_ori_comic_folders(args):
        new_comic_folder = get_new_comic_folder(args, ori_comic_folder)
        for object_path in get_object_paths(ori_comic_folder):
            status, final_path = convert(
                object_path=object_path,
                extractors=extractors,
                compressor=compressor,
                new_comic_folder=new_comic_folder,
                replace=args.replace)

            if status not in ('not_fit', 'extract_error'):
                if args.delete:
                    delete_object_path(object_path)

            print_info(status, final_path)

if __name__ == '__main__':
    main()
