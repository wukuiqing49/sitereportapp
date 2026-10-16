---
contentId: export-and-upload
locale: fr-FR
status: machine-draft
title: 'Export et livraison : guide pratique de SiteReport'
description: Exportez les fichiers et envoyez-les vers un serveur configuré.
slug: export-et-livraison
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_upload/src/main/java/com/wkq/iptc/upload/UploadProtocolType.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/ReportPackageGateway.kt
primaryKeyword: 'Export et livraison : guide pratique de SiteReport'
relatedPages:
- /
- /support.html
template: standard-article
---

# Export et livraison : guide pratique de SiteReport

Les rapports terminés doivent souvent être partagés ou envoyés au stockage du projet.

## Ce que vous pouvez faire

- Exporter PDF, images et ZIP
- Partager les fichiers depuis l’appareil
- Envoyer via des protocoles configurés

## Procédure

- Générez et choisissez les fichiers
- Sélectionnez partage ou livraison
- Vérifiez l’état ou partagez le paquet

## Options à vérifier

- Format, signatures, protocole, serveur et chemin

## Limites à connaître

- La livraison nécessite une destination configurée et un accès réseau.

## Confirmer la destination avant l’envoi

Relisez le rapport local et choisissez PDF, images ou ZIP parmi les formats disponibles. Pour un serveur, confirmez le protocole, l’adresse, le compte et le chemin avec l’administrateur. FTP, FTPS, SFTP, WebDAV et SMB/NAS ne sont pas interchangeables. Pouvoir consulter un dossier ne garantit pas le droit d’y écrire. Testez une destination non confirmée avec un fichier sans données client.

## Vérifier la réception et isoler un échec

Après l’envoi, consultez son état et ouvrez la copie à destination. Le partage vers une autre application ne confirme pas la réception par le client. En cas d’échec, vérifiez le fichier local, le réseau et la configuration. Avant de réessayer, recherchez une copie existante ; ne supposez ni reprise ni dédoublonnage automatique. Communiquez l’erreur au support sans mot de passe.

