# Informe de validación — 16 de octubre de 2026

## Realizado localmente

- Confirmación de que el repositorio local y `main` remoto parten de `9d7d4366e47023fc6c8b54256f13a270be164fb2`.
- Copia Git recuperable del estado anterior y ramas separadas de respaldo/desarrollo. Ramas creadas también en GitHub desde la sesión del propietario.
- Extracción del Python incrustado en el workflow funcional a `scripts/apply_macros.py`. Se verificó la transformación sobre archivos originales de DuetScreen v1.0.0 y Buildroot v0.4.4.
- Los siete archivos de miniaturas resultantes mantienen exactamente los hashes ya aprobados en el workflow anterior. No se introdujeron cambios para corregir la incidencia THUMB-001.
- PNG original recibido desde la ruta indicada por el propietario: PNG RGB 1024×600, SHA256 `a66d80358eb8b77a758119ae8e0e3efb2fe3a77b2f2ddfaca87296dfbec29c31`. Copia exacta en recursos y rutas de splash de la fuente preparada, sin redimensionar ni recodificar.
- Ocho pruebas Python superadas: configuración, versiones, control de branding, comprobación ELF, estructura/permisos del tar, rechazo de imagen inválida y controles de publicación. Se comprobó que un tag/Release existente bloquea la publicación y que un fallo de subida deja el borrador sin hacerlo estable. Los paquetes y ELF de las pruebas unitarias son fixtures sintéticos, no instaladores entregables.
- Compilación y ejecución nativa Windows del selector C++ que se integra realmente en UpgradeHelper: cuatro componentes, orden numérico, rechazo de sufijos y desbordamientos, filtro de draft/prerelease, elección de la mayor versión aunque las Releases estén desordenadas, asset/nombre/origen, paginación y fallos HTTP/JSON.
- Compilación sintáctica Python, lectura de los tres YAML y validación con el binario oficial Windows de actionlint, sin errores. Se revisaron permisos y pasos. Esto no equivale a una ejecución de Actions.
- Investigación del código de arranque, configuración y recuperación de v0.4.4 y del servicio de actualización v0.4.2. No se probó una migración de sistema en hardware.

El compilador local necesitó ejecutarse fuera del sandbox para poder crear sus archivos temporales. El ensayo final pasó; no se usa Linux local ni se instala software en la pantalla.

## Preparado, pendiente de ejecución remota

- Compilación completa ARM T113 con las bases fijadas y submódulos.
- Validación del ELF ARM real y su versión incrustada.
- Generación y validación del `DuetScreen.tar.gz` real: scripts oficiales, permisos, recursos, logo y versión.
- Generación de `sdcard.img` e inspección de su partición ext4: mismo binario que USB, metadatos, Buildroot y las dos rutas de splash.
- Ejecución de los workflows de validación, compilación y publicación.

La subida de los archivos a la rama pública fue bloqueada por la revisión automática de permisos, que pidió autorización específica para ese envío. No se ha intentado eludir el bloqueo. La configuración y el código quedan preparados localmente para revisión. No hay una Release INDART3D publicada ni se entregan tar/img ficticios.

## Pendiente en pantalla física

- Instalación por USB, logotipo exacto horizontal y versión v1.0.0.1.
- Arranque directo desde nuestra SD sin aplicar después el USB.
- Lista/mosaicos, imagen ampliada, subcarpetas, espacios, macro sin imagen, ejecución original y thumbnails de trabajos.
- Conservación de JSON/Wi-Fi al actualizar, exportación y restauración en primer arranque de nueva SD.
- Avisos y comportamiento ante error de descarga/compatibilidad, y recuperación en el modo de arranque concreto.
- Actualización Wi-Fi desde v1.0.0.1 a una revisión posterior sólo cuando se autorice expresamente publicarla. No se publica v1.0.0.2 en este trabajo.

No se debe interpretar la validación física de la modificación anterior de miniaturas como validación de esta nueva distribución.
