import tempfile
import unittest
from pathlib import Path

from novel_engine.profile import load_profile
from novel_engine.quality.txt_format import check_txt

PROFILE = load_profile()


def write(text: str) -> Path:
    tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return Path(tmp.name)


class TxtFormatTest(unittest.TestCase):
    def test_clean_short_chapter_ok(self):
        path = write("第一章 烟火\n\n他推开门。\n院里灯还亮着。\n墙外脚步停了下来。\n")
        errors, _ = check_txt(path, PROFILE)
        self.assertEqual(errors, [])

    def test_bad_title_flagged(self):
        path = write("烟火\n\n他推开门。\n院里灯还亮着。\n墙外脚步停了下来。\n")
        errors, _ = check_txt(path, PROFILE)
        self.assertTrue(any("TITLE_FORMAT" in e for e in errors))

    def test_blank_body_lines_flagged(self):
        path = write("第一章 烟火\n\n他推开门。\n\n院里灯还亮着。\n")
        errors, _ = check_txt(path, PROFILE)
        self.assertTrue(any("TXT_BLANK_LINES" in e for e in errors))

    def test_giant_paragraph_flagged(self):
        big = "字" * 240
        path = write(f"第一章 烟火\n\n他推开门。\n{big}\n墙外脚步停了下来。\n")
        errors, _ = check_txt(path, PROFILE)
        self.assertTrue(any("GIANT_PARAGRAPH" in e for e in errors))

    def test_low_density_warns_for_long_chapter(self):
        # One ~2000-char paragraph: over the normal threshold but only 1 paragraph.
        body = "他走过长廊，" * 350
        path = write(f"第一章 烟火\n\n{body}\n")
        errors, warnings = check_txt(path, PROFILE, chapter_function="face_slap")
        # giant-paragraph error fires too; the density/long warnings should be present.
        self.assertTrue(any("LOW_PARAGRAPH_DENSITY" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
