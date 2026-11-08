"""Deterministic review rules. No predictions, database lookups, or AI calls."""
import csv
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from itertools import combinations

VERSION = "1.0.0"
MAX_ROWS = 500
FIELDS = ["record_id", "compound", "form", "value", "unit", "mw_g_mol", "solvent", "ph", "temperature_c", "method", "measurement_kind", "source", "evidence", "source_locator"]
CONDITIONS = ["compound", "form", "solvent", "ph", "temperature_c", "method", "measurement_kind"]
REQUIRED = ["record_id", "compound", "value", "unit"]
STATES = {"pending", "retain", "exclude", "follow_up"}


class InputError(ValueError):
    pass


def parse_csv(text):
    if not isinstance(text, str) or not text.strip():
        raise InputError("Choose a CSV file or paste a non-empty CSV table.")
    if len(text.encode("utf-8")) > 2_000_000:
        raise InputError("CSV exceeds the 2 MB limit.")
    try:
        reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
        if not reader.fieldnames:
            raise InputError("CSV needs a header row.")
        headers = [h.strip() for h in reader.fieldnames]
        if len(set(headers)) != len(headers):
            raise InputError("CSV has duplicate column names.")
        missing = set(REQUIRED) - set(headers)
        if missing:
            raise InputError("Missing required columns: " + ", ".join(sorted(missing)))
        reader.fieldnames = headers
        rows = []
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise InputError(f"Row {reader.line_num} has a different number of cells from the header.")
            if not any(str(v).strip() for v in row.values()):
                continue
            rows.append({k: str(v).strip() for k, v in row.items()})
            if len(rows) > MAX_ROWS:
                raise InputError(f"Please use at most {MAX_ROWS} records per review.")
    except csv.Error as exc:
        raise InputError("Malformed CSV: " + str(exc)) from exc
    if not rows:
        raise InputError("The CSV has a header but no records.")
    return rows


def finite(value, name):
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise InputError(f"{name} must be a number.") from exc
    if not math.isfinite(result):
        raise InputError(f"{name} must be finite (not NaN or infinity).")
    return result


def normalize(value, unit, mw=""):
    value = finite(value, "Value")
    unit = str(unit).strip().replace("μ", "u").replace("µ", "u").replace(" ", "")
    mass = {"g/L": 1, "mg/L": 1e-3, "ug/L": 1e-6, "mg/mL": 1, "ug/mL": 1e-3}
    molar = {"mol/L": 1, "M": 1, "mmol/L": 1e-3, "mM": 1e-3, "umol/L": 1e-6, "uM": 1e-6, "nmol/L": 1e-9, "nM": 1e-9}
    weight = None
    if str(mw).strip():
        weight = finite(mw, "Molecular weight")
        if weight <= 0:
            raise InputError("Molecular weight must be positive.")
    if unit in {"logS", "log10(mol/L)"}:
        try:
            concentration = 10.0 ** value
        except OverflowError as exc:
            raise InputError("logS is outside the supported numerical range.") from exc
        explanation = f"10^({value:g}) mol/L"
    elif unit in mass:
        if weight is None:
            raise InputError("Mass concentration needs molecular weight in g/mol.")
        concentration = value * mass[unit] / weight
        explanation = f"{value:g} {unit} × {mass[unit]:g} g/L per {unit} ÷ {weight:g} g/mol"
    elif unit in molar:
        concentration = value * molar[unit]
        explanation = f"{value:g} {unit} × {molar[unit]:g} mol/L per {unit}"
    else:
        raise InputError(f"Unsupported unit '{unit}'. Use an explicit molar or mass-per-volume unit; ppm and molality are not inferred.")
    if not math.isfinite(concentration) or concentration <= 0:
        raise InputError("Concentration must be positive and within the supported numerical range.")
    return {"mol_l": concentration, "log_s": math.log10(concentration), "calculation": explanation, "normalized_unit": "mol/L"}


def _canonical(value):
    return " ".join(str(value).strip().casefold().split())


def analyze(rows, threshold=0.5, reviews=None):
    threshold = finite(threshold, "Disagreement threshold")
    if not 0 < threshold <= 10:
        raise InputError("Disagreement threshold must be greater than 0 and at most 10 log units.")
    if not isinstance(rows, list) or not rows or len(rows) > MAX_ROWS:
        raise InputError(f"Provide between 1 and {MAX_ROWS} records.")
    if any(not isinstance(r, dict) for r in rows):
        raise InputError("Every record must be an object with named fields.")
    reviews = reviews if isinstance(reviews, dict) else {}
    fingerprint = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    result = []
    ids = set()
    for index, original in enumerate(rows):
        raw = {str(k): str(v).strip() if v is not None else "" for k, v in original.items()}
        row = {k: raw.get(k, "") for k in FIELDS}
        key = f"row-{index + 1}"
        flags = []

        def flag(code, message, severity="review"):
            flags.append({"code": code, "message": message, "severity": severity})

        for field in REQUIRED:
            if not row[field]:
                flag("missing_" + field, field.replace("_", " ").capitalize() + " is missing.", "error")
        if row["record_id"] in ids:
            flag("duplicate_id", "Record ID is repeated. Row keys keep the evidence separate.", "error")
        ids.add(row["record_id"])
        converted = None
        try:
            converted = normalize(row["value"], row["unit"], row["mw_g_mol"])
        except InputError as exc:
            flag("conversion_error", str(exc), "error")
        condition_values = {}
        for field in CONDITIONS:
            value = row[field]
            if not value:
                flag("missing_" + field, field.replace("_", " ").capitalize() + " is unreported; do not assume a matching condition.")
                condition_values[field] = None
                continue
            if field in {"ph", "temperature_c"}:
                try:
                    number = finite(value, field)
                    if field == "temperature_c" and number <= -273.15:
                        raise InputError("Temperature must be above absolute zero.")
                    if field == "ph" and not -2 <= number <= 16:
                        raise InputError("pH is outside this prototype's supported range (-2 to 16).")
                    condition_values[field] = number
                except InputError as exc:
                    flag("invalid_" + field, str(exc), "error")
                    condition_values[field] = None
            else:
                condition_values[field] = _canonical(value)
        for field in ["source", "evidence", "source_locator"]:
            if not row[field]:
                flag("missing_" + field, {"source": "No source reference recorded.", "evidence": "No source excerpt recorded. The reported value has not been checked against an excerpt.", "source_locator": "Add a page, table, or section so another reader can find the evidence."}[field])
        if row["measurement_kind"] and _canonical(row["measurement_kind"]) not in {"equilibrium", "intrinsic", "apparent", "kinetic"}:
            flag("unknown_kind", "Measurement kind is unrecognized. Use equilibrium, intrinsic, apparent, or kinetic.")
            condition_values["measurement_kind"] = None
        review = reviews.get(key, {})
        if not isinstance(review, dict):
            raise InputError("A review must contain a state and a note.")
        state = review.get("state", "pending")
        note = str(review.get("note", ""))[:2000]
        if state not in STATES:
            raise InputError("Unknown review state.")
        if state != "pending" and not note.strip():
            raise InputError("Every review decision needs a written reason.")
        comparable = converted is not None and all(v is not None for v in condition_values.values()) and not any(f["severity"] == "error" for f in flags)
        result.append({"key": key, "index": index + 1, "raw": raw, "record": row, "conversion": converted, "conditions": condition_values, "comparable": comparable, "flags": flags, "review": {"state": state, "note": note}})

    pairs = []
    for left, right in combinations(result, 2):
        if not left["conversion"] or not right["conversion"]:
            continue
        if _canonical(left["record"]["compound"]) != _canonical(right["record"]["compound"]):
            continue
        delta = abs(left["conversion"]["log_s"] - right["conversion"]["log_s"])
        different = [f for f in CONDITIONS if left["conditions"][f] != right["conditions"][f]]
        incomplete = not left["comparable"] or not right["comparable"]
        if incomplete:
            status = "insufficient_context"
        elif different:
            status = "different_conditions"
        elif delta > threshold and not math.isclose(delta, threshold, abs_tol=1e-12):
            status = "disagreement"
        else:
            status = "within_threshold"
        pairs.append({"left": left["key"], "right": right["key"], "left_id": left["record"]["record_id"], "right_id": right["record"]["record_id"], "compound": left["record"]["compound"], "status": status, "delta_log_s": delta, "different_fields": different})
        if status == "disagreement":
            for a, b in [(left, right), (right, left)]:
                a["flags"].append({"code": "disagreement", "message": f"Differs from {b['record']['record_id']} by {delta:.3f} log units under the same recorded conditions. Review both sources; neither is automatically wrong.", "severity": "review"})
        if not incomplete and not different and math.isclose(delta, 0, abs_tol=1e-10) and left["record"]["source"] and left["record"]["source"] == right["record"]["source"] and left["record"]["evidence"] == right["record"]["evidence"]:
            right["flags"].append({"code": "possible_duplicate", "message": f"Same source, excerpt, conditions, and normalized value as {left['record']['record_id']}. Possible repeated evidence; no row was removed.", "severity": "review"})

    for row in result:
        row["status"] = "invalid" if any(f["severity"] == "error" for f in row["flags"]) else "review" if row["flags"] else "no_flags"
    summary = {"records": len(result), "normalized": sum(r["conversion"] is not None for r in result), "needs_review": sum(bool(r["flags"]) for r in result), "invalid": sum(r["status"] == "invalid" for r in result), "disagreements": sum(p["status"] == "disagreement" for p in pairs), "separate_conditions": sum(p["status"] == "different_conditions" for p in pairs), "reviewed": sum(r["review"]["state"] != "pending" for r in result)}
    return {"schema_version": 1, "engine_version": VERSION, "created_utc": datetime.now(timezone.utc).isoformat(), "input_sha256": fingerprint, "threshold_log_s": threshold, "summary": summary, "rows": result, "pairs": pairs, "limitations": ["Flags are deterministic review prompts, not validation of a paper or proof a result is correct.", "Matching recorded conditions does not establish scientific equivalence: purity, solid state, pressure, equilibration, and other unrecorded variables may differ.", "Compound and form identities are user-provided text. No structure, synonym, salt, or stereochemistry resolution is performed.", "Evidence excerpts and source references are preserved as supplied, not independently verified or parsed for agreement.", "No solubility predictions, clinical recommendations, or automatic corrections are produced."]}


def safe_cell(value):
    text = str(value) if value is not None else ""
    # Neutralize spreadsheet formulas, including leading whitespace/control characters.
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def export_csv(report):
    out = io.StringIO(newline="")
    extra = ["row_key", "mol_l", "log_s", "calculation", "review_status", "decision", "review_note", "flags", "input_sha256"]
    writer = csv.DictWriter(out, fieldnames=FIELDS + extra)
    writer.writeheader()
    for row in report["rows"]:
        converted = row["conversion"] or {}
        record = dict(row["record"])
        record.update({"row_key": row["key"], "mol_l": converted.get("mol_l", ""), "log_s": converted.get("log_s", ""), "calculation": converted.get("calculation", ""), "review_status": row["status"], "decision": row["review"]["state"], "review_note": row["review"]["note"], "flags": " | ".join(f["message"] for f in row["flags"]), "input_sha256": report["input_sha256"]})
        writer.writerow({k: safe_cell(v) if k not in {"mol_l", "log_s"} else v for k, v in record.items()})
    return out.getvalue()
