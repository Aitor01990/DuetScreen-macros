# Manual interno de desarrollo y publicación

[Portada](../README.md) · [Versiones](VERSIONES.md) · [Compatibilidad](COMPATIBILIDAD.md)

Los procedimientos habituales se realizan desde Windows y el navegador. Ubuntu sólo se ejecuta en los servidores de GitHub Actions; no hay que instalarlo en el ordenador del técnico.

## Organización

Repositorio existente: `Aitor01990/DuetScreen-macros`. No se sustituye por otro. La referencia funcional anterior es el commit `9d7d4366e47023fc6c8b54256f13a270be164fb2`, rama `respaldo/macros-validado-2026-10-16`. El desarrollo de esta distribución se realiza en `desarrollo/indart3d-v1.0.0.1`; `main` conserva lo aprobado hasta su integración.

| Ruta | Contenido |
| --- | --- |
| `distribution/config.json` | Única fuente de verdad de versión, bases, destino, repositorio de actualizaciones y logotipo |
| `scripts/apply_macros.py` | Código extraído del workflow funcional, sin alterar su comportamiento |
| `patches/macros-sha256.json` | Los siete hashes exactos del código de miniaturas ya validado |
| `scripts/prepare_source.py` | Genera cabeceras, adapta versión/actualizador y empaquetado; comprueba las bases y los hashes |
| `patches/IndartVersionPolicy.h` | Comparación estricta de cuatro componentes numéricos |
| `patches/github_release_selection.cpp.txt` | Selector C++ estable que se integra en UpgradeHelper |
| `branding/` | PNG original pendiente y condiciones de incorporación |
| `scripts/post_build_indart.sh` | Incluye metadatos y splash en el sistema completo, después del overlay oficial |
| `scripts/verify_artifacts.py` | Comprueba ELF, versión, recursos, permisos USB y contenido real de la partición ext4 de `sdcard.img` |
| `scripts/publish_release.py` | Publica exactamente los archivos comprobados; no reemplaza tags ni Releases |
| `.github/workflows/` | Validación rápida, compilación de pruebas y publicación estable separadas |
| `docs/workflow-validado-9d7d436.yml.txt` | Copia de auditoría del workflow anterior, no ejecutable como workflow |

Las bases son invariables en esta revisión: DuetScreen `8cf206ddd2aad3a55852eb2125a318d94c8601f3`, Buildroot `7b01688559a5602a55d564651db279674a237263`. Se comprueban también submódulos. No actualizar automáticamente upstream.

## Solicitar una modificación a Codex

Indica repositorio, rama, versión base, objetivo concreto y criterios de prueba. Pide conservar los siete archivos funcionales y la incidencia pendiente salvo autorización expresa. Revisa el diff y el informe, compila en rama de desarrollo, descarga artefactos y prueba en una pantalla de laboratorio. Integra sólo el código aprobado. No mezcles la validación de una versión con instaladores regenerados después.

Ejemplo: «Sobre desarrollo/indart3d-v1.0.0.1, cambia únicamente el texto X, conserva macros y caché, prepara la revisión indicada sin publicar hasta validar ambos instaladores».

## Preparar el logotipo

El PNG original INDART3D recibido ya está incorporado. Súbelo como `branding/INDART3D.png`, calcula su SHA256 desde Propiedades/herramienta interna o PowerShell `Get-FileHash` y registra el valor completo en `logo_sha256` de `distribution/config.json`. El PNG recibido debe ser aprobado visualmente; el hash identifica ese recurso y no demuestra por sí mismo su autenticidad.

El proceso conserva el PNG original recibido de 1024×600 exactamente, sin redimensionar ni recodificar. Se instala en `/etc/splash.png` y `/etc/splash/splash_0.png` tanto en USB como en la SD. DisplayHelper copia esta última ruta al seleccionar orientación 0. No se cambia su lógica de orientación ni se desarrolla otra personalización. Comprueba el contraste y el aspecto en pantalla física antes de publicar.

No se introduce una imagen inventada. Sin PNG/hash, la compilación normal falla antes del trabajo ARM. La opción de desarrollo `allow_unbranded` permite ensayar código, pero el manifiesto queda marcado `branded: false` y no puede publicarse con nuestro workflow.

## Compilar desde GitHub

Primera integración: GitHub exige que el workflow manual exista en la rama predeterminada para ofrecer `Run workflow`. Mientras está sólo en desarrollo, la validación rápida sí se dispara con el push. Integra el PR revisado para habilitar la compilación manual desde Actions; la rama de respaldo conserva el sistema anterior. Fuente: [documentación de GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

1. Entra en el repositorio y abre **Actions**.
2. Selecciona **INDART3D - Compilar pruebas ARM T113** (`compilar-duetscreen.yml`).
3. Pulsa **Run workflow** y selecciona la rama aprobada.
4. Activa `full_image` si necesitas también `sdcard.img`. Es obligatorio para publicar una Release completa. Desactivado genera sólo el actualizador, evitando la generación final de imágenes; aun así necesita compilar toolchain y dependencias y puede tardar horas.
5. Deja `allow_unbranded` desactivado para candidatos oficiales. Sólo actívalo para pruebas sin el logo original; esos archivos no son publicables.
6. Pulsa **Run workflow** y abre la ejecución. Amarillo significa en curso, verde que terminaron las validaciones, rojo que hay un fallo. Un verde no acredita pruebas físicas.
7. En el resumen, sección **Artifacts**, descarga `INDART3D-instaladores`. Extrae **solamente el ZIP de Actions** en Windows.
8. Dentro encontrarás `DuetScreen.tar.gz`, y `sdcard.img` si lo solicitaste, además de `SHA256SUMS.txt` y `build-manifest.json`. No descomprimas el `.tar.gz` para instalar por USB.
9. Descarga `INDART3D-informe` para parches, arquitectura, permisos, submódulos y configuración; `INDART3D-logs` contiene registros. Registra el ID numérico de ejecución que figura en la URL `/actions/runs/ID`.
10. Comprueba versión y commit del manifiesto, checksums y pruebas físicas. Conserva localmente los archivos exactos ensayados.

La generación completa inspecciona la partición ext4 de la SD con `debugfs`, sin montar ni escribir en dispositivos. Compara su binario con el USB, metadatos, Buildroot y splash. Si algo difiere, no se suben instaladores como resultado validado.

## Publicar una version

### Procedimiento automático recomendado

1. Edita **sólo** `version` en `distribution/config.json` para establecer la revisión aprobada. No edites a mano `version.h`, tags de upstream ni YAML para cambiar la versión.
2. Actualiza el historial, revisa e integra el código aprobado. No publiques v1.0.0.2 sin petición expresa del propietario.
3. Ejecuta la compilación con `full_image: true` y `allow_unbranded: false`.
4. Descarga y prueba **esos mismos** USB y SD. Comprueba la versión visible, logo, macros, conexión y restauración. Guarda resultados y checksums.
5. Sin modificar la rama desde esa compilación, abre **Actions → INDART3D - Publicar versión estable validada** (`publicar.yml`).
6. Selecciona la misma rama/commit, introduce `build_run_id`, la versión exacta en `expected_version` y marca `hardware_confirmed` únicamente tras las pruebas.
7. Ejecuta. El workflow exige una compilación verde del workflow esperado, mismo commit, branding y SD verificados, dos hashes correctos y confirmación física. No compila otra vez.
8. Crea un tag nuevo apuntando al commit aprobado y una Release borrador, adjunta ambos instaladores, checksums y manifiesto, y sólo entonces la hace estable/pública. Si falla la subida, queda borrador y no aparece en el canal estable.
9. Verifica en **Releases** versión, assets y notas. Descarga de nuevo y compara los hashes con los que probaste. Conserva una copia interna permanente.

Si el tag o la Release ya existen, aborta incluso si están en borrador. No se usa `--clobber`. Revisa manualmente el borrador incompleto; no reutilices un número publicado para binarios distintos. El `GITHUB_TOKEN` sólo tiene escritura de contenido en el trabajo de publicación; las compilaciones son de lectura. No se incorporan tokens al firmware.

### Alternativa manual desde el navegador

1. Cambia la versión en `distribution/config.json`, aprueba el código, compila ambas imágenes y pruébalas según el procedimiento anterior.
2. Abre `build-manifest.json`: la versión debe coincidir con la deseada, `source_commit` con el commit aprobado, `branded` y `sd_verified` deben ser `true`. Revisa ambos SHA256. La comprobación de binario de Actions exige la cadena exacta de versión, no un prefijo parecido.
3. En GitHub abre **Releases → Draft a new release**.
4. En **Choose a tag**, escribe la misma versión, por ejemplo `v1.0.0.2`, y elige crear el tag. En **Target**, selecciona el commit aprobado o su rama sólo si sigue apuntando a ese commit. No uses el último `main` sin comprobar su SHA. No reutilices otro tag.
5. Título: `DuetScreen v1.0.0.2 — INDART3D`. Redacta cambios concretos, bases oficiales, compatibilidad RRF, pruebas realizadas, incidencias pendientes y SHA256.
6. Adjunta exactamente `DuetScreen.tar.gz`, `sdcard.img`, `SHA256SUMS.txt` y `build-manifest.json` de la misma ejecución. No adjuntes el ZIP de Actions como actualizador ni renombres el `.tar.gz`.
7. Guarda primero como borrador y revisa todo. Publica estable sólo con pruebas concluidas; no marques **This is a pre-release** para el canal estable.
8. Pulsa **Publish release**, comprueba que los dos instaladores son descargables y vuelve a verificar sus hashes.

La alternativa manual depende de la revisión humana y no puede impedir que un administrador suba un archivo equivocado. Sigue los controles anteriores; no afirmes una validación automática de una subida manual que no hayas comprobado. [Referencia GitHub](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

### Publicar la siguiente actualización Wi-Fi

Ejemplo futuro, **no ejecutar ni publicar todavía**: cambiar `version` a `v1.0.0.2`, incorporar una modificación visible pequeña solicitada, compilar USB+SD, probar y publicar con uno de los procedimientos anteriores. Una pantalla v1.0.0.1 buscará en `/repos/Aitor01990/DuetScreen-macros/releases`, ignorará borradores/preliminares y elegirá la versión numérica mayor que disponga de `DuetScreen.tar.gz`. Reconecta o reinicia la aplicación para provocar la comprobación y acepta el aviso. Registra el resultado físico; no se presume probado ahora.

Para trasladar al GitHub corporativo, cambia únicamente `update_repository` en la configuración, comprueba permisos/acceso público del repositorio nuevo y recompila. Las pantallas antiguas seguirán consultando el anterior hasta instalar una versión de transición que apunte al nuevo. No basta con mover el repositorio de los desarrolladores.

## Actions Artifacts y Releases

Artifacts son resultados temporales de compilación: instaladores e informes **14 días**, logs **7 días**. Al caducar no sirven como archivo histórico. Si necesitas publicar después de caducar, recompila y repite las pruebas de los archivos nuevos.

Releases son publicaciones persistentes mientras no se eliminen del repositorio; no dependen de la caducidad de Actions. Para versiones antiguas abre **Releases**, elige el tag y descarga sus Assets. Mantén además una copia interna por versión con los dos instaladores, hashes, manifiesto y resultados físicos. Los tags y commits conservan fuentes/parches; descarga su ZIP para revisión, no para instalarlo en pantalla.

## Imagen completa

Activa `full_image` en el mismo workflow. `sdcard.img` se genera desde Buildroot v0.4.4 con nuestra aplicación ya instalada y con el hook posterior al overlay oficial; no es la imagen oficial sin personalización. La validación comprueba el contenido de la partición real, no sólo el directorio `output/target`.

Para publicar por el workflow estable actual se exigen ambos archivos coherentes. No es necesario regenerar todas las imágenes antiguas; conserva al menos la última imagen aprobada para instalación/recuperación y las Releases anteriores. El resultado técnico NAND no forma parte de la entrega normal.

## Deshacer cambios

Para volver al código funcional anterior, selecciona la rama de respaldo o abre el commit `9d7d436...` y crea desde él una nueva rama; no borres el historial ni hagas un push forzado sobre versiones publicadas. El workflow anterior está disponible en ese commit y en la copia de auditoría. Puedes restaurarlo en una nueva rama y compilar antes de integrar.

Si una modificación rompe la compilación, usa un PR de reversión o restaura únicamente el archivo afectado desde el commit anterior. Un cambio de código no cambia el firmware ya instalado. Para revertir la aplicación física usa un paquete USB anterior compatible; para recuperar el sistema microSD, la imagen correspondiente. No muevas un tag publicado ni reemplaces sus binarios por otros bajo la misma versión.

Una Release borrada sólo puede restaurarse fielmente con los archivos originales y sus hashes. Si no están, no regeneres binarios distintos atribuyéndoles silenciosamente la misma versión: registra la incidencia y publica una revisión nueva.

## Diagnosticar una compilación fallida

Abre **Actions → ejecución roja → primer paso fallido**. Descarga `INDART3D-logs` antes de siete días. No busques el último mensaje genérico de error: localiza el primer error del compilador o de la validación.

| Fallo | Acción |
| --- | --- |
| Logo ausente/hash incorrecto | Incorporar PNG original y hash aprobado; no desactivar el control para una Release |
| Base o hash thumbnail incorrecto | Revisar commit y modificación; no actualizar hashes para ocultar diferencias |
| Espacio insuficiente/timeout | Revisar uso de disco y logs; la compilación puede durar horas; límite seis horas |
| Descarga upstream fallida | Reintentar cuando el servicio esté disponible; mantener commits fijados |
| Error C++ | Revisar el primer archivo/línea; ejecutar validación rápida antes de otro build completo |
| Fallo de versión/ELF/recursos/permisos | Revisar preparación, empaquetado y manifiesto; no subir instaladores manualmente como si fueran válidos |
| SD distinta del USB | Revisar hook post-build y orden del overlay; no publicar sólo el USB como Release completa |
| Publicación rechazada | Comprobar mismo SHA, ejecución correcta, artefactos vigentes y tag no existente |

No se requieren Linux local, tokens privados en dispositivos ni comandos para el procedimiento habitual.
