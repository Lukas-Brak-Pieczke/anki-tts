import unittest
from anki_tts.text_cleaner import clean_text_for_tts
from anki_tts.tts_engine import get_audio_filename

class TestAnkiTTS(unittest.TestCase):

    def test_single_word_cleaning(self):
        self.assertEqual(clean_text_for_tts("<b>tammikuu</b>"), "tammikuu")

    def test_html_and_sentence_cleaning(self):
        raw = "Lapsi lukee kirjaa.<br>Hän on iloinen.<p>Se on hyvä kirja.</p>"
        expected = "Lapsi lukee kirjaa. Hän on iloinen. Se on hyvä kirja."
        self.assertEqual(clean_text_for_tts(raw), expected)

    def test_sound_tag_removal(self):
        raw = "koira [sound:tts_123456.mp3]"
        self.assertEqual(clean_text_for_tts(raw), "koira")

    def test_entity_decoding(self):
        raw = "Päivää&nbsp;&amp;&nbsp;näkemiin"
        self.assertEqual(clean_text_for_tts(raw), "Päivää & näkemiin")

    def test_filename_hashing_consistency(self):
        f1 = get_audio_filename("tammikuu", "fi-FI-HarriNeural")
        f2 = get_audio_filename("tammikuu", "fi-FI-HarriNeural")
        f3 = get_audio_filename("tammikuu", "fi-FI-SelmaNeural")
        
        self.assertEqual(f1, f2)
        self.assertNotEqual(f1, f3)
        self.assertTrue(f1.startswith("tts_"))
        self.assertTrue(f1.endswith(".mp3"))

if __name__ == "__main__":
    unittest.main()
