#!/usr/bin/env python
import os
import pydicom
import argparse
import datetime
import numpy as np
import nibabel as nib
from pydicom.dataset import FileDataset


class EntryPoint:

    PROGRAM = f'python {os.path.basename(__file__)}'

    DESCRIPTION = 'Convert NIfTI format (.nii.gz) to DICOM files.'

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
    nii = nib.load(nii_file)
    data = nii.get_fdata()
    affine = nii.affine

    spacing = np.sqrt(np.sum(affine[:3, :3] ** 2, axis=0))
    orientation = affine[:3, :3] / spacing

    # Fixed UIDs across all slices
    study_uid = pydicom.uid.generate_uid()
    series_uid = pydicom.uid.generate_uid()
    frame_uid = pydicom.uid.generate_uid()

    # Fixed time/date across all slices
    now = datetime.datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S.%f')

    if nii_file.endswith('.nii.gz'):
        outdir = nii_file[:-7]
    elif nii_file.endswith('.nii'):
        outdir = nii_file[:-4]
    else:
        raise ValueError(f'Invalid NIfTI file name: {nii_file}')
    os.makedirs(outdir, exist_ok=True)

    for i in range(data.shape[2]):
        slice_data = data[:, :, i].astype(np.int16)
        slice_data = np.rot90(slice_data)

        file_meta = pydicom.Dataset()
        ds = FileDataset(None, {}, file_meta=file_meta, preamble=b'\0' * 128)

        ds.PatientName = os.path.basename(nii_file).replace(' ', '_')
        ds.PatientID = os.path.basename(nii_file).replace(' ', '_')
        ds.Modality = 'CT'
        ds.SOPClassUID = pydicom.uid.CTImageStorage
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid
        ds.FrameOfReferenceUID = frame_uid

        position = (affine @ [0, 0, i, 1])[:3]
        ds.ImagePositionPatient = position.tolist()
        ds.ImageOrientationPatient = orientation[:, 0].tolist() + orientation[:, 1].tolist()
        ds.Rows, ds.Columns = slice_data.shape
        ds.PixelSpacing = [spacing[0], spacing[1]]
        ds.SliceThickness = spacing[2]

        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = 'MONOCHROME2'
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1
        ds.PixelData = slice_data.tobytes()

        ds.StudyDate = date_str
        ds.SeriesDate = date_str
        ds.AcquisitionDate = date_str
        ds.ContentDate = date_str

        ds.StudyTime = time_str
        ds.SeriesTime = time_str
        ds.AcquisitionTime = time_str
        ds.ContentTime = time_str

        fname = os.path.join(outdir, f'slice_{i:03d}.dcm')
        ds.save_as(fname)


if __name__ == '__main__':
    EntryPoint().main()
