#!/usr/bin/env python
import os
import argparse
import numpy as np
import nibabel as nib


class EntryPoint:

    PROGRAM = f'python {os.path.basename(__file__)}'

    DESCRIPTION = 'Show voxel information of a NIfTI (.nii.gz) file.'

    POSITIONAL = [
        {
            'keys': ['nii_file'],
            'properties': {
                'type': str,
                'help': 'path to the NIfTI (.nii.gz) file',
            }
        },
    ]

    OPTIONAL = [
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
        main(nii_file=args.nii_file)


def main(nii_file: str):
    img = nib.load(nii_file)

    # Basic shape and header
    data_shape = img.shape
    voxel_dims = img.header.get_zooms()
    affine = img.affine

    # Orientation and handedness
    orientation = nib.orientations.aff2axcodes(affine)
    handedness = np.linalg.det(affine)  # > 0 means right-handed, < 0 left-handed

    print(f'Shape: {data_shape}')
    print(f'Voxel dimensions: {voxel_dims}')
    print(f'Affine matrix:\n{affine}')
    print(f'Orientation codes (X, Y, Z): {orientation}')
    print(f'Coordinate system: {"Right-handed" if handedness > 0 else "Left-handed"}')


if __name__ == '__main__':
    EntryPoint().main()
