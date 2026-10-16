import io
import json
import struct
import sys
import tarfile
import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from distribution import config, version, check_logo, sha
from verify_artifacts import verify_binary, verify_usb, verify_sd
import publish_release


class DistributionTests(unittest.TestCase):
    def test_config_is_fixed(self):
        data = config()
        self.assertEqual(len(version(data['version'])), 4)
        self.assertEqual(data['preset'], 'T113-Release')
        self.assertEqual(len(data['upstream_commit']), 40)

    def test_version_numeric_comparison(self):
        self.assertGreater(version('v1.0.0.10'), version('v1.0.0.2'))
        self.assertGreater(version('v1.0.1.1'), version('v1.0.0.99'))
        for bad in ['v1.0.0', '1.0.0.1', 'v1.0.0.2-rc', 'v1.0.0.999999999', 'v1..0.1']:
            with self.assertRaises(ValueError):
                version(bad)

    def test_missing_logo_blocks_final(self):
        data = dict(config(), logo_sha256=None)
        with self.assertRaises(ValueError):
            check_logo(data)

    def binary(self):
        data = config()
        binary = bytearray(52)
        binary[:6] = b'\x7fELF\x01\x01'
        struct.pack_into('<H', binary, 18, 40)
        struct.pack_into('<I', binary, 36, 0x400)
        return bytes(binary)+data['version'].encode()+b'\0Macro thumbnail support v1\0'+('/repos/'+data['update_repository']+'/releases').encode()

    def test_arm_validation(self):
        verify_binary(self.binary(), config())
        for broken in [b'invalid', self.binary().replace(config()['version'].encode()+b'\0', config()['version'].encode()+b'0\0'), self.binary().replace(b'\x7fELF', b'FAIL'), self.binary()+b'/repos/Duet3D/DuetScreen/releases']:
            with self.assertRaises(ValueError):
                verify_binary(broken, config())

    def test_usb_structure_and_permissions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'scripts').mkdir()
            (root/'scripts/pre-update').write_bytes(b'pre')
            (root/'scripts/post-update').write_bytes(b'post')
            metadata = dict(config(), branded=False)
            files = {'usr/bin/DuetScreen': self.binary(), 'pre-update': b'pre', 'post-update': b'post',
                     'buildroot_version': b'v0.4.4\n', 'etc/assets/test': b'asset',
                     'etc/indart3d-release.json': json.dumps(metadata).encode()}
            package = root/'DuetScreen.tar.gz'
            for executable in (True, False):
                with tarfile.open(package, 'w:gz') as archive:
                    for name, binary in files.items():
                        item = tarfile.TarInfo(name)
                        item.size = len(binary)
                        item.mode = 0o755 if executable else 0o644
                        archive.addfile(item, io.BytesIO(binary))
                if executable:
                    verify_usb(package, self.binary(), metadata, root)
                else:
                    with self.assertRaises(ValueError):
                        verify_usb(package, self.binary(), metadata, root)

    def test_invalid_sd_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder)/'sdcard.img'
            image.write_bytes(bytes(512))
            with self.assertRaises(ValueError):
                verify_sd(image, self.binary(), dict(config(), branded=False), Path(folder))

    def test_publication_requires_physical_confirmation(self):
        with patch.dict('os.environ', {'EXPECTED_VERSION': config()['version'], 'HARDWARE_CONFIRMED': 'false'}):
            with self.assertRaises(ValueError):
                publish_release.main()

    def test_publication_rejects_existing_and_incomplete_releases(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path.cwd()
            try:
                os.chdir(folder)
                artifacts = Path('artifacts')
                artifacts.mkdir()
                for name in ('DuetScreen.tar.gz', 'sdcard.img'):
                    (artifacts/name).write_bytes(b'test-only fixture')
                metadata = dict(config(), branded=True, sd_verified=True, source_commit='a'*40,
                                files={name: sha(artifacts/name) for name in ('DuetScreen.tar.gz', 'sdcard.img')})
                (artifacts/'build-manifest.json').write_text(json.dumps(metadata))
                (artifacts/'SHA256SUMS.txt').write_text('test checksums\n')
                env = {'EXPECTED_VERSION': config()['version'], 'HARDWARE_CONFIRMED': 'true',
                       'GITHUB_SHA': 'a'*40, 'GITHUB_REPOSITORY': config()['update_repository']}
                with patch.dict(os.environ, env):
                    with patch('publish_release.gh', return_value=json.dumps([[{'tag_name':config()['version']}]])) as gh:
                        with self.assertRaises(ValueError):
                            publish_release.main()
                        self.assertEqual(gh.call_count, 1)
                    with patch('publish_release.gh', side_effect=['[[]]', json.dumps([[{'ref':'refs/tags/'+config()['version']} ]])]) as gh:
                        with self.assertRaises(ValueError):
                            publish_release.main()
                        self.assertEqual(gh.call_count, 2)
                    with patch('publish_release.gh', side_effect=['[[]]', '[[]]', '', RuntimeError('upload failed')]) as gh:
                        with self.assertRaises(RuntimeError):
                            publish_release.main()
                        self.assertFalse(any(call.args[:2] == ('release','edit') for call in gh.call_args_list))
                    with patch('publish_release.gh', side_effect=['[[]]', '[[]]', '', '', '']) as gh:
                        publish_release.main()
                        self.assertEqual(gh.call_args.args[:2], ('release', 'edit'))
            finally:
                os.chdir(original)


if __name__ == '__main__':
    unittest.main()
