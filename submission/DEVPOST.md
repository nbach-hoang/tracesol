# Copy-ready Devpost fields

Review personal details before publishing. Do not claim that this local package has already been hosted or submitted.

## Project name

TraceSol

## Elevator pitch

Turn scattered solubility records into traceable evidence: normalize units, compare experimental context, inspect disagreements, and export a review you can reproduce.

## Team

Ngoc Bach Hoang - confirm preferred public name and Devpost account membership.

## Inspiration

In chemistry, two different numbers are not necessarily contradictory. One might be reported in mg/L and another in micromolar. A higher value might come from a different pH, solvent, temperature, or chemical form. Missing context makes comparison harder still.

My interests in Chemistry and Biological Chemistry, scientific data verification, and flavonoid-solubility research led to a practical question: before putting measurements into a dataset, how can we make their units, context, and sources easier to inspect together?

TraceSol is a small workbench built around that review task.

## What it does

TraceSol imports a CSV of reported solubility records and preserves the original fields. It converts supported concentrations to mol/L and log S, with a visible calculation for each record. Mass-based units require a supplied molecular weight; missing values are not guessed.

The workbench compares same-compound records only when the required recorded conditions are complete. Different pH values, chemical forms, solvents, temperatures, methods, or measurement kinds remain separate. Under matching recorded conditions, a configurable difference threshold highlights pairs worth investigating. It never decides that a particular source is right.

Each record has a source excerpt and locator, a review inspector, and a place to record a human decision with a reason. Users can correct a working record, recheck the comparisons, save and reopen a workspace, or export a reviewed CSV, full JSON audit, or printable offline report.

The application runs locally without accounts, API keys, paid services, or runtime cloud calls. It is designed for chemistry students and researchers reviewing small evidence collections before further analysis.

## How we built it

The backend uses Python's standard library for CSV parsing, finite-number checks, unit conversion, pairwise context screening, hashing, exports, and a local HTTP server. The frontend uses HTML, CSS, JavaScript, and SVG, with an evidence table, source inspector, comparison view, review log, and methods page.

All application code, interface assets, synthetic examples, tests, and documentation were created during November 2026 for LaunchPad Hacks. An AI coding assistant generated the implementation and materials; this assistance is disclosed in the project credits. The runtime itself uses explicit deterministic rules rather than an AI model.

The earlier Carbon Decision Engine prototype was reviewed as a reference for scope and usability. No code, data, or visual assets were copied from it. Chemistry and evidence-verification research interests informed the problem; this project does not include private MERLIN or ai-pharma data or code.

## Challenges

The central challenge was making comparisons conservative enough to be useful. Treating two missing pH values as a match would make the interface appear more decisive while making its conclusion less defensible. TraceSol therefore separates missing context, different context, and disagreements under matching recorded conditions.

Other implementation challenges included preserving original values during editing, distinguishing human decisions from automated flags, handling malformed CSV inputs, and producing exports that remain understandable outside the app.

## Accomplishments

The completed local prototype supports the full import-review-export workflow, requires reasons for review decisions, preserves edit history in workspace exports, and documents every conversion and screening rule.

Automated calculation/server checks and browser workflow checks were run, including equivalent-unit cases, threshold boundaries, missing conditions, invalid concentrations, workspace restoration, exports, and uploaded markup rendered safely as text. Exact counts and recorded results are in the included validation report.

## What we learned

The implementation reinforced a useful distinction: making data numerically comparable does not make the underlying experiments scientifically equivalent. A trustworthy interface should keep that boundary visible, preserve missing information, and make it easy for a reviewer to explain a decision.

## What's next

Next steps are independent researcher usability feedback, a permission-cleared real-paper evaluation set, richer metadata such as equilibration and solid state, and carefully evaluated structure-identity support. Any automated extraction should retain source locations and be tested before it is allowed to influence review decisions.

## Limitations

All built-in examples and source excerpts are synthetic teaching data, not published measurements. No source-verification accuracy, prediction accuracy, time savings, or real-paper validation is claimed. TraceSol does not read PDFs, verify quotations or citations, resolve chemical structures, infer missing conditions, predict solubility, or declare records model-ready. Matching recorded fields does not establish full experimental equivalence.

## Built with

Python, Python standard library, HTML5, CSS3, JavaScript, SVG. AI-assisted development. Playwright and Microsoft Edge were used for development verification only.

## Links to add in the Devpost form

- **Try it out (downloadable local build):** https://github.com/nbach-hoang/tracesol/archive/refs/heads/main.zip
- **Source code:** https://github.com/nbach-hoang/tracesol
- The app runs locally after extraction with Python 3.10+. These links provide the build and source; no hosted web application is claimed.
- **Images:** upload the cover and screenshots in `submission/screenshots/`.
- **Video:** leave blank; the public event requirements make it optional.
- Keep all judging links accessible through 25 November, 5 pm EST / 26 November, 6 am Singapore time.
