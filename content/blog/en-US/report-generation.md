---
contentId: report-generation
locale: en-US
status: draft
title: Review an inspection PDF before sending it to a client
description: Generate structured field reports from project information, checklist
  results, photos, notes, and signatures. Learn the exact problem, options, verified
  steps, and known limitations.
slug: report-generation
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_pdf/src/main/java/com/wkq/nativepdf/NativeReportPdfRenderer.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/NativeSiteReportPdfGateway.kt
primaryKeyword: Review an inspection PDF before sending it to a client
relatedPages:
- /
- /support.html
template: tutorial
---

# Review an inspection PDF before sending it to a client

Turning field observations into a consistent report can take significant manual formatting work.

## What this feature helps you do

- Generate a PDF field report
- Include checklist results, photos, location records, notes, and signatures
- Preview and reopen generated report files

## Where it fits in the workflow

- Complete the inspection record
- Choose report and PDF presentation options
- Generate the report and review the exported files

## What to check before export

- Report template, PDF style, export format, and signature inclusion

## What to keep in mind

- Some report styles and templates may depend on the app edition or selected access plan.

## Check the source record and then the exported PDF

Review the project identity, inspection results, photos, notes, and sign-off data before generating the file. Choose the template, PDF style, and signature inclusion for the intended recipient. Some styles depend on the edition or access plan, so check the options actually available in your installed app.

Open the generated PDF and check the project name, readability of photos, findings, and signature presentation. If something is missing, check the source record and template options before generating a replacement. Open the replacement too, and make sure you select that file when sharing. Creating a PDF and delivering it to the recipient are separate checks.

