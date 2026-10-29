#!/usr/bin/env python3
"""Prepare the pinned, minimal VideoScribe engine; never write a runtime into Git history."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
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

def install_engine(app, target):
    executable = app / 'Contents/MacOS/VideoScribeAgent'
    if not os.access(executable, os.X_OK):
        raise ValueError('Runtime executable missing or not executable')
    target.mkdir(parents=True)
    shutil.copy2(executable, target / 'VideoScribeAgent')
    # CLI resources stay separate from the GUI bundle. Do not create an .app.
    resources = app / 'Contents/Resources'
    if resources.exists():
        shutil.copytree(resources, target / 'Resources', symlinks=True,
                        ignore=shutil.ignore_patterns('AppIcon.icns'))
    else:
        (target / 'Resources').mkdir()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, help='Use an existing VideoScribe.app instead of downloading')
    parser.add_argument('--archive', type=Path, help='Use the pinned release ZIP already downloaded')
    parser.add_argument('--destination', type=Path, default=ROOT / 'runtime.noindex', help='Runtime parent directory')
    args = parser.parse_args()
    if args.app and args.archive:
        parser.error('Choose --app or --archive')
    destination = args.destination.expanduser().resolve()
    target = destination / 'VideoScribeEngine'
    if target.exists():
        raise SystemExit('Destination already exists; remove the generated runtime explicitly or choose another destination.')
    destination.mkdir(parents=True, exist_ok=True)
    if args.app:
        app = args.app.expanduser().resolve()
        if not (app / 'Contents/MacOS/VideoScribeAgent').is_file():
            raise SystemExit('Input app has no VideoScribeAgent executable')
        install_engine(app, target)
    else:
        config = json.loads((ROOT / 'runtime.json').read_text())
        with tempfile.TemporaryDirectory(prefix='videoscribe-runtime-') as folder:
            archive = Path(folder) / 'runtime.zip'
            if args.archive:
                shutil.copyfile(args.archive, archive)
            else:
                url = f"https://github.com/{config['repository']}/releases/download/{config['tag']}/{config['asset']}"
                # macOS curl uses system certificate trust; Python.org builds may lack a CA bundle.
                # Resolve the system/terminal proxy explicitly rather than assuming curl reads macOS settings.
                host = 'github.com'
                proxies = urllib.request.getproxies()
                proxy = '' if urllib.request.proxy_bypass(host) else proxies.get('https', proxies.get('all', ''))
                subprocess.run(['/usr/bin/curl', '--fail', '--location', '--retry', '3',
                                '--connect-timeout', '20', '--max-time', '180',
                                '--proxy', proxy, '--output', str(archive), url], check=True)
            actual = hashlib.sha256(archive.read_bytes()).hexdigest()
            if actual != config['sha256']:
                raise SystemExit('Runtime SHA-256 mismatch; archive rejected')
            extracted = Path(folder) / 'extracted'
            extract_app(archive, extracted)
            install_engine(extracted / 'VideoScribe.app', target)
    if not os.access(target / 'VideoScribeAgent', os.X_OK):
        raise SystemExit('Runtime executable missing or not executable')
    print(f'Runtime prepared: {target}')
    print('Install the external tools and Whisper model described in README.md before transcription.')

if __name__ == '__main__':
    main()
