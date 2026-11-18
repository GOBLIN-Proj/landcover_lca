"""Inventory alignment: landcover_lca given the NID/CRT 2026 areas, compared with the CRT 2026 emissions.

The rows to compare are listed in data/inventory/inventory_coverage.csv. Each row has a status:
    covered   must match the CRT within its tolerance (a normal test)
    gap       a known difference, owned by a dossier; run as expectedFailure. When the dossier's fix
              makes it pass, unittest reports an "unexpected success": flip the row to covered.
    excluded  not comparable (out of scope, not modelled, or zero by construction); not run
Inputs are built by inventory_inputs.py (see its docstring for the mapping and its caveats).

crt_terms: "key:quantity" cells of crt2026_lulucf.csv, summed. Quantities ending in "_soil_C" are kt C with
the CRT sign (+ = gain) and are converted to an emission in kt CO2 (x -44/12).
years: a range "YYYY-YYYY", one year, or "fire" (the years with a published burnt area, CRF 2024: 2020-2022).
basis: per_year (each year within tolerance) or sum (the sum over the years within tolerance).
tolerance: relative; an expected value of 0 (CRT NO) allows at most 1 kg.
"""
import ast
import inspect
import os
import unittest

import pandas as pd

import inventory_inputs as ii
import landcover_lca.lca_emission as lca

COVERAGE = pd.read_csv(os.path.join(ii.INV, "inventory_coverage.csv"), dtype=str).fillna("")
CATEGORIES = ["A.1", "A.2", "B.1", "B.2", "C.1", "C.2", "D.1", "D.2", "E.1", "E.2", "F.1", "F.2", "G"]
ABS_FLOOR_KT = 1e-6  # 1 kg: only so that a CRT "NO" (0) can be matched exactly


def _years(spec):
    if spec == "fire":
        return list(ii.FIRE_YEARS)
    if "-" in spec:
        a, b = spec.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(spec)]


def expected_kt(year, crt_terms):
    total = 0.0
    for term in crt_terms.split(";"):
        key, quantity = term.split(":")
        value = ii.crt(year, key, quantity)
        total += -value * ii.C_TO_CO2 if quantity.endswith("_soil_C") else value
    return total


def package_kt(year, functions):
    return sum(ii.run(getattr(lca, name), year) for name in functions.split(";")) / 1e6


def _check(test, row):
    years = _years(row.years)
    tol = float(row.tolerance)
    pairs = [(y, package_kt(y, row.functions), expected_kt(y, row.crt_terms)) for y in years]

    def close(p, e):
        return abs(p - e) <= max(tol * abs(e), ABS_FLOOR_KT)

    if row.basis == "sum":
        p, e = sum(x[1] for x in pairs), sum(x[2] for x in pairs)
        test.assertTrue(close(p, e), f"{row.id} {years[0]}-{years[-1]} sum: package {p:.3f} kt, CRT {e:.3f} kt")
    else:
        for y, p, e in pairs:
            with test.subTest(year=y):
                test.assertTrue(close(p, e), f"{row.id} {y}: package {p:.3f} kt, CRT {e:.3f} kt")


class TestInventoryAlignment(unittest.TestCase):
    """One test per covered or gap row of the coverage map (added below)."""


def _make(row):
    def test(self):
        _check(self, row)

    test.__doc__ = f"{row.status}: {row.reason}"
    return unittest.expectedFailure(test) if row.status == "gap" else test


for _row in COVERAGE.itertuples(index=False):
    if _row.status in ("covered", "gap"):
        setattr(TestInventoryAlignment, f"test_{_row.id}", _make(_row))


class TestCoverageMap(unittest.TestCase):
    def test_rows_are_well_formed(self):
        self.assertTrue(COVERAGE.id.is_unique)
        self.assertTrue(set(COVERAGE.status) <= {"covered", "gap", "excluded"})
        for row in COVERAGE.itertuples(index=False):
            with self.subTest(row=row.id):
                self.assertTrue(row.reason, "every row states its reason")
                for name in filter(None, row.functions.split(";")):
                    self.assertTrue(hasattr(lca, name), name)
                if row.status == "gap":
                    self.assertTrue(row.dossier, "every gap names its dossier")
                if row.status in ("covered", "gap"):
                    self.assertTrue(row.functions and row.crt_terms and row.years and row.tolerance)
                    self.assertIn(row.basis, ("per_year", "sum"))

    def test_every_crt_category_is_mapped(self):
        mapped = {c for cats in COVERAGE.category for c in cats.split(";")}
        self.assertEqual(sorted(set(CATEGORIES) - mapped), [])

    def test_crt_categories_sum_to_lulucf_total(self):
        """The fixture is complete: Table4 categories A.1 ... G add up to the LULUCF total (row 10)."""
        for year in ii.YEARS:
            for gas in ("CO2", "CH4", "N2O"):
                with self.subTest(year=year, gas=gas):
                    parts = sum(ii.crt(year, f"T4.{c}", gas) for c in CATEGORIES)
                    self.assertAlmostEqual(parts, ii.crt(year, "T4.total", gas), places=3)

    def test_every_total_term_is_mapped(self):
        """Every per-term function summed into total_{co2,ch4,n2o}_emission appears in the coverage map."""
        tree = ast.parse(inspect.getsource(lca))
        functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

        def leaves(name):
            out = set()
            for node in ast.walk(functions[name]):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in functions:
                    out |= leaves(node.func.id) if node.func.id.startswith("total_") else {node.func.id}
            return out

        terms = set().union(*(leaves(f"total_{g}_emission") for g in ("co2", "ch4", "n2o")))
        mapped = {f for fs in COVERAGE.functions for f in fs.split(";") if f}
        self.assertEqual(sorted(terms - mapped), [])


if __name__ == "__main__":
    unittest.main()
