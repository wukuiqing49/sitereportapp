---
contentId: export-and-upload
locale: pt-BR
status: machine-draft
title: 'Exportação e entrega: guia prático do SiteReport'
description: Exporte arquivos e envie-os para um servidor configurado.
slug: exportação-e-entrega
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_upload/src/main/java/com/wkq/iptc/upload/UploadProtocolType.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/ReportPackageGateway.kt
primaryKeyword: 'Exportação e entrega: guia prático do SiteReport'
relatedPages:
- /
- /support.html
template: standard-article
---

# Exportação e entrega: guia prático do SiteReport

Relatórios concluídos geralmente precisam ser compartilhados ou enviados ao armazenamento do projeto.

## O que você pode fazer

- Exportar PDF, imagens e ZIP
- Compartilhar arquivos no dispositivo
- Enviar por protocolos configurados

## Procedimento

- Gere e escolha os arquivos
- Selecione compartilhar ou entregar
- Revise o status ou compartilhe o pacote

## Opções a revisar

- Formato, assinaturas, protocolo, servidor e caminho

## Limitações

- A entrega exige destino configurado e acesso à rede.

## Confirmar o destino antes da entrega

Revise o relatório local e escolha PDF, imagens ou ZIP entre os formatos disponíveis. Para entrega ao servidor, confirme protocolo, endereço, conta e caminho com o administrador. FTP, FTPS, SFTP, WebDAV e SMB/NAS não são intercambiáveis. Ver uma pasta não garante permissão de escrita. Use um arquivo sem dados de clientes para testar um destino ainda não confirmado.

## Verificar o recebimento e investigar falhas

Após o envio, confira o estado da carga e abra a cópia no destino. Compartilhar com outro aplicativo não confirma o recebimento pelo cliente. Se falhar, verifique arquivo local, rede e configuração. Antes de tentar novamente, procure uma cópia existente; não presuma retomada ou eliminação automática de duplicatas. Envie a mensagem de erro ao suporte sem senhas.

