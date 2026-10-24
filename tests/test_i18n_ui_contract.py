from pathlib import Path
import unittest

import i18n

ROOT = Path(__file__).resolve().parents[1]
UI_FILE = ROOT / "windows_app.py"
SOURCE = "① Choose file  →  ② Select columns  →  ③ Pick a method  →  ④ Preview  →  ⑤ Save a new copy"
ENGLISH = "① Choose file  →  ② Select columns  →  ③ Pick a method  →  ④ Preview  →  ⑤ Save a new copy"
JAPANESE = "① ファイル選択  →  ② 列を選択  →  ③ 処理方法  →  ④ プレビュー  →  ⑤ 新しいコピーを保存"


class I18nUiContractTests(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("en")

    def test_guide_switches_both_languages(self):
        i18n.set_language("en")
        self.assertEqual(i18n.translate(SOURCE), ENGLISH)
        i18n.set_language("ja")
        self.assertEqual(i18n.translate(SOURCE), JAPANESE)

    def test_ui_installs_visible_language_switch(self):
        ui = UI_FILE.read_text(encoding="utf-8")
        helper = (ROOT / "i18n.py").read_text(encoding="utf-8")
        self.assertIn("install_bilingual_ui", ui)
        self.assertIn("Language / 言語", helper)


if __name__ == "__main__":
    unittest.main()
