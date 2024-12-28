#!/usr/bin/env python3
from datetime import datetime
from argparse import ArgumentParser
from sys import exit
from os.path import isfile, splitext
from subprocess import run
from json import loads
from glob import glob
from itertools import chain
from collections import defaultdict
from uuid import uuid4

EXTs = ['mp4', 'mov', 'avi', 'jpg', 'jpeg', 'png', 'gif', 'tiff', 'tif', 'webp', 'heic', 'heif']

def exif_tool(file_path: str, tags: list) -> dict[str, str]:
    cmd = ['exiftool', '-json', '-d', '%Y-%m-%dT%H:%M:%S%:z']
    cmd += [f'-{tag}' for tag in tags]
    cmd += [file_path]
    result = run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error: Failed to extract metadata from {file_path}')
        exit(1)
    metadata = loads(result.stdout)[0]
    metadata.pop('SourceFile')
    return metadata

def xmp(creation_date: datetime|None, content_id: str|None) -> str:
    result = "<?xpacket begin='\ufeff' id='W5M0MpCehiHzreSzNTczkc9d'?>\n" \
             "<x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Image::ExifTool 12.99'>\n" \
             "<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>\n\n"
    
    if creation_date:
        result += "<rdf:Description rdf:about=''\n" \
                  " xmlns:exif='http://ns.adobe.com/exif/1.0/'>\n" \
                  f" <exif:DateTimeOriginal>{creation_date.isoformat()}</exif:DateTimeOriginal>\n" \
                  "</rdf:Description>\n\n" \
                  "<rdf:Description rdf:about=''\n" \
                  " xmlns:photoshop='http://ns.adobe.com/photoshop/1.0/'>\n" \
                  f" <photoshop:DateCreated>{creation_date.isoformat()}</photoshop:DateCreated>\n" \
                  "</rdf:Description>\n\n"
    if content_id:
        result += "<rdf:Description rdf:about=''\n" \
                  " xmlns:Apple='http://ns.exiftool.org/MakerNotes/Apple/1.0/'>\n" \
                  f" <Apple:ContentIdentifier>{content_id}</Apple:ContentIdentifier>\n" \
                  "</rdf:Description>\n\n"
    
    result += "</rdf:RDF>\n" \
              "</x:xmpmeta>\n" \
              "<?xpacket end='w'?>"

    return result

def main() -> None:

    parser = ArgumentParser(
                    prog='EXIF Video Repair Tool',
                    description='This tool will create an XMP file for a given video file with the creation date of the video file.')
    parser.add_argument('dir', metavar='dir', type=str, help='The directory containing media files.')
    parser.add_argument('-f', '--force', action='store_true', help='Force the creation of XMP files even if they already exist.')
    args = parser.parse_args()

    file_paths = sorted(list(chain.from_iterable([glob(f'{args.dir}/**/*.{ext}', recursive=True) for ext in EXTs])))
    file_pairs = defaultdict(list)
    for file_path in file_paths:
        root, ext = splitext(file_path)
        file_pairs[root] += ext

    processed_files = []
    for file, exts in file_pairs.items():
        if len(exts) == 2:
            pair_creation_date = None
            pair_content_id = None
            skip = False
            for ext in exts:
                file_path = f'{file}{ext}'
                metadata = exif_tool(file_path, ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'XMP:DateCreated', 'XMP:CreateDate', 'MakerNotes:ContentIdentifier'])
                creation_date = metadata.get('DateTimeOriginal', metadata.get('CreateDate', metadata.get('DateCreated')))
                content_id = metadata.get('ContentIdentifier')
                if creation_date:
                    pair_creation_date = datetime.fromisoformat(creation_date)
                else:
                    print(f'Info: No creation date in {file_path}.')
                if content_id:
                    if pair_content_id and pair_content_id != content_id:
                        print(f'Warning: Content ID mismatch in {file_path}.')
                        skip = True
                        break
                    pair_content_id = content_id
                else:
                    if not pair_content_id:
                        print(f'Info: Creating Missing Content ID for {file_path}.')
                        pair_content_id = str(uuid4())
            if not skip:
                if args.force or not (isfile(f'{file}{exts[0]}.xmp' or isfile(f'{file}{exts[1]}.xmp'))):
                    print(f'Warning: XMP file already exists for pair {file}, skipping.')
                else:
                    for ext in exts:
                        with open(f'{file}{ext}.xmp', 'w') as f:
                            print(f"Notice: Writing XMP Content ID file: {file_path}")
                            f.write(xmp(pair_creation_date, pair_content_id))
                        processed_files.append(f'{file}{ext}')

    for file_path in file_paths:
        metadata = exif_tool(file_path, ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'XMP:DateCreated', 'XMP:CreateDate'])
        creation_date = metadata.get('DateTimeOriginal', metadata.get('CreateDate', metadata.get('DateCreated')))
        if creation_date:
            recent_date = datetime.fromisoformat(creation_date)
            break

    if file_paths and not recent_date:
        print("Warning: No creation date found in any media files.")
    else:
        for file_path in file_paths:
            if file_path not in processed_files:
                metadata = exif_tool(file_path, ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'XMP:DateCreated', 'XMP:CreateDate'])
                creation_date = metadata.get('DateTimeOriginal', metadata.get('CreateDate', metadata.get('DateCreated')))
                if creation_date:
                    recent_date = datetime.fromisoformat(creation_date)
                    break
                else:
                    if args.force or not (isfile(f'{file}{exts[0]}.xmp' or isfile(f'{file}{exts[1]}.xmp'))):
                        print(f'Warning: XMP file already exists for file {file}, skipping.')
                    else:
                        with open(f'{file_path}.xmp', 'w') as f:
                            print(f"Notice: Writing XMP date file: {file_path}")
                            f.write(xmp(pair_creation_date, None))
                        processed_files.append(file_path)
    
    print(f"Complete. Wrote {len(processed_files)} XMP files in {args.dir}.")

if __name__ == "__main__":
    main()