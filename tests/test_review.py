import contextlib
import io
import json
import os
from pathlib import Path
import sys
import subprocess
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
        self.assessment = {"video_sha256": digest, "reviewer_preflight": {
            "schema": 1, "reviewer_id": "reviewer:fixture", "author_scores_exposed": False,
            "channels": {k: {"available": True, "method": "synthetic policy fixture",
                              "evidence": "test record; not a real perceptual review"} for k in review.CHANNELS}},
            **{k: {"status": "observed", "method": "synthetic policy fixture",
                                                       "ranges": [[0, 2]]} for k in ("visual", "motion", "audio")}}
        self.write_evidence()
        self.write_scores()

    def write_json(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_evidence(self):
        if not (self.round / 'input').exists():
            review.prepare_review_input(self.round, self.video, self.manifest, self.metrics, 'producer:fixture')
        request_path = self.round / 'input/request.json'
        request = json.loads(request_path.read_text(encoding='utf-8'))
        request.update(video_sha256=self.metrics['video_sha256'], manifest_sha256=self.metrics['manifest_sha256'])
        request['technical'].update(has_audio=self.metrics['has_audio'], duration=self.metrics['duration'])
        self.write_json(request_path, request)
        self.metrics['review_request_sha256'] = file_sha256(request_path)
        self.write_json(self.round / "metrics.json", self.metrics)
        self.write_json(self.proj / "out" / "delivery.json", self.receipt)
        self.write_json(self.round / "assessment.json", self.assessment)

    def write_scores(self, score="4"):
        (self.round / "report.md").write_text("\n".join(f"| {k} | critério | {score} | evidência sintética 0–2 s |" for k in self.metrics["rubric"]), encoding="utf-8")

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

    def test_scores_are_read_only_from_score_column_and_require_evidence(self):
        for row in ('| {key} | 4 |  | 5 |', '| {key} | critério | 4 |  |',
                    '| {key} | critério | 3 | evidência |\n| {key} | critério | 5 | evidência |'):
            with self.subTest(row=row):
                self.write_scores()
                report = self.round / 'report.md'
                lines = report.read_text(encoding='utf-8').splitlines()
                lines[0] = row.format(key=self.metrics['rubric'][0])
                report.write_text('\n'.join(lines), encoding='utf-8')
                self.assertEqual(self.verdict(), 2)

    def test_boolean_inspection_ranges_are_not_seconds(self):
        self.assessment['motion']['ranges'] = [[False, 2]]
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_analysis_blockers_cannot_be_removed_only_from_metrics(self):
        self.metrics['blockers'] = ['render bloqueado']
        self.write_evidence()
        request_path = self.round / 'input/request.json'
        request = json.loads(request_path.read_text(encoding='utf-8'))
        request['technical']['blockers'] = ['render bloqueado']
        self.write_json(request_path, request)
        self.metrics['review_request_sha256'] = file_sha256(request_path)
        self.metrics['blockers'] = []
        self.write_json(self.round / 'metrics.json', self.metrics)
        self.assertEqual(self.verdict(), 2)

    def test_independent_video_cannot_be_a_hard_link(self):
        clip = self.round / 'input/video.mp4'
        clip.unlink()
        os.link(self.video, clip)
        self.assertEqual(self.verdict(), 2)

    def test_malformed_report_returns_incomplete(self):
        (self.round / 'report.md').write_bytes(b'\xff')
        self.assertEqual(self.verdict(), 2)

    def test_reviewer_schema_must_be_an_integer_not_boolean(self):
        self.assessment['reviewer_preflight']['schema'] = True
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

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

    def test_round_video_is_independent_of_in_place_rerender(self):
        evidence = self.round / 'input/video.mp4'
        original = evidence.read_bytes()
        self.video.write_bytes(b'rerender overwrote delivery in place')
        self.assertEqual(evidence.read_bytes(), original)
        self.assertEqual(self.verdict(), 2)

    def test_modified_round_video_invalidates_scores(self):
        (self.round / 'input/video.mp4').write_bytes(b'tampered evidence')
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

    def test_author_cannot_review_own_video(self):
        self.assessment['reviewer_preflight']['reviewer_id'] = 'producer:fixture'
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_author_scores_exposure_requires_new_reviewer_context(self):
        self.assessment['reviewer_preflight']['author_scores_exposed'] = True
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_frame_only_reviewer_cannot_approve_audiovisual_result(self):
        for channel in ('motion', 'audio'):
            self.assessment['reviewer_preflight']['channels'][channel]['available'] = False
            self.assessment[channel]['status'] = 'unverified'
        self.write_evidence()
        self.assertEqual(self.verdict(), 1)

    def test_metrics_are_not_perceptual_approval(self):
        self.assessment['audio']['status'] = 'instrumented'
        self.write_evidence()
        self.assertEqual(self.verdict(), 1)

    def test_partial_review_does_not_require_fabricated_scores_or_new_round(self):
        self.assessment['audio']['status'] = 'unverified'
        self.write_evidence()
        self.write_scores('')
        before = self.video.read_bytes()
        self.assertEqual(self.verdict(), 1)
        self.assertEqual(self.video.read_bytes(), before)
        self.assertEqual(len(list((self.proj / 'review').iterdir())), 1)

    def test_claimed_observation_requires_capability(self):
        self.assessment['reviewer_preflight']['channels']['motion']['available'] = False
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_partial_ranges_do_not_approve_whole_video(self):
        self.assessment['motion']['ranges'] = [[0, 1]]
        self.write_evidence()
        self.assertEqual(self.verdict(), 1)
        self.assessment['motion']['ranges'] = [[0, 1.5], [0.5, 2]]
        self.write_evidence()
        self.assertEqual(self.verdict(), 0)

    def test_silent_video_does_not_require_audio_capability(self):
        self.metrics['has_audio'] = False
        self.assessment['audio']['status'] = 'not_applicable'
        self.assessment['reviewer_preflight']['channels']['audio']['available'] = False
        self.write_evidence()
        self.assertEqual(self.verdict(), 0)

    def test_missing_or_changed_review_request_is_rejected(self):
        (self.round / 'input/request.json').write_text('{}', encoding='utf-8')
        self.assertEqual(self.verdict(), 2)

    def test_capability_needs_method_and_evidence(self):
        self.assessment['reviewer_preflight']['channels']['audio']['evidence'] = ''
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_preflight_restricts_only_requested_scope(self):
        capability = self.assessment['reviewer_preflight']
        capability['channels']['audio']['available'] = False
        self.assertEqual(review.reviewer_preflight(capability, 'producer:fixture', ('visual',)), [])
        self.assertEqual(review.reviewer_preflight(capability, 'producer:fixture'), ['audio'])

    def test_review_input_excludes_author_score_report(self):
        folder = self.proj / 'separate-review'
        folder.mkdir()
        for name in ('hook.jpg', 'grid.jpg'):
            (folder / name).write_bytes(name.encode())
        (folder / 'report.md').write_text('Author says: all grades 5', encoding='utf-8')
        review.prepare_review_input(folder, self.video, self.manifest, self.metrics, 'producer:fixture')
        self.assertEqual({p.name for p in (folder / 'input').iterdir()}, {'video.mp4', 'hook.jpg', 'grid.jpg', 'request.json'})
        self.assertNotIn('Author says', (folder / 'input/request.json').read_text(encoding='utf-8'))

    def test_extra_author_report_in_input_blocks_approval(self):
        (self.round / 'input/report.md').write_text('Author grades: 5', encoding='utf-8')
        self.assertEqual(self.verdict(), 2)

    def test_modalities_cannot_diverge_from_review_package(self):
        self.metrics['has_audio'] = False
        self.write_json(self.round / 'metrics.json', self.metrics)
        self.assessment['audio']['status'] = 'not_applicable'
        self.write_json(self.round / 'assessment.json', self.assessment)
        self.assertEqual(self.verdict(), 2)

    def filled_human_form(self):
        review.human_form(self.round, self.metrics)
        path = self.round / 'ficha-humana.md'
        text = path.read_text(encoding='utf-8')
        fields = {'Revisor': 'human:fixture', 'Notas do autor não consultadas': 'SIM',
                  'Assisti ao vídeo inteiro': 'SIM', 'Ouvi o áudio inteiro': 'SIM',
                  'Início observado': '0', 'Fim observado': '2',
                  'Método e aparelho': 'synthetic unit fixture; no real playback',
                  'Observações gerais': 'registro sintético para testar política'}
        for label, value in fields.items():
            text = text.replace(f'{label}: \n', f'{label}: {value}\n')
        for key in self.metrics['rubric']:
            text = text.replace(f'| {key} |  |  |', f'| {key} | 4 | trecho sintético 0–2 s |')
        path.write_text(text, encoding='utf-8')
        return path

    def test_valid_human_form_passes_same_verdict(self):
        path = self.filled_human_form()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(review.ingest_human_form(self.proj, path), 0)
        assessment = json.loads((self.round / 'assessment.json').read_text(encoding='utf-8'))
        self.assertEqual(assessment['reviewer_preflight']['reviewer_type'], 'human')
        self.assertEqual(assessment['audio']['ranges'], [[0, 2]])
        self.assertEqual(assessment['audio']['status'], 'observed')
        self.assertEqual(self.verdict(), 0)

    def test_empty_human_form_preserves_assessment(self):
        review.human_form(self.round, self.metrics)
        before = (self.round / 'assessment.json').read_bytes()
        with self.assertRaises(ValueError):
            review.ingest_human_form(self.proj, self.round / 'ficha-humana.md')
        self.assertEqual((self.round / 'assessment.json').read_bytes(), before)

    def test_human_form_rejects_author_hash_partial_or_missing_confirmations(self):
        for old, new in [('Revisor: human:fixture', 'Revisor: PRODUCER:fixture'),
                         (self.metrics['video_sha256'], 'bad-hash'),
                         (self.metrics['manifest_sha256'], 'bad-manifest'),
                         ('Fim observado: 2', 'Fim observado: 1'),
                         ('Fim observado: 2', 'Fim observado: nan'),
                         ('Ouvi o áudio inteiro: SIM', 'Ouvi o áudio inteiro: NA'),
                         ('Assisti ao vídeo inteiro: SIM', 'Assisti ao vídeo inteiro: NÃO'),
                         ('Notas do autor não consultadas: SIM', 'Notas do autor não consultadas: NÃO'),
                         ('| 4 | trecho sintético', '|  | trecho sintético')]:
            with self.subTest(new=new):
                path = self.filled_human_form()
                path.write_text(path.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
                before = (self.round / 'assessment.json').read_bytes()
                with self.assertRaises(ValueError):
                    review.ingest_human_form(self.proj, path)
                self.assertEqual((self.round / 'assessment.json').read_bytes(), before)

    def test_human_form_cli_passes_and_rejects_empty_without_ffmpeg(self):
        command = [sys.executable, str(Path(review.__file__)), str(self.proj), '--human-form']
        result = subprocess.run(command + [str(self.filled_human_form())], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        review.human_form(self.round, self.metrics)
        result = subprocess.run(command + [str(self.round / 'ficha-humana.md')], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('FICHA HUMANA INVÁLIDA', result.stdout)

    def test_human_form_preserves_silent_video_and_low_grade_rules(self):
        self.metrics['has_audio'] = False
        self.write_evidence()
        path = self.filled_human_form()
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('| 4 | trecho sintético', '| 3 | trecho sintético', 1), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(review.ingest_human_form(self.proj, path), 1)
        assessment = json.loads((self.round / 'assessment.json').read_text(encoding='utf-8'))
        self.assertEqual(assessment['audio']['status'], 'not_applicable')

    def test_human_form_does_not_override_technical_failure(self):
        self.receipt['approved'] = False
        self.write_evidence()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(review.ingest_human_form(self.proj, self.filled_human_form()), 1)

    def test_human_form_stale_video_never_passes(self):
        path = self.filled_human_form()
        self.video.write_bytes(b'new render')
        with self.assertRaises(ValueError):
            review.ingest_human_form(self.proj, path)

    def test_pristine_assessment_reports_human_pending_without_approval(self):
        self.assessment = {'video_sha256': self.metrics['video_sha256'],
                           'reviewer_preflight': review.empty_preflight(),
                           **{ch: {'status': 'pending', 'method': '', 'ranges': []} for ch in review.CHANNELS}}
        self.write_evidence()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(review.verdict(self.proj), 2)
        self.assertIn('ENTREGA TÉCNICA APROVADA, REVISÃO HUMANA PENDENTE', output.getvalue())
        self.receipt['approved'] = False
        self.write_evidence()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(review.verdict(self.proj), 2)
        self.assertNotIn('ENTREGA TÉCNICA APROVADA', output.getvalue())

    def test_self_check_does_not_replace_pending_independent_reviewer(self):
        self.assessment = {'video_sha256': self.metrics['video_sha256'],
                           'reviewer_preflight': review.empty_preflight(),
                           **{ch: {'status': 'pending', 'method': '', 'ranges': []} for ch in review.CHANNELS},
                           'self_check': {'producer_id': 'producer:fixture', 'independent': False,
                                          'audio': {'status': 'instrumented', 'method': 'LUFS e silencedetect',
                                                    'ranges': [[0, 2]]}}}
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)

    def test_assessment_method_requires_text(self):
        self.assessment['motion']['method'] = None
        self.write_evidence()
        self.assertEqual(self.verdict(), 2)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.proj = Path(self.temp.name)

    def test_fourth_round_is_blocked_without_modifying_previous_rounds(self):
        for index in range(1, 4):
            folder = review.next_round(self.proj)
            self.assertEqual(folder.name, f'r{index:02d}')
            (folder / 'evidence.bin').write_bytes(bytes([index]))
        before = {p.relative_to(self.proj): p.read_bytes() for p in self.proj.rglob('*') if p.is_file()}
        with self.assertRaises(review.RoundLimitError):
            review.next_round(self.proj)
        self.assertEqual(before, {p.relative_to(self.proj): p.read_bytes() for p in self.proj.rglob('*') if p.is_file()})
        self.assertFalse((self.proj / 'review/r04').exists())

    def test_jpeg_budget_accepts_supported_grid_and_rejects_overflow(self):
        review.validate_grid(1000, 1, 180, 320)
        for every in (0, -1, float('nan'), float('inf'), 1e-300):
            with self.subTest(every=every), self.assertRaises(ValueError):
                review.validate_grid(4, every, 180, 320)

    def test_freeze_at_end_has_same_threshold_as_middle(self):
        for span in (2.3, 2.5, 4.0):
            with self.subTest(span=span):
                mid = review.freeze_checks([(1, span)], 10, False, [])
                end = review.freeze_checks([(10 - span, None)], 10, False, [])
                self.assertEqual(bool(mid[0]), bool(end[0]))
                self.assertEqual(bool(mid[1]), bool(end[1]))

    def test_caption_reading_and_long_video_do_not_trigger_short_freeze_gate(self):
        self.assertTrue(review.freeze_checks([(0, 6)], 20, False, [])[0])
        self.assertFalse(review.freeze_checks([(0, 6)], 20, False, [(0, 2), (2, 4), (4, 6)])[0])
        self.assertFalse(review.freeze_checks([(0, 6)], 20, True, [])[0])
        self.assertTrue(review.freeze_checks([(0, 13)], 20, True, [])[0])

    def test_speech_is_not_inferred_from_pulses_or_music(self):
        for manifest in ({'voice': {'engine': 'none'}}, {'format': 'musica'},
                         {'scenes': [{'narration': ''}]}, {'format': 'asmr-impossivel'}):
            self.assertFalse(review.expects_speech(manifest))
        self.assertTrue(review.expects_speech({'format': 'gravacao', 'voice': {'engine': 'none'}}))
        self.assertTrue(review.expects_speech({'scenes': [{'narration': 'Oi'}]}))

    def test_silent_sound_led_video_fails_even_if_lufs_would_pass(self):
        block, warn = review.audio_checks({'voice': {'engine': 'none'}}, 10, False,
                                         {'silences': [(0.2, 10)], 'audible_fraction': 0.02}, [], [])
        self.assertIn('apenas 2%', block[0])
        self.assertIn('LUFS', block[0])
        self.assertFalse(review.audio_checks({'voice': {'engine': 'none'}}, 10, False,
                                            {'silences': [], 'audible_fraction': 0.5}, [], [])[0])

    def test_middle_silence_warns_with_time_and_correction_and_long_threshold(self):
        activity = {'silences': [(2, 3.1)], 'audible_fraction': 0.89}
        block, warn = review.audio_checks({}, 10, False, activity, [], [])
        self.assertFalse(block)
        self.assertIn('2.0–3.1 s', warn[0])
        self.assertIn('encurte', warn[0])
        self.assertFalse(review.audio_checks({}, 10, True, activity, [], [])[1])

    def test_dead_tail_requires_all_three_signals(self):
        activity = {'silences': [(3.5, 6)], 'audible_fraction': 0.6}
        self.assertIn('Cauda morta', review.audio_checks({}, 6, False, activity, [(4, None)], [])[0][0])
        self.assertFalse(review.audio_checks({}, 6, False, activity, [], [])[0])
        self.assertFalse(review.audio_checks({}, 6, False, activity, [(4, None)], [(4, 6)])[0])
        audible = {'silences': [], 'audible_fraction': 1}
        self.assertFalse(review.audio_checks({}, 6, False, audible, [(4, None)], [])[0])
        unknown = review.audio_checks({}, 6, False, activity, [(4, None)], None)
        self.assertFalse(unknown[0])
        self.assertIn('tempos de exibição', unknown[1][0])
        self.assertFalse(review.audio_checks({}, 6, True, activity, [(4, None)], [])[0])

    def test_residual_motion_tail_is_joint_gate_not_a_freeze(self):
        activity = {'silences': [(3.5, 6)], 'audible_fraction': 0.6}
        for fps in (10, 30):
            energy = [(i / fps, 2 / fps) for i in range(1, 6 * fps)]
            block, _ = review.audio_checks({}, 6, False, activity, [], [], energy)
            self.assertTrue(any('Cauda morta' in b for b in block))
            self.assertEqual(review.freeze_checks([], 6, False, []), ([], []))
        energy = [(i / 10, 2) for i in range(1, 60)]
        self.assertFalse(review.audio_checks({}, 6, False, activity, [], [], energy)[0])

    def test_caption_timing_uses_display_cues_not_asr_words(self):
        captions = self.proj / 'captions'
        captions.mkdir()
        (captions / 'words.json').write_text('[{"start":0,"end":2,"word":"Oi"}]')
        self.assertIsNone(review.caption_ranges(self.proj, {}))
        (captions / 'captions.ass').write_text('[Events]\nDialogue: 0,0:00:00.50,0:00:02.30,Default,,0,0,0,,Oi\n')
        self.assertEqual(review.caption_ranges(self.proj, {}), [(0.5, 2.3)])
        (captions / 'captions.ass').unlink()
        (captions / 'captions.json').write_text('[{"start":1,"end":3,"text":"Oi"}]')
        self.assertEqual(review.caption_ranges(self.proj, {}), [(1, 3)])

    def test_malformed_caption_ranges_cannot_downgrade_a_freeze(self):
        folder = self.proj / 'captions'
        folder.mkdir()
        for cue in ({'start': 0, 'end': float('inf'), 'text': 'Oi'},
                    {'start': False, 'end': 8, 'text': 'Oi'},
                    {'start': -1, 'end': 8, 'text': 'Oi'},
                    {'start': 2, 'end': 1, 'text': 'Oi'},
                    {'start': 0, 'end': 8, 'text': ''}):
            with self.subTest(cue=cue):
                (folder / 'captions.json').write_text(json.dumps([cue]), encoding='utf-8')
                ranges = review.caption_ranges(self.proj, {})
                self.assertIsNone(ranges)
                self.assertTrue(review.freeze_checks([(0, 6)], 8, False, ranges)[0])

    def test_effects_accept_real_audio_asset_and_default_output_without_kind_sfx(self):
        for manifest in ({'assets': [{'path': 'audio/sound-design.wav', 'kind': 'audio'}]},
                         {'assets': [{'path': 'audio/custom.wav', 'role': 'sfx'}]}):
            self.assertTrue(review.has_audio_role(self.proj, manifest, 'sfx'))
        (self.proj / 'audio').mkdir()
        (self.proj / 'audio/sound-design.wav').touch()
        self.assertTrue(review.has_audio_role(self.proj, {}, 'sfx'))
        self.assertFalse(review.has_audio_role(self.proj, {'assets': [{'path': 'audio/voice.wav', 'kind': 'audio'}]}, 'bed'))

    def test_narrated_video_warns_for_missing_bed_unless_waived(self):
        base = {'format': 'gravacao'}
        self.assertTrue(any('cama sonora' in w for w in review.manifest_checks(self.proj, base, False)))
        for change in ({'music': {'bed_waiver': 'Demonstração só com voz, opção editorial'}},
                       {'assets': [{'path': 'audio/ambiente.wav', 'kind': 'audio'}]}):
            self.assertFalse(any('cama sonora' in w for w in review.manifest_checks(self.proj, {**base, **change}, False)))

    def test_shot_and_rhythm_limits_match_long_format(self):
        manifest = {'aspect': '16:9', 'scenes': [{'id': 's1', 'start': 0, 'duration': 10,
                                                'visual': {'shots': [{}]}}]}
        self.assertTrue(any('por plano' in w for w in review.manifest_checks(self.proj, manifest, False)))
        self.assertFalse(any('por plano' in w for w in review.manifest_checks(self.proj, manifest, True)))
        self.assertIn('15 s', dict(review.rubric_for(manifest, 71))['Ritmo'])


if __name__ == "__main__":
    unittest.main()
