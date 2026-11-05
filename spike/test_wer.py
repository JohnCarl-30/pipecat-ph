import unittest

from score import report
from wer import errors, normalize, wer


class WerTest(unittest.TestCase):
    def test_exact_match_ignores_case_punctuation_and_hyphens(self):
        self.assertEqual(wer("Pwede po bang mag-walk in?", "pwede po bang magwalk in"), 0)

    def test_counts_substitution_deletion_and_insertion(self):
        self.assertEqual(errors("open po ba kayo", "open ba kayo bukas"), (2, 4))
        self.assertEqual(errors("magkano po", "magkano pa"), (1, 2))

    def test_empty_hypothesis_is_all_deletions(self):
        self.assertEqual(wer("salamat po", ""), 1)

    def test_normalize_keeps_taglish_words(self):
        self.assertEqual(normalize("Na-receive niyo na po?"), ["nareceive", "niyo", "na", "po"])


class ReportTest(unittest.TestCase):
    def test_pools_errors_over_words_and_skips_missing_clips(self):
        prompts = {"01": "open po ba kayo", "02": "salamat po"}
        out = report(prompts, {"deepgram": {"01": "open ba kayo", "02": "salamat po"}, "whisper": {"02": "salamat"}})
        self.assertIn("| deepgram | 2/2 | 16.7% | 1 |", out)
        self.assertIn("| whisper | 1/2 | 50.0% | 0 |", out)
        self.assertIn("| 01 | deepgram | 1 | open ba kayo |", out)


if __name__ == "__main__":
    unittest.main()
