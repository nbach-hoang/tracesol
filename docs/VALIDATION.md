# Recorded validation

Checked on 8 November 2026. These are implementation checks, not proof of scientific validity or a security certification.

## Calculation and HTTP server suite

**32 tests passed**, using Python 3.12.14 and the standard-library unittest runner. The application is written for Python 3.10+; only the recorded 3.12 environment was exercised here.

Command: `python -m unittest discover -s tests -v`

Detailed output: `output/unittest-results.txt`.

Covered independently known conversion cases, molar-prefix case sensitivity, missing/invalid molecular weight, unsupported units, non-finite/negative/zero inputs, logS overflow/underflow, CSV quotes/BOM/multiline handling, header/shape/size/row errors, condition differences, missing and invalid context, unknown measurement kinds, exact threshold boundaries, threshold sensitivity, source metadata flags, possible duplicates, review-reason requirements, raw data preservation, input fingerprints, spreadsheet-safe CSV export, actual HTTP routes, import/export requests, errors, host/origin restrictions, and public-file allowlisting.

The normal restricted execution environment initially prevented loopback connections. Server checks were then rerun with permission to connect to a temporary local server. An initial Windows connection-abort issue when rejecting a cross-origin POST was corrected by consuming the bounded body before returning the rejection. The recorded final suite passed after that correction.

## Browser workflow

**15 end-to-end checks passed**, using Playwright with installed Microsoft Edge (`msedge`) against the local server. The app was restarted after backend edits before the final browser run.

Structured evidence: `output/browser-qa.json`.

Checks included:

1. Demo metrics: 12 records, 10 normalized, 8 with review flags, 2 invalid inputs, 2 disagreeing pairs.
2. Threshold change and equality-boundary behavior.
3. Search, empty search state, and invalid-input filter.
4. Decisions require reasons and appear in the review log.
5. Workspace export preserves review decisions.
6. Editing a record recalculates comparisons and resets that row's decision; edited synthetic examples retain their synthetic label.
7. Workspace reopening restores the saved dataset and recalculates.
8. JSON audit download.
9. CSV download.
10. Self-contained HTML report download.
11. Actionable malformed-CSV error.
12. User-supplied HTML-like text does not execute or create image elements.
13. No page-level horizontal overflow at 390, 768, 1024, and 1440 pixels.
14. Methods and limitations available in the application.
15. No browser script errors or third-party requests in the exercised workflow.

The test is reproducible with `scripts/browser_qa.cjs`; Node/Playwright are developer tools, not app dependencies. Browser interactions used synthetic teaching data only. The saved example audit/report includes a demonstration follow-up note, not a real source adjudication.

## Visual review

Actual application screenshots were inspected at desktop and mobile sizes. A transient notification was removed from the final mobile capture. The comparison panel was constrained to a scrollable height so repeated pairs do not create an excessively long page.

The 1200 x 630 cover uses an actual screenshot inside an original graphic layout. The two-page project brief was rendered to page images using Poppler and visually inspected; its title, screenshot, tables, text, and footer fit without overlap. The PDF contains two pages and selectable text. Poppler printed display-font warnings, but the rendered embedded-font text was visually intact.

## Scope not established

- No independent human usability study or screen-reader audit.
- No evaluation against real-paper reviewed labels.
- No accuracy, researcher time-saving, or generalization benchmark.
- No production hosting, external service integration, public-link access check, or Devpost submission.
- No verification of participant age, geographic eligibility, or identity.
- No exhaustive browser/device matrix or independent penetration test.

## Release checks

The release is packaged with a per-file SHA-256 manifest and a separate ZIP checksum. The packaging script excludes environments, caches, secrets, temporary QA workspaces, and PDF render intermediates. ZIP integrity and the extracted command-line demo are checked as part of final delivery.
