# Compatibilidad y recuperación técnica

## Bases fijadas

| Componente | Referencia obligatoria |
| --- | --- |
| DuetScreen v1.0.0 | `8cf206ddd2aad3a55852eb2125a318d94c8601f3` |
| Buildroot v0.4.4 | `7b01688559a5602a55d564651db279674a237263` |
| Hardware y preset | DuetScreen 7, ARM T113, `T113-Release`, ELF32 ARM hard-float |
| RepRapFirmware | Mínimo oficial 3.6.2; no garantizar 3.6.1 |
| Orientación personalizada | Horizontal, rotación 0, 1024×600 |

El logotipo original recibido se copia sin modificar: PNG RGB de 1024×600, SHA256 `a66d80358eb8b77a758119ae8e0e3efb2fe3a77b2f2ddfaca87296dfbec29c31`. Se conserva también como recurso original para auditoría.

## Aplicación frente a sistema completo

`DuetScreen.tar.gz` mantiene la estructura oficial: `usr/bin/DuetScreen`, `etc/assets/`, splash, scripts `pre-update`/`post-update` y marcador `buildroot_version`. Nuestro añadido instala además `/etc/splash/splash_0.png` y `/etc/indart3d-release.json`.

El servicio oficial extrae el paquete sobre el sistema existente. El marcador en la raíz del tar sirve para comparar compatibilidad; **no sustituye `/etc/buildroot_version` ni actualiza kernel, bootloader, bibliotecas del sistema o NAND**. El pre-update elimina assets y `/var/lib/duetscreen`; no borra `/etc/duetscreen.json` ni el Wi-Fi. El paquete preparado tampoco contiene esos ajustes. Una tarjeta nueva sí sustituye el sistema y necesita restauración/reconfiguración.

`sdcard.img` contiene MBR, arranque `awboot` fuera de la tabla, partición FAT de arranque y partición ext4. La configuración oficial incluye kernel, árbol de dispositivos, OP-TEE y rootfs. El hook INDART3D se ejecuta después del overlay para que no reaparezca el splash oficial. Se comprueba el binario dentro de la partición SD real frente al del USB; no basta con examinar `output/target`.

## Cómo comprobar versiones

En Ajustes generales, el código muestra versión de firmware y Buildroot. La primera procede de `FIRMWARE_VERSION`; la segunda lee `/etc/buildroot_version`. Si hay acceso de mantenimiento ya autorizado, ese archivo identifica la revisión del proyecto Buildroot y `/etc/indart3d-release.json` la distribución compilada. No confundas la revisión v0.4.x del proyecto con el número interno 202x.xx de Buildroot que pueda aparecer en `os-release`.

## Sistemas v0.4.2

Se consultó el script oficial `S50rootfs-upgrade` de la etiqueta v0.4.2: admite `update.tar.gz` en `/boot` y USB, compara major/minor y sólo advierte ante diferencia de patch. El v0.4.4 conserva ese criterio. Un paquete construido para v0.4.4 puede por ello ser aceptado sobre v0.4.2 con aviso; **eso no demuestra compatibilidad binaria** y no actualiza el sistema a v0.4.4.

Antes de usarlo en clientes, valida el hardware, bibliotecas, servicios y resultados físicos de esa combinación. Si se necesita realmente la nueva base, el procedimiento previsto es reinstalar una microSD con la imagen completa en equipos cuyo arranque microSD esté confirmado. No se han eliminado ni relajado comprobaciones de compatibilidad. Para sistemas anteriores/desconocidos no se garantiza la presencia del actualizador USB: revisar su script/versión y modo de arranque antes de actuar.

## microSD y NAND

La microSD usa una raíz ext4 y una partición FAT visible desde Windows; NAND utiliza almacenamiento flash/UBI y su propio bootloader. Las opciones de primer arranque de `BOOT.md` se documentan para microSD, no para NAND. Preservar la tarjeta original ofrece una recuperación distinta de reprogramar memoria interna.

Buildroot genera técnicamente un paquete `output/images/update.tar.gz` con `awboot-boot-spi.bin`, DTB, OP-TEE, kernel, `rootfs.ubi` y `post-update`. No es nuestro actualizador de aplicación, aunque comparta un nombre de recuperación. El `post-update` oficial comprueba que el sistema esté arrancado desde ext4 antes de escribir NAND, y utiliza borrado/escritura de MTD y UBI. Puede alterar bootloader y sistema y puede implicar gestión de bloques defectuosos. No se entrega como tercer instalador normal ni se automatiza aquí.

No usar ese paquete como alternativa para actualizar remotamente clientes o evitar abrir el equipo sin un procedimiento de laboratorio independiente. No se implementan actualizadores experimentales de kernel, NAND, bootloader o microSD.

## Recuperacion oficial de la aplicacion

El README oficial describe un método sin interfaz gráfica funcional: una **copia del paquete de aplicación compatible** se llama `update.tar.gz` y se coloca en la raíz del USB; el servicio de Buildroot la detecta. En microSD puede ponerse en la partición FAT `/boot` para procesarla al arrancar. Deben funcionar el sistema y `S50rootfs-upgrade`; no recupera un kernel/bootloader que no arranque.

Es un procedimiento técnico: el servicio puede aplicar el archivo sin confirmación gráfica. Verifica versión del sistema, procedencia y contenido del tar antes de usarlo. No confundir con el paquete NAND generado por Buildroot, no eliminar controles y no asumir que cualquier pantalla antigua admite este mecanismo. No se prescribe como rescate universal de NAND.

Si la aplicación funciona, el USB normal `DuetScreen.tar.gz` con confirmación es la vía habitual. Si el sistema microSD no arranca, usa una tarjeta nueva con imagen aprobada. La prueba física de la recuperación en cada combinación concreta sigue pendiente.

## Configuración y restauración

La fuente T113 usa `/etc/duetscreen.json` para preferencias; `NVS_FOLDER=/var/lib/duetscreen` corresponde a cachés/estado, no al archivo principal. `NetworkHelper.cpp` guarda Wi-Fi en `/etc/wpa_supplicant.conf`. `S02setup` admite `duetscreen.json`, `wpa_supplicant.conf` y `dhcpcd.conf` en `/boot`, y se desactiva tras el primer arranque. Los pasos de Windows están en [Usuarios](USUARIOS.md#copia-de-seguridad), sin afirmar una copia completa de la pantalla.

## Fuentes primarias revisadas

- [DuetScreen v1.0.0: README y actualización](https://github.com/Duet3D/DuetScreen/blob/8cf206ddd2aad3a55852eb2125a318d94c8601f3/README.md#updating).
- [UpgradeHelper.cpp](https://github.com/Duet3D/DuetScreen/blob/8cf206ddd2aad3a55852eb2125a318d94c8601f3/src/utils/UpgradeHelper.cpp), [StorageHelper.cpp](https://github.com/Duet3D/DuetScreen/blob/8cf206ddd2aad3a55852eb2125a318d94c8601f3/src/utils/StorageHelper.cpp), [DisplayHelper.cpp](https://github.com/Duet3D/DuetScreen/blob/8cf206ddd2aad3a55852eb2125a318d94c8601f3/src/utils/DisplayHelper.cpp).
- [Buildroot v0.4.4: primer arranque](https://github.com/Duet3D/buildroot-duetscreen/blob/7b01688559a5602a55d564651db279674a237263/BOOT.md).
- [S50rootfs-upgrade v0.4.4](https://github.com/Duet3D/buildroot-duetscreen/blob/7b01688559a5602a55d564651db279674a237263/board/duet3d/duetscreen/rootfs_overlay/etc/init.d/S50rootfs-upgrade).
- [S50rootfs-upgrade v0.4.2](https://github.com/Duet3D/buildroot-duetscreen/blob/v0.4.2/board/duet3d/duetscreen/rootfs_overlay/etc/init.d/S50rootfs-upgrade).
- [Generación de imagen](https://github.com/Duet3D/buildroot-duetscreen/blob/7b01688559a5602a55d564651db279674a237263/board/duet3d/duetscreen/scripts/genimage.cfg) y [post-update NAND](https://github.com/Duet3D/buildroot-duetscreen/blob/7b01688559a5602a55d564651db279674a237263/board/duet3d/duetscreen/bin/post-update).
