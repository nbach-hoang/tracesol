# TraceSol methods and boundaries

## Purpose

Assist a human reviewing reported aqueous-solubility records. The central question is whether different-looking values are unit equivalents, possible disagreements, or observations that should remain separate because of their recorded context.

This is a deterministic screening prototype. Its flags have not been evaluated against a reviewed real-paper gold standard. No accuracy, sensitivity, specificity, or researcher-time-saved claim is made.

## Normalization

`S` is stored in mol/L. `log_s` is the base-10 logarithm of the numerical value of S in mol/L, equivalently `log10(S / (1 mol/L))`.

| Input | Conversion to mol/L |
|---|---|
| mol/L or M | value |
| mmol/L or mM | value × 10^-3 |
| umol/L, uM, µM, or μM | value × 10^-6 |
| nmol/L or nM | value × 10^-9 |
| g/L or mg/mL | value / molecular weight |
| mg/L or ug/mL | value × 10^-3 / molecular weight |
| ug/L | value × 10^-6 / molecular weight |
| logS or log10(mol/L) | 10^value |

Micro signs are normalized to `u`. Units remain case-sensitive. Molecular weight is in g/mol and must be supplied for mass-based conversions. When supplied for another unit, it must still be positive and finite. Zero, negative, non-finite, underflowed, and overflowed concentrations fail conversion. Negative logS is valid.

No density assumption is used. ppm, mass fractions, volume fractions, molality, percentages, and unqualified mass units are unsupported. No aqueous-solubility classification is inferred from an arbitrary concentration.

## Context screening

Each same-compound-label pair with valid conversions is considered. A possible-disagreement comparison additionally requires all of the following to be present and valid on both records:

1. Compound label or user-supplied identity identifier.
2. Chemical form.
3. Solvent/composition description.
4. pH.
5. Temperature in degrees Celsius.
6. Measurement method.
7. Measurement kind: equilibrium, intrinsic, apparent, or kinetic.

Text is trimmed, case-folded, and runs of whitespace are normalized. Numbers are compared exactly after parsing, so `7` and `7.0` match. There are no pH/temperature tolerance bins, no molecular-structure canonicalization, and no synonym, salt, hydrate, or stereochemistry resolution. Different compound labels are not paired. User labels must be precise.

Missing or invalid conditions yield **insufficient context**, including when both records omit the same field. Valid different conditions yield **different conditions**. Otherwise an absolute logS difference above the selected threshold yields **disagreement**; values equal to the threshold are not flagged. Default threshold 0.5 log units is a configurable product heuristic, not a universal scientific acceptance standard. Floating-point equality uses a 10^-12 absolute tolerance at the boundary.

Even identical recorded fields do not establish comparable experiments. Purity, polymorphism, crystal state, pressure, ionic strength, buffers, equilibration time, analytical protocol, and other omitted variables may matter. This prototype flags a reason to inspect sources, not a reproducibility failure.

## Repeated evidence

If normalized concentration, complete comparison conditions, non-empty source reference, and excerpt match, the later row receives a possible-duplicate flag. Distinct record identifiers are retained. This is neither DOI deduplication nor proof that two publications report the same experiment.

## Provenance

Inputs, quotations, and source locators are user-supplied. The program does not visit URLs, verify citations, perform OCR, parse a paper, or check that the excerpt numerically supports the entered value. The inspector labels this boundary explicitly.

Raw cell values are retained after import trimming. This is not byte-for-byte preservation of the original CSV file. Extra columns are retained in audit/workspace JSON. SHA-256 hashes are computed over the parsed working input as sorted-key JSON, not over the original file bytes. The fingerprint is for dataset identification, not authorship or authenticity.

## Human review and edits

States: pending, retain evidence, exclude from working set, or follow up. Non-pending states require a reason. No state makes a measurement verified or model-ready. All records remain in reports, regardless of decision. Flags and comparisons continue to include excluded records so a reviewer can inspect the full evidence history.

Edits preserve before/after records in workspace history and reset the edited row's decision. Other decisions persist; a human should revisit related decisions when comparisons change. The audit JSON represents the current working input. Use a workspace export to retain edit history.

## Privacy and security

The application binds to 127.0.0.1. It serves only explicitly allowed frontend assets. It performs no remote inference or analytics, and does not log submitted evidence. Host validation and cross-origin checks limit browser access from other sites. These are prototype safeguards, not a third-party security certification. The server is for local use and should not be exposed directly to the public internet.

HTML content is escaped. Formula-like text fields in CSV exports are prefixed with an apostrophe; numeric normalized columns remain numeric. This may alter how raw text appears in spreadsheet imports, while audit JSON preserves the raw field content.

## Scientific references

- [IUPAC Gold Book: solubility](https://goldbook.iupac.org/terms/view/S05740). DOI: 10.1351/goldbook.S05740.
- [IUPAC Gold Book: amount concentration](https://goldbook.iupac.org/terms/view/A00295). DOI: 10.1351/goldbook.A00295.
- [Llompart et al., Will we ever be able to accurately predict solubility?, Scientific Data 11, 303 (2024)](https://doi.org/10.1038/s41597-024-03105-6). Background on curated solubility data and prediction limitations; no values are imported from this paper.
