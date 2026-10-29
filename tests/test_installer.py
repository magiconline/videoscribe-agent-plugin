import importlib.util
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/prepare-runtime.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class ArchiveTests(unittest.TestCase):
    def run_archive(self, name, mode=0o100755):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / 'test.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                entry = zipfile.ZipInfo(name)
                entry.external_attr = mode << 16
                bundle.writestr(entry, b'test')
            installer.extract_app(archive, root / 'out')
            return (root / 'out' / name).stat().st_mode

    def test_rejects_parent_traversal(self):
        with self.assertRaises(ValueError): self.run_archive('VideoScribe.app/../../escape')

    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError): self.run_archive('/escape')

    def test_rejects_symlink(self):
        with self.assertRaises(ValueError): self.run_archive('VideoScribe.app/link', stat.S_IFLNK | 0o777)

    def test_preserves_executable(self):
        self.assertTrue(self.run_archive('VideoScribe.app/Contents/MacOS/VideoScribeAgent') & 0o111)


class EngineTests(unittest.TestCase):
    def test_engine_has_no_gui_bundle_and_keeps_worker_executable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = root / 'VideoScribe.app'
            binary = app / 'Contents/MacOS/VideoScribeAgent'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'engine')
            binary.chmod(0o755)
            resources = app / 'Contents/Resources'
            resources.mkdir()
            (resources / 'AppIcon.icns').write_bytes(b'icon')
            target = root / 'VideoScribeEngine'
            installer.install_engine(app, target)
            self.assertTrue((target / 'VideoScribeAgent').stat().st_mode & 0o111)
            self.assertFalse(list(target.rglob('*.app')))
            self.assertFalse((target / 'Resources/AppIcon.icns').exists())
