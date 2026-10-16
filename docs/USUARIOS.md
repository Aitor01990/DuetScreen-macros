# Manual de usuario e instalación

[Portada](../README.md) · [Compatibilidad](COMPATIBILIDAD.md)

Guía del código preparado para v1.0.0.1 INDART3D. Esta revisión aún no está publicada ni probada físicamente. Las instrucciones se han contrastado con las bases fijadas; la instalación anterior de miniaturas fue validada por el propietario.

## Qué archivos existen

En [GitHub Releases](https://github.com/Aitor01990/DuetScreen-macros/releases), selecciona la versión estable y despliega **Assets**.

| Archivo | Uso y contenido |
| --- | --- |
| `DuetScreen.tar.gz` | Actualiza la aplicación: ejecutable INDART3D, miniaturas de macros, actualizador, recursos, logotipo y scripts oficiales |
| `sdcard.img` | Instalación/recuperación completa: arranque, Buildroot v0.4.4 y la misma aplicación personalizada con todos sus recursos |
| `SHA256SUMS.txt` | Huellas para comprobar la integridad de los instaladores |
| `build-manifest.json` | Versión, bases, commit, logotipo y comprobaciones automáticas |

Los ZIP de código fuente añadidos por GitHub no son instaladores. Si no hay una Release estable INDART3D, no hay todavía una descarga oficial para clientes.

## Antes de instalar

Comprueba DuetScreen 7 ARM T113 y RRF 3.6.2 o posterior; RRF 3.6.1 no está garantizado. Anota las versiones de aplicación y Buildroot en Ajustes, sección general. Si el sistema es v0.4.2 o desconocido, consulta al servicio técnico antes de actualizar. Que acepte el paquete no garantiza compatibilidad de bibliotecas.

Detén la impresión, utiliza alimentación estable y respalda los ajustes. No interrumpas la instalación. Conserva la microSD original y prepara otra siempre que sea posible.

## Actualizar mediante USB

1. Descarga `DuetScreen.tar.gz` de la Release aprobada.
2. Usa un pendrive que la pantalla reconozca; FAT32 es una opción habitual desde Windows. No formatees uno con datos sin respaldarlos.
3. Copia el archivo a la raíz **sin descomprimir ni renombrar**. Activa las extensiones de archivo en el Explorador y evita `.tar.gz.gz`.
4. Conecta el pendrive a la pantalla encendida y en reposo. Revisa el puerto/modo USB: el USB-C puede estar reservado para Wi-Fi o comunicación.
5. La aplicación detecta el archivo y muestra la confirmación. Acepta para iniciar o cancela.
6. Espera a que termine y vuelva a abrirse la aplicación. El código reinicia servicios; no implica necesariamente un reinicio completo de placa.
7. Comprueba la versión INDART3D en Ajustes, conexión, macros y trabajos de impresión. Retira el USB al terminar.

La aplicación recuerda la fecha del archivo para evitar avisos repetidos. Un aviso de Buildroot exige revisar compatibilidad; no elimines comprobaciones. El paquete de aplicación no cambia kernel/bootloader ni convierte Buildroot v0.4.2 en v0.4.4.

## Actualizar mediante Wi-Fi

Requiere una pantalla que ya use nuestra distribución. La versión oficial o la modificación anterior no necesariamente consultan nuestro GitHub.

1. En Ajustes configura la conexión Wi-Fi de la pantalla en **Red de pantalla**. Con Wi-Fi interno, el modo USB-C debe corresponder a **Internal WiFi / Wi-Fi interno**, según el idioma. Conectarse a la Duet no garantiza salida a Internet.
2. El código comprueba actualizaciones al pasar de no tener dirección IP a tenerla. No consulta continuamente: si ya tenías red cuando se publicó una versión, vuelve a conectar el Wi-Fi o reinicia la aplicación.
3. Si existe una versión estable superior, aparece un aviso con versión disponible e instalada.
4. Acepta para descargar e instalar o cancela. No instala por el simple hecho de estar conectado.
5. Espera y comprueba la versión en Ajustes.

El botón existente **Actualizar desde la última versión de GitHub**, en ajustes de desarrollador cuando estén visibles, se adapta para comprobar y mostrar la misma confirmación antes de instalar. El recorrido completo y los textos visibles de esta revisión quedan pendientes de prueba física.

Si no aparece actualización, comprueba Internet, repositorio correcto, Release pública estable superior y asset `DuetScreen.tar.gz`. Borradores, preliminares, versiones iguales/inferiores y nombres distintos se ignoran. .10 es mayor que .2. Sin conexión, por límite de peticiones GitHub o error de descarga, conserva la instalación y prueba después o usa USB. El funcionamiento local continúa sin Internet.

## Instalar desde microSD

**Grabar la imagen borra todo el contenido anterior de la tarjeta seleccionada.** Si Windows ofrece formatear una partición desconocida después de grabar, cancela: puede ser la partición Linux del sistema.

1. Usa este procedimiento para equipos confirmados para arrancar desde microSD: instalación nueva, recuperación o migración completa a la base prevista. Descarga `sdcard.img` de la Release aprobada.
2. Apaga y desconecta la alimentación conforme a las instrucciones del fabricante. Retira la microSD cuando corresponda, siempre con el equipo apagado.
3. Conserva la original. Conecta otra microSD adecuada mediante lector Windows, de capacidad superior al tamaño de la imagen. El modelo/capacidad deben validarse en tu equipo.
4. Abre [balenaEtcher](https://etcher.balena.io/) o [Rufus](https://rufus.ie/) de su web oficial.
5. Selecciona `sdcard.img` y verifica cuidadosamente la unidad de destino.
6. Inicia la escritura y espera a su finalización y verificación. Si Rufus pregunta, usa escritura de imagen sin modificar el contenido.
7. Antes del primer arranque puedes [restaurar ajustes compatibles](#copia-de-seguridad) en la partición de arranque visible desde Windows.
8. Expulsa de forma segura, introduce la tarjeta en la pantalla apagada y enciende.
9. Comprueba arranque horizontal INDART3D, versión, conexión a Duet, Wi-Fi e idioma.

**Si la imagen incorpora v1.0.0.1 INDART3D, no instales después el USB de esa misma versión.** Las posteriores revisiones podrán instalarse por USB o Wi-Fi.

En un equipo NAND, grabar una microSD no equivale a actualizar la NAND. No cambies su arranque ni uses paquetes NAND por este manual; consulta [Compatibilidad](COMPATIBILIDAD.md#microsd-y-nand).

## Copia de seguridad

| Información | Ubicación y conservación |
| --- | --- |
| Macros, G-code y archivos de Duet | Están en la electrónica Duet; estos instaladores de pantalla no los sustituyen. Respáldalos aparte desde Duet Web Control |
| Configuración RepRapFirmware | Está en la Duet (`sys`, etc.); no forma parte de la copia de pantalla |
| Conexión, idioma y preferencias de pantalla | `/etc/duetscreen.json`; el paquete de aplicación preparado no lo incluye y el pre-update no lo elimina. Grabar SD sustituye el sistema anterior |
| Wi-Fi y claves | `/etc/wpa_supplicant.conf`; no se exportan en el JSON |
| IP fija de pantalla | `/etc/dhcpcd.conf`; tampoco se exporta en el JSON |
| Caché de miniaturas | `/var/lib/duetscreen`; el pre-update oficial la elimina. No contiene la copia completa de ajustes |
| Otros archivos de microSD | Se pierden al grabar de nuevo la tarjeta |

### Respaldar configuración

Si está disponible en Ajustes de desarrollador, pulsa **Subir configuración a Duet**. El código exporta `StorageHelper::dump()` a `duetscreen.json` en el directorio de sistema de la Duet (normalmente `0:/sys/duetscreen.json`). Descárgalo después a Windows con Duet Web Control y comprueba que existe y contiene JSON válido. Pulsar el botón no demuestra que haya terminado la transferencia.

No es una copia completa: no incluye claves Wi-Fi, IP fija del sistema, archivos arbitrarios ni macros. Anota método de comunicación, IP/puerto y contraseña de conexión a Duet, modo USB-C, SSID/clave Wi-Fi, IP fija si existe, idioma, orientación horizontal, brillo, tema y preferencias. Guarda el JSON y las claves de forma privada.

### Restaurar en una tarjeta nueva

El script oficial `S02setup` de v0.4.4 copia `/boot/duetscreen.json` a `/etc/duetscreen.json`. Puedes poner el JSON respaldado en la raíz de la partición de arranque visible en Windows **tras grabar la imagen y antes del primer arranque**. El servicio se desactiva después de ese arranque: no se promete restauración posterior copiando el archivo a cualquier USB.

En ese mismo primer arranque admite `wpa_supplicant.conf` y `dhcpcd.conf` válidos. El botón de exportar JSON no los genera. Sin copias fiables, vuelve a introducir las redes y ajustes desde la interfaz. Revisa direcciones y claves antes de reutilizar configuraciones de otra pantalla.

Restauración y persistencia de cada preferencia están comprobadas por lectura del código, pendientes de prueba física en esta distribución.

## Recuperación

- **La aplicación funciona pero falla una revisión:** conserva el paquete anterior compatible y consulta al técnico para regresar por USB. Wi-Fi sólo ofrece versiones superiores. Los ajustes de una versión futura pueden no ser compatibles hacia atrás.
- **No abre la aplicación pero el sistema microSD sí arranca:** existe el mecanismo oficial `update.tar.gz`, reservado al procedimiento técnico de [Compatibilidad](COMPATIBILIDAD.md#recuperacion-oficial-de-la-aplicacion). No confundir con NAND.
- **Sistema sin arranque o tarjeta dañada:** prepara otra microSD con imagen aprobada, conserva la anterior y restaura los ajustes disponibles. Sólo para un modo de arranque microSD confirmado.
- **Arranque NAND, origen desconocido o fallo de hardware:** solicita asistencia; no hay una recuperación universal por USB garantizada.

Si falla una actualización, conserva mensaje, versión anterior, Buildroot y nombre del paquete. No encadenes reinstalaciones ni interrumpas una escritura en curso.

## Problemas frecuentes

| Incidencia | Comprobaciones |
| --- | --- |
| USB no detectado | Pendrive conocido, puerto y modo USB adecuados; evita hubs sin validar |
| Sin aviso USB | Nombre exacto y extensiones, raíz del USB, conexión tras arrancar y fecha ya procesada |
| Sin Wi-Fi | Modo interno, SSID/clave, cobertura y salida a Internet de la pantalla |
| Sin nuevas versiones | Distribución INDART3D, Release estable superior y asset; reconecta o reinicia aplicación |
| Aviso Buildroot | El paquete no actualiza el sistema completo; revisa compatibilidad |
| Aplicación sin arranque | Distingue aplicación/sistema y microSD/NAND; sigue recuperación compatible |
| Ajustes perdidos al reinstalar SD | Restaura JSON antes del primer arranque o reconfigura manualmente |
| Miniatura recortada tras primera apertura | Incidencia conocida: salir y entrar en carpeta la restablece según la prueba del propietario. [Pendiente](../PENDIENTES.md), sin corrección en esta revisión |
