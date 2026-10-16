# Incidencias y validaciones pendientes

## THUMB-001 — Miniatura recortada tras la primera apertura

- **Estado:** pendiente de investigación.
- **Prioridad:** baja.
- **Ámbito:** trabajos de impresión y macros `.g` con miniaturas 64×64 y 300×300.
- **Descripción:** en la primera carga, parte de la imagen ampliada aparece en el listado al cancelar.
- **Reproducción:** entrar inicialmente en carpeta; ver icono pequeño correcto; abrir archivo; esperar imagen grande; cancelar; observar listado; salir/entrar de nuevo; repetir apertura/cancelación.
- **Observado por el propietario:** a veces la primera cancelación muestra recorte de la imagen grande; salir y entrar recupera el icono pequeño. Después no se repite al abrir/cerrar reiteradamente.
- **Posibles componentes, sin diagnóstico:** caché de imágenes, primera descarga, invalidación o actualización visual LVGL.
- **Instrucción:** NO corregir ahora. No cambiar caché, descarga, escalado ni eventos gráficos para resolverlo. Requiere autorización expresa posterior.

## Preparación de v1.0.0.1

- PNG original INDART3D recibido; SHA256 registrado; incorporación byte por byte comprobada.
- Compilar ARM T113 y validar los instaladores reales USB y SD.
- Probar ambos en pantalla, logotipo horizontal y conservación/restauración de ajustes.
- Verificar macros: lista, mosaico, confirmación, subcarpetas, espacios, sin imagen y ejecución; verificar thumbnails de trabajos.
- Probar Wi-Fi con una siguiente revisión autorizada. No publicar v1.0.0.2 hasta solicitud expresa.
- Validar compatibilidad binaria v0.4.2 en hardware antes de autorizar equipos de clientes.
