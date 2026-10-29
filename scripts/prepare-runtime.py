#!/usr/bin/env python3
"""Prepare the pinned, minimal VideoScribe engine; never write a runtime into Git history."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def extract_app(archive, destination):
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or '..' in name.parts:
                raise ValueError('Unsafe archive path')
            if not name.parts or name.parts[0] != 'VideoScribe.app':
                continue
            mode = entry.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError('Symbolic links are not accepted in this runtime archive')
            target = destination.joinpath(*name.parts)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(entry) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)
                if mode & 0o111:
                    target.chmod(0o755)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, help='Use an existing VideoScribe.app instead of downloading')
    parser.add_argument('--archive', type=Path, help='Use the pinned release ZIP already downloaded')
    parser.add_argument('--destination', type=Path, default=ROOT / 'runtime', help='Runtime parent directory')
    args = parser.parse_args()
    if args.app and args.archive:
        parser.error('Choose --app or --archive')
    destination = args.destination.expanduser().resolve()
    target = destination / 'VideoScribe.app'
    if target.exists():
        raise SystemExit('Destination already exists; remove the generated runtime explicitly or choose another destination.')
    destination.mkdir(parents=True, exist_ok=True)
    if args.app:
        app = args.app.expanduser().resolve()
        if not (app / 'Contents/MacOS/VideoScribeAgent').is_file():
            raise SystemExit('Input app has no VideoScribeAgent executable')
        shutil.copytree(app, target, symlinks=True)
    else:
        config = json.loads((ROOT / 'runtime.json').read_text())
        with tempfile.TemporaryDirectory(prefix='videoscribe-runtime-') as folder:
            archive = Path(folder) / 'runtime.zip'
            if args.archive:
                shutil.copyfile(args.archive, archive)
            else:
                url = f"https://github.com/{config['repository']}/releases/download/{config['tag']}/{config['asset']}"
                with urllib.request.urlopen(url, timeout=60) as response, archive.open('wb') as output:
                    shutil.copyfileobj(response, output)
            actual = hashlib.sha256(archive.read_bytes()).hexdigest()
            if actual != config['sha256']:
                raise SystemExit('Runtime SHA-256 mismatch; archive rejected')
            extract_app(archive, destination)
    if not os.access(target / 'Contents/MacOS/VideoScribeAgent', os.X_OK):
        raise SystemExit('Runtime executable missing or not executable')
    print(f'Runtime prepared: {target}')
    print('Install the external tools and Whisper model described in README.md before transcription.')

if __name__ == '__main__':
    main()
