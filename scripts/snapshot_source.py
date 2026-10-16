"""Fuente técnica de auditoría, separada de los dos instaladores."""
import subprocess
import zipfile
from pathlib import Path

source = Path('DuetScreen')
names = set(subprocess.check_output(['git', '-C', str(source), 'ls-files'], text=True).splitlines())
names.update(str(p.relative_to(source)).replace('\\', '/') for p in (source/'assets/indart3d').rglob('*') if p.is_file())
names.update(('src/utils/IndartDistribution.h', 'src/utils/IndartVersionPolicy.h'))
with zipfile.ZipFile('artifacts/modified-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(names):
        if (source/name).is_file():
            archive.write(source/name, name)
