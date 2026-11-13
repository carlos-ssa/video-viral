import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _common import load_manifest, save_manifest
from trends import explore_url, import_csv, parse_interest_csv


class TrendsTests(unittest.TestCase):
    def test_full_hourly_period_validation(self):
        data = parse_interest_csv('Hour,Corte\n2026-11-01T23:00:00,50\n')
        self.assertEqual(data['points'][0]['period'], '2026-11-01T23:00:00')
        for period in ('2026-11-01garbage', '2026-11-01T25:00:00', '2026-11-01T12:99'):
            with self.subTest(period=period), self.assertRaises(ValueError):
                parse_interest_csv(f'Hour,Corte\n{period},50\n')

    def test_query_keeps_geo_period_property_and_unicode(self):
        params = parse_qs(urlparse(explore_url(["salão de beleza", "barbearia"], "BR-SP", "today 12-m", "youtube", 44)).query)
        self.assertEqual(params["q"], ["salão de beleza,barbearia"])
        self.assertEqual(params["geo"], ["BR-SP"])
        self.assertEqual(params["date"], ["today 12-m"])
        self.assertEqual(params["gprop"], ["youtube"])
        self.assertEqual(params["cat"], ["44"])

    def test_web_query_does_not_select_youtube(self):
        self.assertNotIn("gprop", parse_qs(urlparse(explore_url(["x"], property_="web")).query))

    def test_official_csv_with_preamble_bom_and_censored_value(self):
        data = parse_interest_csv('\ufeffCategory: All categories\n\nWeek,Corte: (Brazil),Cor: (Brazil)\n2026-11-01,100,<1\n2026-11-08,0,\n')
        self.assertEqual(data["points"][0]["values"]["Corte: (Brazil)"]["index"], 100)
        censored = data["points"][0]["values"]["Cor: (Brazil)"]
        self.assertIsNone(censored["index"])
        self.assertTrue(censored["below_one"])
        self.assertFalse(data["points"][1]["values"]["Cor: (Brazil)"]["below_one"])

    def test_portuguese_semicolon_csv(self):
        data = parse_interest_csv('Categoria: Todas\n\nDia;Corte: (Brasil)\n2026-11-01;50\n')
        self.assertEqual(len(data["points"]), 1)

    def test_monthly_period_is_preserved(self):
        data = parse_interest_csv('Month,Corte\n2026-11,50\n')
        self.assertEqual(data["points"][0]["period"], "2026-11")

    def test_regions_and_invalid_data_rejected(self):
        for csv_text in ('País,Corte\nBrasil,100\n', 'Week,Corte\n2026-11-01,101\n',
                         'Week,Corte\n2026-11-01,wat\n', 'Week,Corte,Corte\n2026-11-01,1,2\n',
                         'Week,Corte\n2026-99-01,50\n', 'Week,Corte\n2026-11-01,1,2\n', 'Week,Corte\n'):
            with self.subTest(csv_text=csv_text), self.assertRaises(ValueError):
                parse_interest_csv(csv_text)

    def test_import_preserves_source_provenance_and_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            save_manifest(proj, {"title": "Preservar", "research": {"hypotheses": ["hipótese"]}})
            source = proj / "input.csv"
            source.write_text('Week,Corte: (Brasil)\n2026-11-01,50\n', encoding="utf-8")
            record = import_csv(proj, source, ["Corte"], "BR", "today 3-m", "youtube")
            data = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual((proj / data["source_csv"]).read_bytes(), source.read_bytes())
            self.assertEqual(data["scale"], "relative_index_0_100")
            self.assertEqual(load_manifest(proj)["research"]["hypotheses"], ["hipótese"])
            self.assertEqual(load_manifest(proj)["research"]["google_trends"]["source_sha256"], data["source_sha256"])

    def test_different_declared_filters_preserve_both_records(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            save_manifest(proj, {})
            source = proj / "input.csv"
            source.write_text('Week,Corte\n2026-11-01,50\n', encoding="utf-8")
            first = import_csv(proj, source, ["Corte"], "BR", "today 3-m", "youtube")
            second = import_csv(proj, source, ["Corte"], "PT", "today 3-m", "youtube")
            self.assertNotEqual(first, second)
            self.assertEqual(json.loads(first.read_text(encoding="utf-8"))["geo"], "BR")
            self.assertEqual(json.loads(second.read_text(encoding="utf-8"))["geo"], "PT")

    def test_wrong_terms_rejected_without_manifest_change(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            save_manifest(proj, {"title": "original"})
            source = proj / "input.csv"
            source.write_text('Week,Corte: (Brasil)\n2026-11-01,50\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                import_csv(proj, source, ["Outro"], "BR", "today 3-m", "youtube")
            self.assertEqual(load_manifest(proj), {"title": "original"})
            self.assertFalse((proj / "research").exists())


if __name__ == "__main__":
    unittest.main()
