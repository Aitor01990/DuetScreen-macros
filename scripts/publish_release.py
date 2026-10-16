"""Publicación explícita: no reemplaza tags, Releases ni assets existentes."""
import json
import os
import subprocess
from pathlib import Path
from distribution import config, sha


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True)


def main():
    data = config()
    tag = data['version']
    if os.environ.get('EXPECTED_VERSION') != tag or os.environ.get('HARDWARE_CONFIRMED') != 'true':
        raise ValueError('Falta confirmar versión y prueba física.')
    manifest = json.loads(Path('artifacts/build-manifest.json').read_text())
    commit = os.environ['GITHUB_SHA']
    if not manifest['branded'] or not manifest['sd_verified'] or manifest['source_commit'] != commit:
        raise ValueError('Compilación sin branding, imagen SD verificada o procedencia válida.')
    if manifest['version'] != tag or manifest['update_repository'] != data['update_repository']:
        raise ValueError('Manifiesto incoherente.')
    for name in ('DuetScreen.tar.gz', 'sdcard.img'):
        if sha(Path('artifacts')/name) != manifest['files'][name]:
            raise ValueError('Checksum incorrecto: '+name)
    repo = os.environ['GITHUB_REPOSITORY']
    # Un 403/500 no equivale a que no exista: listar con éxito antes de continuar.
    releases = json.loads(gh('api', '--paginate', '--slurp', f'repos/{repo}/releases?per_page=100'))
    if any(r['tag_name'] == tag for page in releases for r in page):
        raise ValueError('La Release ya existe; no se sobrescribirá.')
    tags = json.loads(gh('api', '--paginate', '--slurp', f'repos/{repo}/git/matching-refs/tags/{tag}'))
    if any(r['ref'] == 'refs/tags/'+tag for page in tags for r in page):
        raise ValueError('El tag ya existe. Revisar manualmente, sin sobrescribir.')
    notes = Path('artifacts/RELEASE-NOTES.md')
    notes.write_text(f'# DuetScreen {tag} — INDART3D\n\nBase DuetScreen v1.0.0; Buildroot v0.4.4; ARM T113.\n\n'
                     f'Commit: `{commit}`. Validaciones automáticas superadas y prueba física confirmada por el operador.\n\n'
                     'Instalación USB y microSD: consultar docs/USUARIOS.md. RRF mínimo 3.6.2.\n\n'
                     'Incidencia de primera carga de miniaturas pendiente; sin cambios de caché en esta revisión.\n\n'
                     '## SHA256\n\n```text\n'+Path('artifacts/SHA256SUMS.txt').read_text()+'```\n')
    # La Release sólo se hace visible cuando los cuatro assets se han subido correctamente.
    gh('release', 'create', tag, '--repo', repo, '--target', commit, '--draft', '--title', f'DuetScreen {tag} — INDART3D', '--notes-file', str(notes))
    gh('release', 'upload', tag, '--repo', repo, 'artifacts/DuetScreen.tar.gz', 'artifacts/sdcard.img',
       'artifacts/SHA256SUMS.txt', 'artifacts/build-manifest.json')
    gh('release', 'edit', tag, '--repo', repo, '--draft=false', '--latest')


if __name__ == '__main__':
    main()
