# DuetScreen: miniaturas de macros

Base exacta: DuetScreen v1.0.0 (8cf206ddd2aad3a55852eb2125a318d94c8601f3), Buildroot v0.4.4 (7b01688559a5602a55d564651db279674a237263). Destino: ARM T113, preset T113-Release. RRF minimo compatible: 3.6.2; no se garantiza RRF 3.6.1.

## Descargar e instalar

1. Abre la pestana Actions y selecciona DuetScreen v1.0.0 - Macros ARM T113. Puedes repetirlo con Run workflow.
2. Espera al resultado verde de la ejecucion y abre su resumen.
3. En Artifacts descarga DuetScreen-USB-T113 e inicia sesion en GitHub si lo pide.
4. En Windows extrae solamente el ZIP descargado. Dentro estara DuetScreen.tar.gz junto a hashes, manifiesto, parche y fuentes modificadas.
5. Copia DuetScreen.tar.gz, SIN descomprimirlo, a la raiz del pendrive.
6. Con la maquina en reposo, conecta el USB a DuetScreen, acepta la actualizacion y espera al reinicio.
7. Comprueba conexion, lista, mosaicos, confirmacion de macros y Trabajos.

Una compilacion verde verifica arquitectura ELF32 ARM hard-float, marca del codigo modificado, contenido y permisos del paquete oficial. No demuestra una prueba fisica en pantalla. No instales artefactos de una ejecucion fallida.

## Imagenes y pruebas

Incluye una imagen PNG Base64 de hasta 64x64 para los listados y otra de hasta 400x400 para el dialogo ampliado. Una macro con solo 300x300 no tiene miniatura pequena para el listado inicial. Se mantienen la ejecucion original, la confirmacion y los iconos de carpeta.

M36 reconoce metadatos; falta comprobar M36.1 o rr_thumbnail y el funcionamiento fisico en tu configuracion. Usa el offset real que devuelva M36, no un numero fijo.

## Ajustes y recuperacion

Anota tus ajustes antes de actualizar: el script oficial pre-update elimina /var/lib/duetscreen y sustituye los assets.

Conserva en otra carpeta el DuetScreen.tar.gz original de https://github.com/Duet3D/DuetScreen/releases/tag/v1.0.0 . Si necesitas volver atras y funciona la interfaz, copia el paquete original al USB y aplica la actualizacion.

Si no funciona la interfaz, el README oficial documenta renombrar una COPIA del paquete original como update.tar.gz y ponerla en la raiz del USB o microSD; con microSD se aplica al encender. Comprueba las extensiones en Windows. Si el sistema tampoco arranca, sigue la recuperacion oficial de la microSD. Referencia: https://github.com/Duet3D/DuetScreen/blob/v1.0.0/README.md#updating .

## Compilacion

La primera compilacion puede durar horas. El workflow usa dos trabajos, libera espacio y exige 30 GiB libres. Limite de ejecucion: seis horas. No utiliza secretos de Duet3D ni PAT privados. El propio workflow contiene las modificaciones y comprueba que el parche generado coincide byte a byte con el parche revisado (SHA256 123cbdab41f4f2f4412ca730cd2406e2a66dae938c3dfa4ae8736037b17cd5ac).

Los artefactos de firmware se guardan 14 dias; los logs, 7 dias. Si falla, abre el primer paso rojo y consulta DuetScreen-build-logs. El paquete instalable solo se publica despues de superar las comprobaciones.
