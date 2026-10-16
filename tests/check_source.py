"""Integración sobre archivos exactos de las bases locales; no toca esos checkouts."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from distribution import config, sha
from prepare_source import prepare


def main():
    data = config()
    source_base, br_base = map(Path, sys.argv[1:3])
    expected = json.loads((ROOT/'patches/macros-sha256.json').read_text())
    (ROOT/'.qa').mkdir(exist_ok=True)
    names = list(expected) + ['src/utils/UpgradeHelper.cpp', 'src/UI/Screens/Settings/SettingsPresenter.cpp',
                            'src/UI/Screens/Settings/SettingsView.cpp', 'scripts/update_version.sh', 'scripts/create_upgrade.sh']
    with tempfile.TemporaryDirectory(dir=ROOT/'.qa') as folder:
        source, br = Path(folder)/'source', Path(folder)/'buildroot'
        for base, dest, files in ((source_base, source, names), (br_base, br, ['configs/duet3d_duetscreen_defconfig'])):
            for name in files:
                path = dest/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(subprocess.check_output(['git', '-C', str(base), 'show', f'HEAD:{name}']))
        with patch('prepare_source.subprocess.check_output', side_effect=[data['upstream_commit'], data['buildroot_commit']]):
            prepare(source, br, unbranded='--allow-unbranded' in sys.argv)
        assert all(sha(source/name) == digest for name, digest in expected.items())
        upgrade = (source/'src/utils/UpgradeHelper.cpp').read_text()
        assert '/repos/Duet3D/DuetScreen/releases' not in upgrade
        assert 'IndartVersionPolicy.h' in upgrade
        assert 'upgradeFromUSB' in upgrade
        assert data['update_repository'] in (source/'src/utils/IndartDistribution.h').read_text()
        assert json.loads((source/'assets/indart3d/distribution.json').read_text())['version'] == data['version']
        if '--allow-unbranded' not in sys.argv:
            assert (source/'assets/indart3d/splash_0.png').read_bytes() == (ROOT/data['logo_file']).read_bytes()
            assert (source/'assets/splash.png').read_bytes() == (ROOT/data['logo_file']).read_bytes()
        assert 'INDART3D' in (source/'src/UI/Screens/Settings/SettingsView.cpp').read_text()
    print('SOURCE OK: transformación sobre bases exactas; siete hashes funcionales idénticos; USB conservado.')


if __name__ == '__main__':
    main()
