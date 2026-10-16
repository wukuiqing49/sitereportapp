---
contentId: export-and-upload
locale: de-DE
status: machine-draft
title: 'Export und Zustellung: Praxisleitfaden für SiteReport'
description: Dateien exportieren und an einen konfigurierten Server senden.
slug: export-und-zustellung
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_upload/src/main/java/com/wkq/iptc/upload/UploadProtocolType.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/ReportPackageGateway.kt
primaryKeyword: 'Export und Zustellung: Praxisleitfaden für SiteReport'
relatedPages:
- /
- /support.html
template: standard-article
---

# Export und Zustellung: Praxisleitfaden für SiteReport

Fertige Berichte müssen oft geteilt oder an den Projektspeicher gesendet werden.

## Möglichkeiten

- PDF, Bilder und ZIP exportieren
- Dateien vom Gerät teilen
- Über konfigurierte Protokolle senden

## Vorgehensweise

- Bericht erzeugen und Dateien wählen
- Teilen oder Zustellen auswählen
- Status prüfen oder Paket teilen

## Zu prüfende Optionen

- Format, Signaturen, Protokoll, Server und Pfad

## Einschränkungen

- Die Zustellung benötigt ein konfiguriertes Ziel und Netzwerkzugriff.

## Das Ziel vor der Übertragung bestätigen

Prüfen Sie den lokalen Bericht und wählen Sie PDF, Bilder oder ZIP aus den verfügbaren Formaten. Klären Sie für eine Serverübertragung Protokoll, Adresse, Konto und Zielpfad mit der Administration. FTP, FTPS, SFTP, WebDAV und SMB/NAS sind nicht austauschbar. Ein lesbarer Ordner erlaubt nicht automatisch Schreibzugriffe. Testen Sie unbekannte Ziele mit einer Datei ohne Kundendaten.

## Empfang prüfen und Fehler eingrenzen

Prüfen Sie nach der Übertragung den Status und öffnen Sie die Datei am Ziel. Die Übergabe an eine andere App bestätigt keinen Kundenempfang. Prüfen Sie bei Fehlern lokale Datei, Netzwerk und Konfiguration. Suchen Sie vor einem erneuten Versuch nach vorhandenen Kopien; setzen Sie keine automatische Fortsetzung oder Duplikatvermeidung voraus. Geben Sie Fehlermeldungen ohne Passwörter weiter.

