import copy
import csv
import io
import math
import unittest
from pathlib import Path

from tracesol.engine import InputError, MAX_ROWS, analyze, export_csv, normalize, parse_csv

ROOT = Path(__file__).resolve().parents[1]


def record(**changes):
    row = dict(record_id="X1", compound="Example", form="neutral", value="1", unit="uM", mw_g_mol="100", solvent="water", ph="7", temperature_c="25", method="shake-flask", measurement_kind="equilibrium", source="Synthetic A", evidence="Synthetic teaching example.", source_locator="Table 1")
    row.update(changes)
    return row


class ConversionTests(unittest.TestCase):
    def test_units_with_independently_known_answers(self):
        cases = [(1,"M",1),(1,"mol/L",1),(1,"mM",1e-3),(1,"mmol/L",1e-3),(1,"uM",1e-6),(1,"µM",1e-6),(1,"μM",1e-6),(1,"umol/L",1e-6),(1,"nM",1e-9),(1,"nmol/L",1e-9),(1,"g/L",.01),(1,"mg/L",1e-5),(1,"ug/L",1e-8),(1,"mg/mL",.01),(1,"ug/mL",1e-5),(-6,"logS",1e-6),(-6,"log10(mol/L)",1e-6)]
        for value,unit,expected in cases:
            with self.subTest(unit=unit):
                actual=normalize(value,unit,100)
                self.assertTrue(math.isclose(actual["mol_l"],expected,rel_tol=1e-12))
                self.assertAlmostEqual(actual["log_s"],math.log10(expected),12)

    def test_molar_prefixes_are_case_sensitive(self):
        self.assertEqual(normalize(1,"M")["mol_l"] / normalize(1,"mM")["mol_l"],1000)
        with self.assertRaises(InputError): normalize(1,"mm")

    def test_mass_requires_positive_mw(self):
        for weight in ["",0,-100,"NaN","Infinity"]:
            with self.subTest(mw=weight),self.assertRaises(InputError): normalize(1,"mg/L",weight)

    def test_rejects_ambiguous_and_unsupported_units(self):
        for unit in ["ppm","%","mol/kg","mg","unknown"]:
            with self.subTest(unit=unit),self.assertRaises(InputError): normalize(1,unit,100)

    def test_nonfinite_negative_and_overflow(self):
        for value,unit in [("NaN","M"),("Infinity","M"),(-1,"M"),(0,"M"),(999,"logS"),(-999,"logS"),("not a number","M")]:
            with self.subTest(value=value,unit=unit),self.assertRaises(InputError): normalize(value,unit)

    def test_equivalent_mass_and_molar_inputs(self):
        self.assertAlmostEqual(normalize(.30224,"mg/L",302.24)["log_s"],normalize(1,"uM")["log_s"],12)


class ImportTests(unittest.TestCase):
    def test_bom_quotes_newlines_and_extra_fields_preserved(self):
        rows=parse_csv('\ufeffrecord_id,compound,value,unit,evidence,custom\nA,Example,1,uM,"A quote, with comma\nand newline",extra\n')
        self.assertEqual(rows[0]["custom"],"extra")
        self.assertIn("\n",rows[0]["evidence"])

    def test_bad_headers_and_shapes(self):
        for text in ["", "name,value\nx,1", "record_id,compound,value,unit,value\nA,X,1,M,2", "record_id,compound,value,unit\nA,X,1", "record_id,compound,value,unit\nA,X,1,M,extra", "record_id,compound,value,unit\n", 'record_id,compound,value,unit\nA,"X,1,M']:
            with self.subTest(text=text),self.assertRaises(InputError): parse_csv(text)

    def test_size_and_row_limits(self):
        for text in ["x"*2_000_001,"record_id,compound,value,unit\n"+"A,X,1,M\n"*(MAX_ROWS+1)]:
            with self.assertRaises(InputError): parse_csv(text)


class ReviewTests(unittest.TestCase):
    def pair(self, **changes):
        return analyze([record(),record(record_id="X2",source="Synthetic B",**changes)])

    def test_disagreement_only_under_same_complete_context(self):
        r=self.pair(value="100")
        self.assertEqual(r["pairs"][0]["status"],"disagreement")
        self.assertEqual(r["summary"]["disagreements"],1)
        self.assertTrue(all(any(f["code"]=="disagreement" for f in row["flags"]) for row in r["rows"]))

    def test_every_condition_difference_prevents_conflict(self):
        for field,value in [("form","hydrate"),("solvent","ethanol"),("ph","8"),("temperature_c","30"),("method","turbidimetry"),("measurement_kind","kinetic")]:
            with self.subTest(field=field):
                r=self.pair(value="100",**{field:value})
                self.assertEqual(r["pairs"][0]["status"],"different_conditions")
                self.assertEqual(r["summary"]["disagreements"],0)

    def test_different_compounds_not_compared(self):
        self.assertFalse(self.pair(compound="Other",value="100")["pairs"])

    def test_unknown_conditions_never_equal_unknown(self):
        r=analyze([record(ph=""),record(record_id="X2",ph="",value="100")])
        self.assertEqual(r["pairs"][0]["status"],"insufficient_context")

    def test_unknown_measurement_kind_prevents_a_disagreement_conclusion(self):
        r=analyze([record(measurement_kind="unknown"),record(record_id="X2",measurement_kind="unknown",value="100")])
        self.assertEqual(r["pairs"][0]["status"],"insufficient_context")

    def test_invalid_conditions_prevent_comparison(self):
        for change in [{"ph":"NaN"},{"ph":"99"},{"temperature_c":"-273.15"},{"temperature_c":"Infinity"}]:
            with self.subTest(change=change):
                r=self.pair(value="100",**change)
                self.assertEqual(r["rows"][1]["status"],"invalid")
                self.assertEqual(r["pairs"][0]["status"],"insufficient_context")

    def test_numeric_and_text_context_normalization(self):
        r=self.pair(ph="7.0",temperature_c="25.00",solvent=" WATER ",value="100")
        self.assertEqual(r["pairs"][0]["status"],"disagreement")

    def test_exact_threshold_is_not_disagreement(self):
        r=analyze([record(value="-6",unit="logS"),record(record_id="X2",value="-5.5",unit="logS")],.5)
        self.assertEqual(r["pairs"][0]["status"],"within_threshold")

    def test_threshold_sensitivity(self):
        rows=[record(value="-6",unit="logS"),record(record_id="X2",value="-5.4",unit="logS")]
        self.assertEqual(analyze(rows,.5)["summary"]["disagreements"],1)
        self.assertEqual(analyze(rows,1)["summary"]["disagreements"],0)

    def test_invalid_threshold_and_row_types(self):
        for threshold in [0,-1,11,"nan","bad"]:
            with self.assertRaises(InputError): analyze([record()],threshold)
        for rows in [None,{},[],[1],[record()]*(MAX_ROWS+1)]:
            with self.assertRaises(InputError): analyze(rows)

    def test_no_flags_does_not_mean_verified(self):
        r=analyze([record()])
        self.assertEqual(r["rows"][0]["status"],"no_flags")
        self.assertTrue(any("not validation" in l for l in r["limitations"]))

    def test_missing_provenance_is_flagged(self):
        r=analyze([record(source="",evidence="",source_locator="")])
        codes={f["code"] for f in r["rows"][0]["flags"]}
        self.assertTrue({"missing_source","missing_evidence","missing_source_locator"}<=codes)

    def test_duplicate_does_not_delete_evidence(self):
        r=analyze([record(),record(record_id="X2")])
        self.assertEqual(len(r["rows"]),2)
        self.assertIn("possible_duplicate",[f["code"] for f in r["rows"][1]["flags"]])

    def test_review_needs_reason_and_preserves_raw(self):
        original=record(custom="original")
        before=copy.deepcopy(original)
        for review in [{"state":"retain","note":""},{"state":"invented","note":"x"},"bad"]:
            with self.assertRaises(InputError): analyze([original],reviews={"row-1":review})
        r=analyze([original],reviews={"row-1":{"state":"exclude","note":"Need source confirmation"}})
        self.assertEqual(r["rows"][0]["raw"]["custom"],"original")
        self.assertEqual(r["summary"]["records"],1)
        self.assertEqual(original,before)

    def test_fingerprint_changes_only_with_input_not_decision(self):
        a=analyze([record()]);b=analyze([record()],reviews={"row-1":{"state":"retain","note":"Checked source"}});c=analyze([record(value="2")])
        self.assertEqual(a["input_sha256"],b["input_sha256"])
        self.assertNotEqual(a["input_sha256"],c["input_sha256"])

    def test_csv_export_escapes_formulas_and_preserves_numeric_log(self):
        r=analyze([record(compound="  =HYPERLINK(1)",source="@cmd",evidence="\t+calc")])
        row=next(csv.DictReader(io.StringIO(export_csv(r))))
        for field in ["compound","source","evidence"]:
            self.assertTrue(row[field].startswith("'"))
        self.assertEqual(float(row["log_s"]),-6)

    def test_demo_expected_scenarios(self):
        r=analyze(parse_csv((ROOT/"data/demo.csv").read_text(encoding="utf-8")))
        self.assertEqual(r["summary"]["records"],12)
        self.assertEqual(r["summary"]["normalized"],10)
        self.assertEqual(r["summary"]["invalid"],2)
        self.assertEqual(r["summary"]["disagreements"],2)
        self.assertEqual(next(p for p in r["pairs"] if {p["left_id"],p["right_id"]}=={"Q-01","Q-04"})["status"],"different_conditions")
        self.assertEqual(next(p for p in r["pairs"] if {p["left_id"],p["right_id"]}=={"Q-01","Q-06"})["status"],"different_conditions")


if __name__ == "__main__":
    unittest.main()
