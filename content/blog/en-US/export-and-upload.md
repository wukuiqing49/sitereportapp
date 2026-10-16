---
contentId: export-and-upload
locale: en-US
status: draft
title: Export an inspection report and verify server delivery
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
primaryKeyword: Export an inspection report and verify server delivery
relatedPages:
- /
- /support.html
template: standard-article
---

# Export an inspection report and verify server delivery

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

## Choose a file handoff or a server destination

Generate and review the report first. Decide whether the recipient needs a PDF, image files, or a ZIP package, using the export formats available in the app. Device sharing is suitable when you want to pass the file to another installed app. Configured server delivery needs a reachable destination and a matching delivery profile.

SiteReport supports configured FTP, FTPS, SFTP, WebDAV, and SMB/NAS delivery. These protocols are not interchangeable. Ask the server administrator for the supported protocol, server address, account permissions, and destination path rather than guessing from a web login address.

## Check the destination before uploading real reports

Confirm the server and remote path with the person responsible for project storage. The account must be allowed to write to that destination; being able to browse a folder does not establish upload permission. If you need to test access, use a report without client or site details until the destination is confirmed.

After delivery, review the upload state and check the destination for the expected file. Open that copy and verify its contents. Generating a report locally does not confirm that it reached the server, and handing a file to a sharing app does not confirm receipt by the client.

## If delivery fails, isolate the failing step

First confirm that the generated file opens locally. Then check network access, the selected protocol, server address, account, and remote path. A private company server may require access to the company network. Keep the failure message for support, but do not include passwords or other credentials.

Before retrying, check whether a file already exists at the destination. Do not assume failed or repeated attempts are automatically resumed, deduplicated, or renamed. When server access cannot be restored immediately, keep the reviewed local export and agree on an alternative delivery method with the recipient.

