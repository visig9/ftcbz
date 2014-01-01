#!/usr/bin/env python3

import os.path
import zipfile
import argparse
import os

program_version = 1.0

parser = argparse.ArgumentParser(
        description = 'Assign some comic dirs and archive to .cbz format.')
parser.add_argument('folders', metavar = 'COMICDIR',
        type = str, nargs = '+',
        help = 'Comic book container. It should include multiple volume dirs.')
parser.add_argument('-k', '--keep-vol-dir', dest = 'keep_vol_dir',
        action = 'store_const', const = True, default = False,
        help = 'Keep the "volume dir" not be deleted.')
parser.add_argument('-v', '--version', action = 'version',
        version = str(program_version))

args = parser.parse_args()

def archive_cbz(folder):
    '''zip the folder to .cbz format in the folder's parent dir
    '''
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


# walk all folders
for folder in args.folders:
    isdir = os.path.isdir(folder)
    if isdir:
        subdirs = [ os.path.join(folder, subdir) for subdir
                in os.listdir(folder)
                if os.path.isdir(os.path.join(folder, subdir)) ]
        for subdir in subdirs:
            try:
                archive_cbz(subdir)
            except RuntimeError as e:
                print(e)
