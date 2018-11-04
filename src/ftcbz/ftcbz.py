"""Ftcbz cmdline ui."""

import argparse
import os
import sys
import tempfile

from .utils import delete_object_path

from .extractor import Extractor
from .extractor import FolderExtractor
from .extractor import ZipExtractor

from .compressor import Compressor
from .compressor import CbzCompressor
from .compressor import FolderCompressor


VERSION = '2.3.2'


# Framework


def get_object_paths(comic_folder):
    """Return every files and folders under container folder directly."""
    object_paths = [os.path.join(comic_folder, obj)
                    for obj in os.listdir(comic_folder)]
    return sorted(object_paths)


def convert(object_path, extractors=None, compressor=CbzCompressor,
            new_comic_folder=None, replace=False):
    """Convert target in path by extractor and compressor.

    Args:
        object_path      == source path
        extractors       == list of extractor, only the x which
                           "x.fit(objpath) == True" will be used.
        compressor       == compressor
        new_comic_folder == the output comic_folder.
                            if == None, comic_folder == object_path dir
        replace          == replace already exists result files

    Returns:
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

    """
    extractors = [] if extractors is None else extractors

    if new_comic_folder is None:
        new_comic_folder = os.path.dirname(object_path)
    os.makedirs(new_comic_folder, exist_ok=True)
    baseext = os.path.basename(object_path)
    if os.path.isfile(object_path):  # file
        volume_name, ext = os.path.splitext(baseext)
    else:  # folder
        volume_name = baseext

    compress_filepath = compressor.get_final_path(
        new_comic_folder=new_comic_folder,
        volume_name=volume_name)

    for extractor in extractors:
        if extractor.fit(object_path):
            if not replace and os.path.exists(compress_filepath):
                return 'already_exists', compress_filepath

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
    """Get used extractors."""
    extractors = [eclass(passwords=args.passwords)
                  for eclass in Extractor.__subclasses__()
                  if eclass.id in args.extractors]
    return extractors


def get_used_compressor(args):
    """Get used compressor."""
    for C in Compressor.__subclasses__():
        if C.id == args.compressor:
            return C()


def get_args():
    """Get command line args."""
    def generate_all_info(classes):
        """Generate all info form exreactors or compressors."""
        infos = []
        for c in classes:
            infos.append('{:>6} - {}'.format(c.id, c.description))
        info = '\n'.join(infos)
        ids = [c.id for c in classes]
        return (info, ids)

    def get_all_extractors_info():
        """Collect extractors info."""
        extractors = Extractor.__subclasses__()
        return generate_all_info(extractors)

    def get_all_compressors_info():
        """Collect extractors info."""
        compressors = Compressor.__subclasses__()
        return generate_all_info(compressors)

    def extra_varify(args):
        if not sys.version_info >= (3, 3, 0):
            print('ftcbz required running on python>=3.3. Cancel.')
            sys.exit()
        if not (args.all or args.folders):
            print('Neither "ALLDIR" nor "COMICDIR" found. Cancel.\n'
                  'Use "-h" for more detail.')
            sys.exit()
        for e in get_used_extractors(args):
            e.check_requirement()

    def extra_modify(args):
        if args.reverse:
            args.extractors = [ZipExtractor.id]
            args.compressor = FolderCompressor.id

    def parse_args():
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description='Freezing a lot of comic directories & files'
                        ' to .cbz format!')

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
            help='If not assign, the files will be generated'
                 '\nin their source directories.')

        parser.add_argument(
            '-r', '--replace', dest='replace',
            action='store_const', const=True, default=False,
            help='Replace target files if the files are already exists.')

        parser.add_argument(
            '-d', '--delete', dest='delete',
            action='store_const', const=True, default=False,
            help='Delete data source when archive complete.')

        parser.add_argument(
            '--reverse', dest='reverse',
            action='store_const', const=True, default=False,
            help='Reverse standard archive operation. Equal to:\n'
                 '"--extractors {zipid} --compressor {dirid}"\n'
                 'It will overwrite your manual setting.'
                 .format(zipid=ZipExtractor.id, dirid=FolderCompressor.id)
                 )

        e_info, e_ids = get_all_extractors_info()
        parser.add_argument(
            '-e', '--extractors', metavar='EXTRACTOR', dest='extractors',
            action='store', default=[FolderExtractor.id], nargs="*",
            choices=e_ids,
            help='\n'.join([
                'Choice the volume format(s) you want to process.',
                'Available formats:',
                e_info,
                '(default: {})'.format(FolderExtractor.id)]))

        c_info, c_ids = get_all_compressors_info()
        parser.add_argument(
            '-c', '--compressor', metavar='COMPRESSOR', dest='compressor',
            action='store', default=CbzCompressor.id,
            choices=c_ids,
            help='\n'.join([
                'Choice a output format.',
                'Available formats:',
                c_info,
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
    extra_modify(args)
    extra_varify(args)
    return args


def main():
    """Entry point."""
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
        """Get new_comic_folder for convert() function."""
        if args.output_alldir:
            norm_folder = os.path.normpath(ori_comic_folder)
            basename = os.path.basename(norm_folder)
            new_comic_folder = os.path.join(args.output_alldir, basename)
        else:
            new_comic_folder = ori_comic_folder
        return new_comic_folder

    def delete(request_delete, status, object_path, final_path):
        """Delete object_path."""
        if status not in ('not_fit', 'extract_error'):
            if request_delete:
                abs_object_path = os.path.abspath(object_path)
                abs_final_path = os.path.abspath(final_path)
                if abs_object_path != abs_final_path:
                    delete_object_path(object_path)

    def print_info(status, final_path):
        """Print process info for each object."""
        if status != 'not_fit':
            if status == 'archived':
                info = 'Archived OK: -> {}'.format(final_path)
            if status == 'already_exists':
                info = 'Already Exist: -> {}'.format(final_path)
            if status == 'extract_error':
                info = 'Extract error: -> {}'.format(final_path)
            print(info)

    args = get_args()

    extractors = get_used_extractors(args)
    compressor = get_used_compressor(args)

    for ori_comic_folder in get_ori_comic_folders(args):
        new_comic_folder = get_new_comic_folder(args, ori_comic_folder)
        for object_path in get_object_paths(ori_comic_folder):
            status, final_path = convert(
                object_path=object_path,
                extractors=extractors,
                compressor=compressor,
                new_comic_folder=new_comic_folder,
                replace=args.replace)

            delete(args.delete, status, object_path, final_path)
            print_info(status, final_path)
