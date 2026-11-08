# TraceSol: no-video judge walkthrough

Estimated hands-on route: about three minutes, excluding Python installation if needed. No recording, narration, camera, or login is needed.

## Open the application

Extract the release ZIP. On Windows, double-click `START_TRACESOL.cmd`; on another platform run `python app.py` from the extracted folder. Python 3.10+ is required, with no packages to install. Open the printed local URL, usually http://127.0.0.1:8765. Keep the server window open while reviewing.

## 1. See through different units

The built-in collection has 12 synthetic records. Select Q-01. Its conversion is:

`0.30224 mg/L × 0.001 / 302.24 g/mol = 0.000001 mol/L`

Q-02 reports 1 uM: the same normalized concentration, log S = -6. The original units and source excerpts remain visible.

## 2. Inspect a possible disagreement

Choose **Compare conditions**. Q-03 is tenfold higher than Q-01 and Q-02 under the same recorded context. There are two flagged pairs, not two proven erroneous records. Change the threshold from 0.5 to 1.0 log units: these exact-boundary pairs are no longer flagged. Change back to 0.5.

## 3. Keep context differences separate

Q-04 has a different pH; Q-06 has a different chemical form. These are separated rather than labeled disagreements. Q-05 lacks pH and is marked as missing context, even if another record also lacks pH.

The comparison is deliberately limited to recorded fields. It does not establish full experimental equivalence.

## 4. Follow a flag to a decision

Return to **Evidence library**. Select Q-03, choose **Follow up with source**, and enter a reason such as: “Check the reported concentration and conditions against the source; keep both values until resolved.” Save. Open **Review decisions** to see the note.

Edit Q-03's working value from 3.0224 to 0.30224. Its decision resets and the disagreement disappears. This is a demonstration of correction/rechecking, not evidence that the original value was wrong. Use **Reset demo** to restore the initial synthetic collection.

## 5. See the failures and exports

Filter to **Invalid inputs**. N-01 is missing the molecular weight required for a mass-unit conversion. R-01 has a negative concentration. Neither is silently converted.

Export a CSV, audit JSON, or readable HTML report. Save an editable workspace and reopen it. The HTML report opens offline; the audit includes a SHA-256 input fingerprint. All original rows remain in exports, including excluded evidence.

## For deeper review

See the in-app **Methods & limits** page, `docs/METHODS.md`, `docs/VALIDATION.md`, and `tests/`. No built-in record is claimed as a real literature measurement. Source excerpts are preserved as supplied and are not independently checked by the program.
