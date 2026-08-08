# Google Play Listing Contract

## Default field limits

Use these as working limits and verify against current Google Play Console requirements before publication:

| Field | Working maximum |
| --- | ---: |
| App title | 30 characters |
| Short description | 80 characters |
| Full description | 4,000 characters |

Count Unicode code points, including spaces and punctuation. Target natural copy below the maximum instead of filling every field.

## Evidence rules

- Every product capability maps to a verified feature evidence path.
- Every screenshot caption matches visible UI and the available locale.
- Release notes map to a changelog, commit range, issue list, or explicit user input.
- Pricing, trials, subscriptions, regions, compatibility, and offline availability require explicit evidence.

## Screenshot sequence

Start with the clearest primary outcome, then show the core workflow, differentiators, and trust or control features. Use a source screenshot only if it represents the current app and target locale. A caption must add context without covering essential UI or claiming invisible behavior.

## Experiments

Change one element per experiment. Define the audience, hypothesis, baseline, primary metric, guardrail, minimum runtime or sample decision, and stop condition. Do not invent expected lift.

## Final checks

- Fields fit current locale limits.
- No unsupported claims, testimonials, rankings, or promotional metadata.
- No competitor marks or misleading platform affiliation.
- Feature availability and monetization qualifiers are visible.
- Machine-generated translations are labeled for review.
- Every referenced image exists and matches its listing locale.
