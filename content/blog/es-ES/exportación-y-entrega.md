---
contentId: export-and-upload
locale: es-ES
status: machine-draft
title: Exportar un informe y verificar su entrega al servidor
description: Exporta archivos y envíalos a un servidor configurado.
slug: exportación-y-entrega
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_upload/src/main/java/com/wkq/iptc/upload/UploadProtocolType.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/ReportPackageGateway.kt
primaryKeyword: Exportar un informe y verificar su entrega al servidor
relatedPages:
- /
- /support.html
template: standard-article
---

# Exportar un informe y verificar su entrega al servidor

Los informes terminados suelen necesitar compartirlos o enviarlos al almacenamiento del proyecto.

## Qué puedes hacer

- Exportar PDF, imágenes y ZIP
- Compartir archivos desde el dispositivo
- Enviar mediante protocolos configurados

## Procedimiento

- Genera y elige archivos
- Selecciona compartir o entregar
- Revisa el estado o comparte el paquete

## Opciones que debes revisar

- Formato, firmas, protocolo, servidor y ruta

## Limitaciones

- La entrega necesita un destino configurado y acceso de red.

## Elegir entre compartir y enviar al servidor

Genera y revisa el informe antes de elegir PDF, imágenes o ZIP entre los formatos disponibles. Compartir desde el dispositivo entrega el archivo a otra aplicación instalada. El envío al servidor requiere un destino accesible y un perfil de entrega adecuado.

SiteReport admite configuraciones FTP, FTPS, SFTP, WebDAV y SMB/NAS. Los protocolos no son intercambiables. Pide al administrador el protocolo, la dirección, los permisos de la cuenta y la ruta de destino; no deduzcas la configuración a partir de una página de acceso web.

## Verificar permisos y comprobar la copia recibida

Confirma el servidor y la carpeta con la persona responsable del almacenamiento. Poder ver una carpeta no demuestra que la cuenta pueda escribir en ella. Si necesitas probar el acceso, usa primero un informe sin datos de clientes ni del sitio.

Después del envío, revisa el estado de carga y comprueba que el archivo esperado existe y se abre en el destino. Generarlo localmente no confirma su recepción. Entregarlo a una aplicación para compartir tampoco confirma que el cliente lo haya recibido.

## Qué comprobar si falla la entrega

Primero abre el archivo local. Después revisa la red, el protocolo, la dirección, la cuenta y la ruta remota. Un servidor privado puede exigir acceso a la red de la empresa. Conserva el mensaje de error para soporte sin incluir contraseñas.

Antes de reintentar, comprueba si ya existe una copia en el destino. No supongas que los reintentos reanudan, eliminan duplicados o cambian nombres automáticamente. Conserva la exportación local revisada y acuerda otra vía con el destinatario si no puedes restaurar el acceso.

