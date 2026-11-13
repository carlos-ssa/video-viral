import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _common import file_sha256, manifest_sha256, save_manifest
import review


class VerdictTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.proj = Path(self.temp.name)
        self.round = self.proj / "review" / "r01"
        self.round.mkdir(parents=True)
        (self.proj / "out").mkdir()
        self.video = self.proj / "out" / "example.mp4"
        self.video.write_bytes(b"opaque fixture: provenance unit test, not an encoded video")
        self.manifest = {"format": "gravacao", "aspect": "9:16"}
        save_manifest(self.proj, self.manifest)
        for name in ("hook.jpg", "grid.jpg"):
            (self.round / name).write_bytes(name.encode())
        digest = file_sha256(self.video)
        self.metrics = {"schema": 2, "video": str(self.video), "video_sha256": digest,
                        "manifest_sha256": manifest_sha256(self.manifest), "has_audio": True,
                        "duration": 2, "rubric": [k for k, _ in review.rubric_for(self.manifest, 2)],
                        "blockers": [], "frame_sha256": {n: file_sha256(self.round / n) for n in ("hook.jpg", "grid.jpg")}}
        self.receipt = {"schema": 1, "video": str(self.video), "video_sha256": digest,
                        "manifest_sha256": self.metrics["manifest_sha256"],
                        "approved": True, "draft": False}
        self.assessment = {"video_sha256": digest, **{k: {"status": "instrumented", "method": "unit fixture",
                                                       "ranges": [[0, 2]]} for k in ("visual", "motion", "audio")}}
        self.write_evidence()
        self.write_scores()

    def write_json(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_evidence(self):
        self.write_json(self.round / "metrics.json", self.metrics)
        self.write_json(self.proj / "out" / "delivery.json", self.receipt)
        self.write_json(self.round / "assessment.json", self.assessment)

    def write_scores(self, score="4"):
        (self.round / "report.md").write_text("\n".join(f"| {k} | {score} |" for k in self.metrics["rubric"]), encoding="utf-8")

    def verdict(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return review.verdict(self.proj)

    def test_rubric_matches_specialized_formats(self):
        music = [k for k, _ in review.rubric_for({"format": "musica"}, 40)]
        self.assertIn("Sincronismo musical", music)
        self.assertNotIn("Fala e imagem", music)
        self.assertIn("Sincronia labial", [k for k, _ in review.rubric_for({"format": "avatar"}, 40)])
        self.assertIn("Continuidade", [k for k, _ in review.rubric_for({"format": "storytelling"}, 40)])
        self.assertIn("Mensagem e CTA", [k for k, _ in review.rubric_for({"brief": {"objective": "conversao"}}, 40)])

    def test_complete_consistent_evidence_passes(self):
        self.assertEqual(self.verdict(), 0)

    def test_missing_or_malformed_metrics_never_pass(self):
        (self.round / "metrics.json").unlink()
        self.assertEqual(self.verdict(), 2)
        (self.round / "metrics.json").write_text("{", encoding="utf-8")
        self.assertEqual(self.verdict(), 2)

    def test_missing_video_never_passes(self):
        self.video.unlink()
        self.assertEqual(self.verdict(), 2)

    def test_replaced_video_invalidates_scores(self):
        self.video.write_bytes(b"different render")
        self.assertEqual(self.verdict(), 2)

    def test_missing_or_changed_frames_invalidate_scores(self):
        (self.round / "hook.jpg").write_bytes(b"different frames")
        self.assertEqual(self.verdict(), 2)
        (self.round / "grid.jpg").unlink()
        self.assertEqual(self.verdict(), 2)

    def test_creative_manifest_change_invalidates_review(self):
        save_manifest(self.proj, {**self.manifest, "cta": "novo destino"})
        self.assertEqual(self.verdict(), 2)

    def test_appending_review_history_does_not_invalidate_review(self):
        save_manifest(self.proj, {**self.manifest, "review": [{"round": "r01"}]})
        self.assertEqual(self.verdict(), 0)

    def test_delivery_must_match_render_and_be_publishable(self):
        for change, expected in [({"approved": False}, 1), ({"draft": True}, 1),
                                 ({"video_sha256": "other"}, 2)]:
            with self.subTest(change=change):
                self.write_json(self.proj / "out" / "delivery.json", {**self.receipt, **change})
                self.assertEqual(self.verdict(), expected)

    def test_missing_or_pending_assessment_never_passes(self):
        (self.round / "assessment.json").unlink()
        self.assertEqual(self.verdict(), 2)
        self.assessment["audio"]["status"] = "pending"
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_license_changes_need_new_technical_delivery(self):
        self.manifest["assets"] = [{"path": "music.wav", "commercial_ok": False}]
        save_manifest(self.proj, self.manifest)
        self.metrics["manifest_sha256"] = manifest_sha256(self.manifest)
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_unverified_audio_is_not_approved(self):
        self.assessment["audio"]["status"] = "unverified"
        self.write_evidence()
        self.assertEqual(self.verdict(), 1)

    def test_inspected_ranges_must_exist_and_fit_video(self):
        for ranges in ([], [[0, 3]], [[1, 0]], [[-1, 1]]):
            with self.subTest(ranges=ranges):
                self.assessment["motion"]["ranges"] = ranges
                self.write_evidence()
                self.assertEqual(self.verdict(), 2)

    def test_scores_cannot_exceed_five(self):
        self.write_scores("5.9")
        self.assertEqual(self.verdict(), 2)

    def test_third_failed_round_is_a_limit_not_approval(self):
        self.write_scores("3")
        self.round.rename(self.round.with_name("r03"))
        self.assertEqual(self.verdict(), 3)


if __name__ == "__main__":
    unittest.main()
