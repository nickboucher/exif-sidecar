# EXIF Sidecar

This tool will create an XMP sidecar file for media files in a directory missing date/time metadata.

Date/time metadata is inferred from surrounding files in the directory containing this information.

"Live Photos" missing links to the video file will be corrected by adding a Content Identifier to the XMP sidecar file.

## Usage

```bash
./exif_sidecar.py [-f] <dir>
```

Adding the `-f` flag will force the tool to overwrite existing XMP sidecar files.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.6 or later.