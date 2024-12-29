# XMP Tool

This tool will create an XMP sidecar file for media files in a directory missing date/time metadata.

Date/time metadata is inferred from surrounding files in the directory containing this information.

"Live Photos" missing links to the video file will be corrected by adding a Content Identifier to the XMP sidecar file.

## Usage

```bash
xmptool [-h] [-f] [-v] [-d] dir

positional arguments:
  dir            The directory containing media files.

options:
  -h, --help     show this help message and exit
  -f, --force    Force the creation of XMP files even if they already exist.
  -v, --verbose  Enable verbose logging.
  -d, --debug    Enable debug logging.
```

## Installation

After cloning this repository, you can install the tool using the following command:

```bash
pip install .
```

In addition, this tool requires the `exiftool` command line utility to be installed on your system. You can download it from the [ExifTool website](https://exiftool.org/).

Once installed, you can run the tool using the `xmptool` command.