#!/usr/bin/env python3

import os.path
import zipfile
import argparse
import os
import sys
import shutil


VERSION = '1.1.2'


def get_args():
    '''get command line args'''
    parser = argparse.ArgumentParser(
            description='Assign some comic dirs and archive to .cbz format.')
    parser.add_argument('folders', metavar='COMICDIR',
            type=str, nargs='*',
            help='A comic book folders.'
                 ' Each COMICDIR contain multiple "volume dirs".')
    parser.add_argument('--delete', dest='delete',
            action='store_const', const=True, default=False,
            help='Delete "volume dir" after the archive complete.')
    parser.add_argument('--all', metavar='FOLDER', dest='all',
            type=str, nargs='+',
            help='Some folders has multiple COMICDIR.')
    parser.add_argument('-v', '--version', action='version',
            version=VERSION)

    args = parser.parse_args()
    return args


def archive_cbz(folder):
    '''zip the folder to .cbz format in the folder's parent dir'''
    if os.path.isdir(folder):
        basename = os.path.basename(folder)
        filename = basename + '.cbz'
        dirname = os.path.dirname(folder)
        filepath = os.path.join(dirname, filename)
        with zipfile.ZipFile(filepath, 'w') as zfile:
            for path, dirs, files in os.walk(folder):
                for fn in files:
                    absfn = os.path.join(path, fn)
                    zfn = os.path.relpath(absfn, dirname)
                    zfile.write(absfn, zfn)
        print('Archive OK: ' + filepath)
    else:
        raise RuntimeError(
                'folder: "{}" Not a dir! do nothing'.format(folder))


def get_subdirs(folder):
    '''return a list which has multiple subdirs.'''
    subdirs = [os.path.join(folder, subdir) for subdir
            in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, subdir))]
    return sorted(subdirs)


def archive_comicdir(folder, delete=False):
    '''folder which include multiple volume dirs.

        if delete == True, vol dirs will be delete.
        '''
    isdir = os.path.isdir(folder)
    if isdir:
        for subdir in get_subdirs(folder):
            try:
                archive_cbz(subdir)
                if delete:
                    shutil.rmtree(subdir)
            except RuntimeError as e:
                print(e)


def main():
    '''entry point'''
    args = get_args()

    if not (args.all or args.folders):
        print('Neither "--all" nor "COMICDIR". Cancel.')
        print('Use "-h" for more detail.')
        sys.exit()

    for folder in args.folders:
        archive_comicdir(folder, args.delete)

    if args.all:
        for all_folder in args.all:
            for folder in get_subdirs(all_folder):
                archive_comicdir(folder, args.delete)


if __name__ == '__main__':
    main()
