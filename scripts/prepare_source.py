"""Aplica únicamente las modificaciones de distribución a las bases fijadas."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from distribution import ROOT, config, check_logo, sha


def edit(path, old, new):
    text = path.read_text(encoding='utf-8')
    if text.count(old) != 1:
        raise RuntimeError(f'Base inesperada: {path}: {old[:65]!r}')
    path.write_text(text.replace(old, new), encoding='utf-8', newline='\n')


def prepare(source, buildroot, unbranded=False):
    data = config()
    for folder, key in ((source, 'upstream_commit'), (buildroot, 'buildroot_commit')):
        actual = subprocess.check_output(['git', '-C', str(folder), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != data[key]:
            raise ValueError(f'Base incorrecta: {folder}: {actual}')
    logo = None if unbranded else check_logo(data)
    subprocess.run([sys.executable, str(ROOT/'scripts/apply_macros.py'), str(source)], check=True)
    # Los siete archivos funcionales quedan congelados antes y después de esta fase.
    import hashlib
    expected = json.loads((ROOT/'patches/macros-sha256.json').read_text())
    frozen = {name: sha(source/name) for name in expected}
    utils = source/'src/utils'
    shutil.copyfile(ROOT/'patches/IndartVersionPolicy.h', utils/'IndartVersionPolicy.h')
    header = '#pragma once\n#define INDART_UPDATE_REPOSITORY '+json.dumps(data['update_repository'])+'\n'
    header += '#define INDART_RELEASES_PATH '+json.dumps('/repos/'+data['update_repository']+'/releases')+'\n'
    (utils/'IndartDistribution.h').write_text(header, encoding='utf-8', newline='\n')
    upgrade = utils/'UpgradeHelper.cpp'
    edit(upgrade, '#include "UpgradeHelper.h"', '#include "UpgradeHelper.h"\n#include "IndartDistribution.h"\n#include "IndartVersionPolicy.h"')
    text = upgrade.read_text()
    start = text.index('\t\tstatic std::optional<GithubReleaseInfo> getNewestGithubReleaseWithUpgradeAsset()')
    end = text.index('\t\tconstexpr const char* kBuildrootVersionFile', start)
    replacement = (ROOT/'patches/github_release_selection.cpp.txt').read_text()
    upgrade.write_text(text[:start]+replacement+'\n'+text[end:], encoding='utf-8', newline='\n')
    # El botón de desarrollador también muestra la confirmación existente en Home.
    presenter = source/'src/UI/Screens/Settings/SettingsPresenter.cpp'
    text = presenter.read_text()
    start = text.index('\t\tif (!UpgradeHelper::upgradeFromGithubLatest())')
    end = text.index('\n\t}\n} // namespace UI', start)
    text = text[:start]+'''\t\tconst auto tag = UpgradeHelper::checkForUpdate();
\t\tif (tag)
\t\t{
\t\t\tModel::get().post<EventType::GithubUpdateAvailable>(*tag);
\t\t}
\t\telse
\t\t{
\t\t\tModel::get().post<EventType::Response>(ResponseType::ERROR, _("settings.upgrade_from_github_failed"));
\t\t}'''+text[end:]
    presenter.write_text(text, encoding='utf-8', newline='\n')
    metadata = dict(data, branded=not unbranded)
    asset_dir = source/'assets/indart3d'
    asset_dir.mkdir(parents=True, exist_ok=True)
    if logo:
        from PIL import Image
        with Image.open(logo) as image:
            if image.size != (1024, 600):
                raise ValueError('El splash original debe ser horizontal de 1024×600; no se reconstruye ni modifica.')
        shutil.copyfile(logo, asset_dir/'splash_0.png')
        shutil.copyfile(asset_dir/'splash_0.png', source/'assets/splash.png')
        shutil.copyfile(logo, asset_dir/'INDART3D-original.png')
        metadata['splash_sha256'] = sha(asset_dir/'splash_0.png')
    (asset_dir/'distribution.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    # Buildroot y CMake invocan este script con argumentos distintos: ambos leen la misma versión.
    updater = '''#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json
from pathlib import Path
version = json.loads(Path('assets/indart3d/distribution.json').read_text())['version']
Path('version.h').write_text('#pragma once\\n#define FIRMWARE_VERSION '+json.dumps(version)+'\\n')
PY
'''
    (source/'scripts/update_version.sh').write_text(updater, encoding='utf-8', newline='\n')
    # La interfaz añade la marca sin alterar la versión numérica usada por el actualizador.
    edit(source/'src/UI/Screens/Settings/SettingsView.cpp', 'FIRMWARE_VERSION, BuildDateText, BuildTimeSuffix', 'FIRMWARE_VERSION " INDART3D", BuildDateText, BuildTimeSuffix')
    extra = '''# INDART3D: conservar el formato oficial e incluir las rutas de arranque.
mkdir -p out/update/etc/splash
cp assets/indart3d/distribution.json out/update/etc/indart3d-release.json
if [ -f assets/indart3d/splash_0.png ]; then
    cp assets/indart3d/splash_0.png out/update/etc/splash/splash_0.png
fi
'''
    edit(source/'scripts/create_upgrade.sh', 'echo "Creating upgrade archive..."', extra+'\necho "Creating upgrade archive..."')
    defconfig = buildroot/'configs/duet3d_duetscreen_defconfig'
    hook = ROOT/'scripts/post_build_indart.sh'
    edit(defconfig, 'BR2_ROOTFS_POST_BUILD_SCRIPT="board/duet3d/duetscreen/scripts/post-build.sh"',
         'BR2_ROOTFS_POST_BUILD_SCRIPT="board/duet3d/duetscreen/scripts/post-build.sh '+hook.as_posix()+'"')
    for name, digest in frozen.items():
        if sha(source/name) != digest:
            raise ValueError(f'Se ha alterado la funcionalidad congelada: {name}')
    print('Fuente preparada. Branding:', not unbranded)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--buildroot', type=Path, required=True)
    parser.add_argument('--allow-unbranded', action='store_true')
    args = parser.parse_args()
    prepare(args.source.resolve(), args.buildroot.resolve(), args.allow_unbranded)
