# Launch Review Policy

## Required human review

Require explicit review before public use for developer identity, privacy policy, data safety, pricing, subscriptions, legal claims, competitor comparisons, testimonials, performance claims, and every non-source locale.

## Allowed machine-draft content

Machine generation may prepare evidence indexes, page structures, initial metadata, keyword hypotheses, article drafts, screenshot ordering, and static HTML drafts when all product facts are verified.

## Status values

- `draft`: generated but not reviewed
- `machine-draft`: machine-generated localized or public content awaiting review
- `reviewed`: a human reviewer approved the content
- `publishable`: all validation and review gates passed
- `published`: use only after the user explicitly confirms publication

Never change `machine-draft` to `reviewed`, `publishable`, or `published` without explicit human confirmation.
