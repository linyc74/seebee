#!/usr/bin/env python
import os
import argparse
import subprocess
from os.path import basename, dirname, abspath, exists


class EntryPoint:

    PROGRAM = f'python {os.path.basename(__file__)}'

    DESCRIPTION = 'Convert DICOM files to NIfTI format (.nii.gz) using dcm2niix.'

    POSITIONAL = [
        {
            'keys': ['dicom_dir'],
            'properties': {
                'type': str,
                'help': 'path to the dicom directory',
            }
        },
    ]

    OPTIONAL = [
        {
            'keys': ['-j', '--keep-json'],
            'properties': {
                'action': 'store_true',
                'help': 'keep output json file',
            }
        },
        {
            'keys': ['-h', '--help'],
            'properties': {
                'action': 'help',
                'help': 'show this help message',
            }
        },
    ]

    parser: argparse.ArgumentParser

    def main(self):
        self.set_parser()
        self.add_required_arguments()
        self.add_optional_arguments()
        self.run()

    def set_parser(self):
        self.parser = argparse.ArgumentParser(
            prog=self.PROGRAM,
            description=self.DESCRIPTION,
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter)

    def add_required_arguments(self):
        group = self.parser.add_argument_group('positional arguments')
        for item in self.POSITIONAL:
            group.add_argument(*item['keys'], **item['properties'])

    def add_optional_arguments(self):
        group = self.parser.add_argument_group('optional arguments')
        for item in self.OPTIONAL:
            group.add_argument(*item['keys'], **item['properties'])

    def run(self):
        args = self.parser.parse_args()
        main(dicom_dir=args.dicom_dir, keep_json=args.keep_json)


def main(dicom_dir: str, keep_json: bool):

    dicom_dir = abspath(dicom_dir)  # convert to absolute path to avoid weird behavior, e.g. './dicom_dir/./'

    outdir = dirname(dicom_dir)
    fname = basename(dicom_dir)

    nii_gz = f'{outdir}/{fname}.nii.gz'
    if exists(nii_gz):
        print(f'{nii_gz} already exists, overwrite it.', flush=True)
        os.remove(nii_gz)

    cmd = ' '.join([
        'dcm2niix',
        '-z y',  # compress output
        f'-f {fname}',
        f'-o {outdir}',
        dicom_dir
    ])
    print(f'CMD: {cmd}\n', flush=True)
    subprocess.check_call(cmd, shell=True)

    if not keep_json:
        json_file = f'{outdir}/{fname}.json'
        if exists(json_file):
            os.remove(json_file)


if __name__ == '__main__':
    EntryPoint().main()
