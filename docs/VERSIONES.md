# Versiones e historial

La única fuente de verdad es [`distribution/config.json`](../distribution/config.json), campo `version`.

Formato: `vA.B.C.D`, cuatro enteros entre 0 y 65535. `A.B.C` es la base oficial; `D` la revisión INDART3D. No añadir sufijos al canal estable. La comparación es numérica: v1.0.0.10 supera v1.0.0.2. El selector estable rechaza etiquetas de tres componentes y preliminares.

`prepare_source.py` copia esta versión a los recursos y sustituye `scripts/update_version.sh` para que tanto CMake como Buildroot lean esos mismos metadatos, aunque Buildroot pase un `git describe` diferente. `version.h` se genera, no se edita. La versión numérica se usa en el binario/actualizador; la sección general añade la marca INDART3D a su presentación. Paquete, imagen y Release se comprueban contra la misma configuración.

## Historial

### v1.0.0.1 — en preparación, no publicada

- Mantiene exactamente los siete archivos de miniaturas funcionales.
- Extrae modificaciones y comprobaciones del YAML a scripts mantenibles.
- Configuración central, revisión de cuatro componentes, canal GitHub estable propio.
- Confirmación de actualización también desde el botón de desarrollador.
- Preparación de branding horizontal en USB y SD; PNG original recibido e incorporado sin modificar.
- Workflows separados para validación, compilación de pruebas y publicación de los mismos artefactos ensayados.
- Manuales de usuario y desarrollo; caché pendiente sin cambios.

### Estado funcional anterior — 15 de octubre de 2026

DuetScreen v1.0.0 con modificación de thumbnails, commit de distribución `9d7d4366e47023fc6c8b54256f13a270be164fb2`. Instalación y funcionamiento físico confirmados por el propietario. No se rebautiza ese binario como v1.0.0.1.

## Próximas versiones

v1.0.0.2 se reserva para una modificación visible pequeña y la prueba de actualización Wi-Fi, después de validar la primera y recibir autorización expresa. No está publicada ni se publica automáticamente por preparar estos workflows.

Un futuro salto de base a v1.0.1 requerirá revisión y aprobación independiente de los commits fijados; su primera revisión sería v1.0.1.1. Este proyecto no actualiza automáticamente las bases.
