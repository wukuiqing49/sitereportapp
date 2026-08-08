---
contentId: export-and-upload
locale: en-US
status: draft
title: 'Export and server delivery: what it does in SiteReport'
description: Export report packages and send them through supported server protocols
  when configured. Learn the exact problem, options, verified steps, and known limitations.
slug: export-and-upload
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_upload/src/main/java/com/wkq/iptc/upload/UploadProtocolType.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/ReportPackageGateway.kt
primaryKeyword: 'Export and server delivery: what it does in SiteReport'
relatedPages:
- /
- /support.html
template: standard-article
---

# Export and server delivery: what it does in SiteReport

Completed reports often need to be shared with clients or delivered to an existing project storage system.

## What this feature helps you do

- Export PDF, image, and ZIP report packages
- Share generated report files from the device
- Upload through FTP, FTPS, SFTP, WebDAV, or SMB/NAS configurations

## Where it fits in the workflow

- Generate the report and select export files
- Choose share or configured server delivery
- Review the upload state or share the exported package

## What to check before export

- Output format, signatures, upload protocol, server address, and remote path

## What to keep in mind

- Server delivery requires a configured endpoint and suitable network access.

