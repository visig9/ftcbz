#!/usr/bin/env python3

import os.path
import zipfile
import argparse
import os
import sys
import shutil
import subprocess
import uuid


VERSION = '1.2.0'


def get_args():
    '''get command line args'''
    parser = argparse.ArgumentParser(
        description='Assign some comic dirs and archive to .cbz format.')
    parser.add_argument(
        'folders', metavar='COMICDIR', type=str, nargs='*',
        help='A comic book folders.'
             ' Each COMICDIR contain multiple "volume dirs".')
    parser.add_argument(
        '-d', '--delete', dest='delete',
        action='store_const', const=True, default=False,
        help='Delete "volume dir" after the archive complete.')
    parser.add_argument(
        '--rar', dest='rar',
        action='store_const', const=True, default=False,
        help='Also convert "volume.rar" to "volume.cbz" and remove password.'
             ' (Required unrar)')
    parser.add_argument(
        '-p', '--passwords', metavar='PW', dest='passwords',
        action='store', default=None, nargs="*",
        help='Some unzip passwords for rar files.')
    parser.add_argument(
        '-a', '--all', metavar='FOLDER', dest='all', type=str, nargs='+',
        help='Some folders has multiple COMICDIR.')
    parser.add_argument(
        '-v', '--version', action='version', version=VERSION)

    def extra_varify(args):
        if not (args.all or args.folders):
            print('Neither "--all" nor "COMICDIR". Cancel.\n'
                  'Use "-h" for more detail.')
            sys.exit()
        if args.rar:
            if not shutil.which('unrar'):
                print('Program "unrar" not found. Cancel')
                sys.exit()
        if args.passwords:
            if not args.rar:
                print('Arguments "--passwords" only work with "--rar".'
                      ' Cancel.')
                sys.exit()

    args = parser.parse_args()
    extra_varify(args)

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
    '''
    return a list which has multiple directorys which under the "folder"
    directly.
    '''
    subdirs = [os.path.join(folder, subdir) for subdir
               in os.listdir(folder)
               if os.path.isdir(os.path.join(folder, subdir))]
    return sorted(subdirs)


def get_rars(folder):
    '''
    return a list which has multiple rar files which under the "folder"
    directly.
    '''
    def is_rar(filename):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            return False
        trash, ext = os.path.splitext(filename)
        if ext not in ['.rar', '.cbr']:
            return False
        return True

    rars = [os.path.join(folder, filename) for filename
            in os.listdir(folder)
            if is_rar(filename)]
    return sorted(rars)


def rar2cbz(rarpath, passwords=[]):
    '''Convert rar to cbz file'''
    def get_tmp_dirpath(rarpath):
        '''this dirpath will holding the unzip data.'''
        dirname = os.path.dirname(rarpath)
        baseext = os.path.basename(rarpath)
        base, ext = os.path.splitext(baseext)
        tmp_dirpath = os.path.join(dirname, base)
        return tmp_dirpath

    def get_cmd(rarpath, tmp_dirpath, password=None):
        '''generate command list'''
        unrar = shutil.which('unrar')
        cmd = [unrar, 'e', '-inul']
        if password:
            cmd.append('-p' + password)
        else:
            cmd.append('-p-')
        cmd.append(rarpath)
        cmd.append(tmp_dirpath + '/')
        return cmd

    def get_cmds(rarpath, tmp_dirpath, passwords=[]):
        yield get_cmd(rarpath, tmp_dirpath)  # no password version
        for password in passwords:
            yield get_cmd(rarpath, tmp_dirpath, password)

    def backup_conflict_path(tmp_dirpath):
        '''
        Move the original conflict things to tmp_oripath if necessary

            return = a temporary path string for original data.
                     None mean no conflict.
        '''
        if os.path.exists(tmp_dirpath):
            dirbase, ext = os.path.splitext(tmp_dirpath)
            tmp_oripath = dirbase + '_tmp_' + uuid.uuid4().hex[:8]
            shutil.move(tmp_dirpath, tmp_oripath)
            return tmp_oripath
        else:
            return None

    def restore_conflict_path(tmp_dirpath, tmp_oripath):
        '''restore what backup_conflict_path() done.'''
        if tmp_oripath:
            shutil.move(tmp_oripath, tmp_dirpath)

    tmp_dirpath = get_tmp_dirpath(rarpath)
    tmp_oripath = backup_conflict_path(tmp_dirpath)  # backup

    # try every passwords for unrar operation
    for cmd in get_cmds(rarpath, tmp_dirpath, passwords):
        rtn = subprocess.call(cmd)
        if rtn != 10:  # password error code == 10
            break

    if rtn != 0:  # some unknown error, cancel.
        if os.path.isdir(tmp_dirpath):
            shutil.rmtree(tmp_dirpath)
        print(
            'ERROR: "{}" unrar failed. error code => {}'.format(rarpath, rtn))

    if os.path.isdir(tmp_dirpath):
        archive_cbz(tmp_dirpath)      # generate cbz
        shutil.rmtree(tmp_dirpath)    # remove tmp_dirpath

    restore_conflict_path(tmp_dirpath, tmp_oripath)  # restore


def process_comicdir(folder, delete=False, rar=False, passwords=[]):
    '''folder which include multiple volume dirs.

        delete    = Original files will be delete.
        rar       = True will process rar files as volume dir too.
        passwords = list of rar passwords.
        '''
    if os.path.isdir(folder):
        for subdir in get_subdirs(folder):
            try:
                archive_cbz(subdir)
                if delete:
                    shutil.rmtree(subdir)
            except RuntimeError as e:
                print(e)
        if rar:
            for rarfile in get_rars(folder):
                try:
                    rar2cbz(rarfile, passwords)
                    if delete:
                        os.remove(rarfile)
                except RuntimeError as e:
                    print(e)


def main():
    '''entry point'''
    def get_comic_folders(args):
        """Each comic folder container multiple volumes."""
        comic_folders = {folder for folder in args.folders}
        if args.all:
            for all_folder in args.all:
                for folder in get_subdirs(all_folder):
                    comic_folders.add(folder)
        return comic_folders

    args = get_args()
    comic_folders = get_comic_folders(args)

    for folder in comic_folders:
        process_comicdir(
            folder, args.delete, rar=args.rar, passwords=args.passwords)


if __name__ == '__main__':
    main()
