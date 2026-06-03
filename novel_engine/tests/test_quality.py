import unittest

from novel_engine.contracts import validate_editor_verdict, validate_scene_spec
from novel_engine.profile import load_profile
from novel_engine.quality import prose_metrics, prose_patterns

PROFILE = load_profile()


class ProsePatternsTest(unittest.TestCase):
    def test_not_but_within_limit_is_clean(self):
        text = "他没有回头，而是径直走进雨里。剩下的句子都是直接的动作和对话。"
        errors, _ = prose_patterns.evaluate(text, PROFILE)
        self.assertEqual(errors, [])

    def test_not_but_over_limit_errors(self):
        text = "这不是结束，而是开始。那不是恐惧，而是期待。它不是巧合，而是安排。"
        errors, _ = prose_patterns.evaluate(text, PROFILE)
        self.assertTrue(any("OVERUSED_NOT_BUT_PATTERN" in e for e in errors))

    def test_meta_original_text_is_hard_error(self):
        text = "原书中他本该死去，但这里活了下来。"
        errors, _ = prose_patterns.evaluate(text, PROFILE)
        self.assertTrue(any("META_ORIGINAL_TEXT" in e for e in errors))

    def test_scan_reports_counts(self):
        text = "这不是结束，而是开始。"
        hits = {h.key: h.count for h in prose_patterns.scan(text, PROFILE)}
        self.assertEqual(hits.get("contrast_negation"), 1)


class ProseMetricsTest(unittest.TestCase):
    def test_fingerprint_basic(self):
        text = "他推开门。院里灯还亮着。\n“谁在那儿？”他低声问。"
        fp = prose_metrics.fingerprint(text)
        self.assertEqual(fp["paragraph_count"], 2)
        self.assertGreater(fp["sentence_count"], 0)
        self.assertGreater(fp["dialogue_ratio"], 0)

    def test_identical_texts_zero_divergence(self):
        text = "他推开门。院里灯还亮着，雨水顺着屋檐落下来，敲在青石板上。"
        result = prose_metrics.compare(text, text)
        self.assertEqual(result["divergence_score"], 0.0)

    def test_different_rhythm_diverges(self):
        terse = "他走。门开。雨落。人来。"
        flowing = "他缓缓走过长长的回廊，推开那扇沉重的木门，外面的雨正绵密地落在石阶上，没有要停的意思。"
        result = prose_metrics.compare(terse, flowing)
        self.assertGreater(result["divergence_score"], 0.2)


class ContractTest(unittest.TestCase):
    def test_valid_scene_spec(self):
        spec = {
            "id": "ch012_s02",
            "pov": "林栖",
            "emotional_temperature": {"from": "松弛", "to": "警觉"},
            "sensory_anchor": "灯油味和潮湿的石墙",
            "exit_on": "墙外脚步停下",
            "one_change": "",
        }
        self.assertEqual(validate_scene_spec(spec), [])

    def test_scene_spec_requires_experiential_fields(self):
        spec = {"id": "s1", "pov": "x", "one_change": "拿到道具"}
        problems = validate_scene_spec(spec)
        self.assertTrue(any("emotional_temperature" in p for p in problems))
        self.assertTrue(any("sensory_anchor" in p for p in problems))
        self.assertTrue(any("exit_on" in p for p in problems))

    def test_valid_editor_verdict(self):
        verdict = {
            "verdict": "revise",
            "reader": "cold_reader_subagent",
            "blockers": [{"where": "第三段", "severity": "high", "why": "断句机械"}],
        }
        self.assertEqual(validate_editor_verdict(verdict), [])

    def test_editor_verdict_bad_enum(self):
        self.assertTrue(validate_editor_verdict({"verdict": "maybe"}))


if __name__ == "__main__":
    unittest.main()
