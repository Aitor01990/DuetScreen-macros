"""Configuración central y validaciones de distribución; sólo biblioteca estándar."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda: file.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def version(value):
    if not re.fullmatch(r'v\d{1,5}(?:\.\d{1,5}){3}', value):
        raise ValueError('Se requiere una versión estable vA.B.C.D.')
    result = tuple(map(int, value[1:].split('.')))
    if any(n > 65535 for n in result):
        raise ValueError('Componente de versión superior a 65535.')
    return result


def config():
    data = json.loads((ROOT/'distribution/config.json').read_text(encoding='utf-8'))
    version(data['version'])
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', data['update_repository']):
        raise ValueError('Repositorio de actualizaciones inválido.')
    if data['upstream_commit'] != '8cf206ddd2aad3a55852eb2125a318d94c8601f3' or data['buildroot_commit'] != '7b01688559a5602a55d564651db279674a237263':
        raise ValueError('No se permite cambiar las bases oficiales en esta revisión.')
    if data['preset'] != 'T113-Release' or data['buildroot_version'] != 'v0.4.4':
        raise ValueError('Destino o Buildroot no autorizado.')
    return data


def check_logo(data):
    path = ROOT/data['logo_file']
    if not data['logo_sha256'] or not path.is_file() or sha(path) != data['logo_sha256']:
        raise ValueError('Falta el PNG original INDART3D o su SHA256 aprobado. No se puede generar una distribución final.')
    from PIL import Image
    with Image.open(path) as image:
        if image.format != 'PNG':
            raise ValueError('El logotipo original debe ser PNG.')
        image.verify()
    return path


if __name__ == '__main__':
    print(config()['version'])
