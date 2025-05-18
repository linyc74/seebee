#!/usr/bin/env python
import os
import argparse
import numpy as np
import scipy.ndimage
import nibabel as nib


class EntryPoint:

    PROGRAM = f'python {os.path.basename(__file__)}'

    DESCRIPTION = 'Resize voxel dimensions of an NIfTI (.nii.gz) file.'

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
            'keys': ['-x', '--left-right-size'],
            'properties': {
                'type': float,
                'required': False,
                'default': 0.,
                'help': 'voxel size (mm) on the left-right axis, default for no resizing (default: %(default)s)',
            }
        },
        {
            'keys': ['-y', '--posterior-anterior-size'],
            'properties': {
                'type': float,
                'required': False,
                'default': 0.,
                'help': 'voxel size (mm) on the posterior-anterior axis, default for no resizing (default: %(default)s)',
            }
        },
        {
            'keys': ['-z', '--inferior-superior'],
            'properties': {
                'type': float,
                'required': False,
                'default': 0.,
                'help': 'voxel size (mm) on the inferior-superior axis, default for no resizing (default: %(default)s)',
            }
        },
        {
            'keys': ['-o', '--output'],
            'properties': {
                'type': str,
                'required': False,
                'default': 'None',
                'help': 'output file path, default for auto rename (default: %(default)s)',
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
        main(
            nii_file=args.nii_file,
            x=args.left_right_size,
            y=args.posterior_anterior_size,
            z=args.inferior_superior,
            output=args.output)


def main(nii_file: str, x: float, y: float, z: float, output: str):
    if x == 0 and y == 0 and z == 0:
        print('No resizing specified, exiting.')
        return

    img = nib.load(nii_file)
    data = img.get_fdata()
    affine = img.affine
    original_sizes = img.header.get_zooms()[:3]

    if x == 0.:
        x = original_sizes[0]
    if y == 0.:
        y = original_sizes[1]
    if z == 0.:
        z = original_sizes[2]

    target_sizes = (x, y, z)

    # Resample with interpolation (e.g., linear)
    zoom_factors = tuple(o / t for o, t in zip(original_sizes, target_sizes))
    resampled_data = scipy.ndimage.zoom(data, zoom=zoom_factors, order=1)

    # Update affine for new voxel sizes
    new_affine = np.copy(affine)
    for i in range(3):  # for x, y, z
        new_affine[0:3, i] = new_affine[0:3, i] * (target_sizes[i] / original_sizes[i])  # x, y, z correspond to 0, 1, 2 columns
        new_affine[i, 3] = new_affine[i, 3] * (target_sizes[i] / original_sizes[i])  # x, y, z correspond to 0, 1, 2 elements of the 4th column

    # Create new NIfTI image
    new_img = nib.Nifti1Image(resampled_data, affine=new_affine)

    if output.lower() == 'none':
        prefix = nii_file
        if nii_file.endswith('.nii.gz'):
            prefix = prefix[:-7]
        elif nii_file.endswith('.nii'):
            prefix = prefix[:-4]
        output = f'{prefix}_resized_{x}_{y}_{z}.nii.gz'
    nib.save(new_img, output)


if __name__ == '__main__':
    EntryPoint().main()
