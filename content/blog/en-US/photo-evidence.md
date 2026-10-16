---
contentId: photo-evidence
locale: en-US
status: draft
title: Capture inspection photos that keep their site context
description: Capture photos for inspection items and associate them with notes, time,
  and location information. Learn the exact problem, options, verified steps, and
  known limitations.
slug: photo-evidence
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_camera/src/main/res/values/strings.xml
- feature/feature_app/src/main/java/com/wkq/feature/app/photo/PhotoEvidenceWriter.kt
primaryKeyword: Capture inspection photos that keep their site context
relatedPages:
- /
- /support.html
template: standard-article
---

# Capture inspection photos that keep their site context

A photo without its inspection context is difficult to use as evidence later.

## What this feature helps you do

- Capture one or more photos for an inspection item
- Associate photos with checklist records
- Record location and capture time when available

## Where it fits in the workflow

- Open an inspection item
- Capture or select the evidence photo
- Review the photo and continue the inspection

## What to check before export

- Photo source, inspection item, and visible evidence annotations

## What to keep in mind

- Location details depend on device location availability and permission.

## Make a photo useful to someone who was not there

Open the relevant inspection point before adding a photo so that the image is linked to the correct record. For a defect, consider taking an overview that identifies the area and a close view that shows the observation. Check focus and legibility while you are still on site; a detailed note cannot recover an unreadable image.

Add the location within the site and the observed condition to your notes. Device location is supporting context, not a substitute for identifying the room or inspection point. If location data is absent, check device availability and permissions; do not assume a gallery image will provide complete location information. Review the evidence again in the generated report.

