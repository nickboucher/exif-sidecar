# XMP Tool

This tool will create an XMP sidecar file for media files in a directory missing date/time metadata.

Date/time metadata is inferred from surrounding files in the directory containing this information.

"Live Photos" missing links to the video file will be corrected by adding a Content Identifier to the XMP sidecar file.

## Usage

```bash
exif-sidecar.py [-h] [-f] [-v] [-d] dir

positional arguments:
  dir            The directory containing media files.

options:
  -h, --help     show this help message and exit
  -f, --force    Force the creation of XMP files even if they already exist.
  -v, --verbose  Enable verbose logging.
  -d, --debug    Enable debug logging.
```

## Installation

Install the required packages with pip:

```bash
pip install -r requirements.txt
```

In addition, this tool requires the `exiftool` command line utility to be installed on your system. You can download it from the [ExifTool website](https://exiftool.org/).

Requires Python 3.6 or later.