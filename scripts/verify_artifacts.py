"""Verifica los paquetes reales; nunca marca una prueba física como realizada."""
import argparse
import json
import shutil
import struct
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from distribution import ROOT, config, check_logo, sha, version


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def verify_binary(binary, data):
    ensure(len(binary) >= 52 and binary[:6] == b'\x7fELF\x01\x01', 'No es ELF32 little endian.')
    ensure(struct.unpack_from('<H', binary, 18)[0] == 40, 'No es ARM.')
    ensure(struct.unpack_from('<I', binary, 36)[0] & 0x400, 'No es ARM hard-float.')
    ensure(data['version'].encode()+b'\0' in binary, 'Versión exacta ausente en el binario.')
    ensure(b'Macro thumbnail support v1' in binary, 'Falta modificación de macros.')
    ensure(('/repos/'+data['update_repository']+'/releases').encode() in binary, 'Actualizador incorrecto.')
    ensure(b'/repos/Duet3D/DuetScreen/releases' not in binary, 'Actualizador oficial todavía presente.')


def verify_usb(package, binary, metadata, source):
    verify_binary(binary, metadata)
    with tarfile.open(package, 'r:gz') as archive:
        members = {}
        for member in archive:
            name = member.name.removeprefix('./')
            ensure(not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts, 'Ruta insegura en paquete.')
            ensure(name not in members, 'Entrada duplicada en paquete.')
            members[name] = member
        for name in ('usr/bin/DuetScreen', 'pre-update', 'post-update', 'buildroot_version', 'etc/indart3d-release.json'):
            ensure(name in members and members[name].isfile(), f'Falta archivo regular {name}.')
        for name in ('usr/bin/DuetScreen', 'pre-update', 'post-update'):
            ensure(members[name].mode & 0o111, f'Falta permiso de ejecución en {name}.')
        def read(name):
            return archive.extractfile(members[name]).read()
        ensure(read('usr/bin/DuetScreen') == binary, 'Binario USB distinto del compilado.')
        ensure(read('buildroot_version').strip().decode() == metadata['buildroot_version'], 'Buildroot USB incorrecto.')
        ensure(json.loads(read('etc/indart3d-release.json')) == metadata, 'Metadatos USB distintos.')
        for name in ('pre-update', 'post-update'):
            ensure(read(name) == (source/'scripts'/name).read_bytes(), 'Scripts oficiales alterados.')
        ensure(any(n.startswith('etc/assets/') for n in members), 'Faltan recursos.')
        if metadata['branded']:
            for name in ('etc/splash.png', 'etc/splash/splash_0.png'):
                ensure(name in members and read(name) == (source/'assets/indart3d/splash_0.png').read_bytes(), f'Splash incorrecto: {name}.')
            ensure(read('etc/assets/indart3d/INDART3D-original.png') == check_logo(config()).read_bytes(), 'PNG original distinto.')


def verify_sd(image, binary, metadata, source):
    # Extraer sólo la partición ext4 del MBR; nunca se monta ni se escribe en dispositivos.
    with Path(image).open('rb') as file:
        mbr = file.read(512)
        ensure(mbr[510:512] == b'\x55\xaa', 'MBR inválido.')
        partitions = [struct.unpack_from('<B3sB3sII', mbr, 446+i*16) for i in range(4)]
        rootfs = [p for p in partitions if p[2] == 0x83]
        ensure(len(rootfs) == 1 and any(p[2] == 0x0c for p in partitions), 'Particiones SD incorrectas.')
        offset, size = rootfs[0][4]*512, rootfs[0][5]*512
        ensure(size > 0 and offset+size <= Path(image).stat().st_size, 'Partición truncada.')
        file.seek(offset)
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            ext4 = temp/'rootfs.ext4'
            with ext4.open('wb') as out:
                remaining = size
                while remaining:
                    block = file.read(min(remaining, 1024*1024))
                    ensure(bool(block), 'Imagen truncada.')
                    out.write(block)
                    remaining -= len(block)
            with ext4.open('rb') as out:
                out.seek(1024+56)
                ensure(out.read(2) == b'\x53\xef', 'No hay un sistema ext válido.')
            def dump(path):
                output = temp/'dumped'
                output.unlink(missing_ok=True)
                subprocess.run(['debugfs', '-R', f'dump {path} {output.as_posix()}', str(ext4)], check=True, capture_output=True)
                ensure(output.is_file(), f'Falta {path} en la imagen SD.')
                return output.read_bytes()
            ensure(dump('/usr/bin/DuetScreen') == binary, 'Binario SD distinto del USB.')
            ensure(json.loads(dump('/etc/indart3d-release.json')) == metadata, 'Versión/metadatos SD distintos.')
            ensure(dump('/etc/buildroot_version').strip().decode() == metadata['buildroot_version'], 'Buildroot SD incorrecto.')
            if metadata['branded']:
                splash = (source/'assets/indart3d/splash_0.png').read_bytes()
                ensure(dump('/etc/splash.png') == splash, 'Splash SD incorrecto.')
                ensure(dump('/etc/splash/splash_0.png') == splash, 'Splash de rotación SD incorrecto.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('DuetScreen'))
    parser.add_argument('--buildroot', type=Path, default=Path('buildroot-duetscreen'))
    parser.add_argument('--output', type=Path, default=Path('artifacts'))
    parser.add_argument('--full-image', action='store_true')
    parser.add_argument('--allow-unbranded', action='store_true')
    args = parser.parse_args()
    data = config()
    metadata = json.loads((args.source/'assets/indart3d/distribution.json').read_text())
    ensure(all(metadata[k] == v for k, v in data.items()), 'Configuración de fuente incoherente.')
    ensure(args.allow_unbranded or metadata['branded'], 'No se puede validar una distribución final sin logotipo.')
    expected = json.loads((ROOT/'patches/macros-sha256.json').read_text())
    for name, digest in expected.items():
        ensure(sha(args.source/name) == digest, 'Código de thumbnails alterado: '+name)
    binary = (args.buildroot/'output/target/usr/bin/DuetScreen').read_bytes()
    package = args.output/'DuetScreen.tar.gz'
    verify_usb(package, binary, metadata, args.source)
    files = [package]
    if args.full_image:
        sd = args.output/'sdcard.img'
        verify_sd(sd, binary, metadata, args.source)
        files.append(sd)
    manifest = dict(metadata, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                    hardware_tested=False, sd_verified=args.full_image,
                    files={p.name: sha(p) for p in files})
    (args.output/'build-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (args.output/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
