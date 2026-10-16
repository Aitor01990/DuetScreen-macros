# DuetScreen — INDART3D

DuetScreen 7 ARM T113 · Base **v1.0.0** · Buildroot **v0.4.4** · Revisión prevista **v1.0.0.1** · RepRapFirmware mínimo **3.6.2**.

**En preparación, no publicada:** PNG original incorporado; faltan la compilación ARM y la validación de los dos instaladores y del hardware. La modificación anterior de miniaturas sí fue validada físicamente por el propietario. No instalar archivos de una compilación fallida.

## Usuarios e instalación

- [Descargar versiones estables](https://github.com/Aitor01990/DuetScreen-macros/releases) — todavía sin versión INDART3D publicada.
- [Actualizar mediante USB](docs/USUARIOS.md#actualizar-mediante-usb).
- [Actualizar mediante Wi-Fi](docs/USUARIOS.md#actualizar-mediante-wi-fi).
- [Instalar desde microSD](docs/USUARIOS.md#instalar-desde-microsd).
- [Copia de seguridad y recuperación](docs/USUARIOS.md#copia-de-seguridad).
- [Problemas frecuentes](docs/USUARIOS.md#problemas-frecuentes).

## Desarrollo y mantenimiento

- [Compilar desde Windows con GitHub](docs/DESARROLLO.md#compilar-desde-github).
- [Publicar nuevas versiones](docs/DESARROLLO.md#publicar-una-version).
- [Versiones e historial](docs/VERSIONES.md).
- [Compatibilidad, sistemas antiguos y NAND](docs/COMPATIBILIDAD.md).
- [Incidencias pendientes](PENDIENTES.md).
- [Resultados de validación](docs/VALIDACION.md).

Los dos instaladores previstos son `DuetScreen.tar.gz` (aplicación USB/Wi-Fi) y `sdcard.img` (sistema completo con esa misma aplicación personalizada). La SD no necesita después el paquete USB de la misma versión. Checksums y manifiesto son comprobantes, no un tercer instalador.

Se conservan las macros `.g`, miniaturas de listas, mosaicos y confirmación, subcarpetas, espacios y ejecución original. No se intenta corregir la incidencia conocida de primera carga.
