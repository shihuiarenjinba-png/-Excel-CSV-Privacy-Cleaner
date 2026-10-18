from __future__ import annotations

import locale
import os
import tkinter as tk
from tkinter import filedialog, messagebox

_LANGUAGE = "ja" if any((x or "").lower().startswith("ja") for x in (locale.getlocale()[0], os.environ.get("LANG"))) else "en"
_CONTROLLERS = []
_PATCHED = False

TEXTS = {
    "Excel / CSV Privacy Cleaner": ("Excel / CSV Privacy Cleaner", "Excel / CSVプライバシークリーナー"),
    "Select file → check columns → choose method → preview → export a new copy.": ("Select file → check columns → choose method → preview → export a new copy.", "ファイル選択 → 列をチェック → 処理方法 → プレビュー → 新しいコピーを出力"),
    "1  Choose file": ("1  Choose file", "1  ファイルを選択"),
    "2  Check the columns to process (none selected by default)": ("2  Check the columns to process (none selected by default)", "2  処理する列にチェック（初期状態は未選択）"),
    "3  Processing method:": ("3  Processing method:", "3  処理方法:"),
    "Mask (hide values)": ("Mask (hide values)", "マスク（値を隠す）"),
    "Pseudonymize (ID)": ("Pseudonymize (ID)", "仮名化（ID変換）"),
    "Drop (remove columns)": ("Drop (remove columns)", "削除（列を消す）"),
    "4  Preview": ("4  Preview", "4  プレビュー"),
    "5  Export copy": ("5  Export copy", "5  コピーを出力"),
    "Advanced options": ("Advanced options", "詳細設定"),
    "Show pseudonym key": ("Show pseudonym key", "仮名化キーを表示"),
    "mask: partly hide | pseudonymize: ID | drop: remove": ("mask: partly hide | pseudonymize: ID | drop: remove", "mask: 一部を隠す | pseudonymize: 仮名ID | drop: 列削除"),
    "Pseudonym key (keep private; use same key for consistent IDs):": ("Pseudonym key (keep private; use same key for consistent IDs):", "仮名化キー（秘密に保管。同じID対応には同じキーが必要）:"),
    "Preview and processing results (example rows; verify exported file yourself):": ("Preview and processing results (example rows; verify exported file yourself):", "プレビュー・処理結果（例示。出力ファイルは自身で確認してください）:"),
    "No columns selected": ("No columns selected", "処理列が未選択"),
    "Export complete": ("Export complete", "出力完了"),
    "Review export": ("Review export", "出力内容を確認"),

    "Excel / CSV Privacy Cleaner — Windows": ("Excel / CSV Privacy Cleaner — Windows", "Excel / CSVプライバシークリーナー — Windows"),
    "Privacy Cleaner": ("Privacy Cleaner", "プライバシークリーナー"),
    "Create a safer copy locally. Original files are never overwritten.": ("Create a safer copy locally. Original files are never overwritten.", "ローカルで安全化したコピーを作成します。元ファイルは上書きしません。"),
    "Choose CSV/XLSX": ("Choose CSV/XLSX", "CSV/XLSXを選択"),
    "Export safer copy": ("Export safer copy", "安全化コピーを出力"),
    "Columns to process (comma separated; blank = all columns):": ("Columns to process (comma separated; blank = all columns):", "処理する列（カンマ区切り、空欄=全列）:"),
    "Mode: mask / pseudonymize / drop": ("Mode: mask / pseudonymize / drop", "モード: mask / pseudonymize / drop"),
    "Pseudonym salt (keep stable if you need consistent IDs):": ("Pseudonym salt (keep stable if you need consistent IDs):", "仮名化ソルト（同じID対応が必要なら固定してください）:"),
    "Remove hidden worksheets (XLSX)": ("Remove hidden worksheets (XLSX)", "非表示ワークシートを削除 (XLSX)"),
    "Remove cell comments (XLSX)": ("Remove cell comments (XLSX)", "セルコメントを削除 (XLSX)"),
    "Choose CSV or XLSX": ("Choose CSV or XLSX", "CSVまたはXLSXを選択"),
    "Choose a file first.": ("Choose a file first.", "先にファイルを選択してください。"),
    "Mode must be mask, pseudonymize, or drop.": ("Mode must be mask, pseudonymize, or drop.", "モードは mask、pseudonymize、drop のいずれかにしてください。"),
    "Only CSV and XLSX are supported.": ("Only CSV and XLSX are supported.", "CSVとXLSXのみ対応しています。"),
    "Data files": ("Data files", "データファイル"), "Output": ("Output", "出力"), "Excel": ("Excel", "Excel"), "CSV": ("CSV", "CSV"),
}

PHRASES = (
    ("Unsupported or undecodable CSV encoding", "未対応またはデコード不能なCSV文字コード"),
    ("Decoded text contains NUL bytes and appears binary.", "デコード結果にNUL文字が含まれ、バイナリデータの可能性があります。"),
    ("Decoded text contains too many control characters and appears binary.", "制御文字が多すぎるため、バイナリデータの可能性があります。"),
    ("CSV header row is missing or could not be parsed.", "CSVヘッダー行がないか解析できません。"),
    ("contains a blank header", "空のヘッダーを含んでいます"),
    ("Duplicate CSV header", "CSVヘッダーが重複しています"),
    ("Duplicate worksheet", "ワークシートのヘッダーが重複しています"),
    ("has more fields than the header", "ヘッダーより多いフィールドがあります"),
    ("Refusing ambiguous input", "曖昧な入力のため処理を拒否しました"),
    ("Requested column(s) not found", "指定列が見つかりません"),
    ("Refusing to drop every CSV column.", "CSVの全列削除は拒否しました。"),
    ("is missing requested column(s)", "に指定列がありません"),
    ("Refusing to drop every column", "全列削除は拒否しました"),
    ("All worksheets would be removed. Keep at least one visible sheet.", "すべてのワークシートが削除対象です。少なくとも1つ表示シートを残してください。"),
    ("Refusing to overwrite the input file", "入力ファイルの上書きを拒否しました"),
    ("Select an input file.", "入力ファイルを選択してください。"),
    ("Check one or more column names.", "処理する列を1つ以上チェックしてください。"),
    ("Other columns and workbook content may still contain personal data.", "未選択列やブック内に個人情報が残る可能性があります。"),
    ("Workbook formulas and hidden structures are not comprehensively certified.", "数式や隠し構造の完全な安全性は保証されません。"),
    ("Continue to choose a NEW output file?", "新しい出力ファイルを指定して続行しますか？"),
    ("Choose a new output filename; existing files are never replaced.", "新しいファイル名を指定してください。既存のファイルは上書きしません。"),
    ("New copy created. Check the final output before sharing.", "新しいコピーを作成しました。共有前に出力結果を確認してください。"),
    ("Select file", "ファイル選択"), ("Preview", "プレビュー"),
    ("Selected:", "選択ファイル:"), ("Loaded", "読み込んだ列数"),
    ("SAVED", "保存済み"),
    ("Safer copy saved:", "安全化コピーを保存しました:"),
    ("ERROR", "エラー"),
)


def get_language() -> str:
    return _LANGUAGE


def translate(text):
    if not isinstance(text, str): return text
    if text in TEXTS: return TEXTS[text][1 if _LANGUAGE == "ja" else 0]
    if _LANGUAGE == "ja":
        for en, ja in PHRASES: text = text.replace(en, ja)
    return text


def set_language(lang: str):
    global _LANGUAGE
    if lang not in {"en", "ja"}: raise ValueError("language must be 'en' or 'ja'")
    _LANGUAGE = lang
    for c in tuple(_CONTROLLERS): c.refresh()


def _patch():
    global _PATCHED
    if _PATCHED: return
    _PATCHED = True
    original_insert = tk.Listbox.insert
    tk.Listbox.insert = lambda self, index, *items: original_insert(self, index, *(translate(x) for x in items))
    for name in ("showinfo", "showwarning", "showerror", "askokcancel"):
        original = getattr(messagebox, name)
        setattr(messagebox, name, lambda title, message, *a, _f=original, **k: _f(translate(title), translate(message), *a, **k))
    for name in ("askopenfilename", "askopenfilenames", "asksaveasfilename", "askdirectory"):
        original = getattr(filedialog, name)
        def wrapper(*a, _f=original, **k):
            if "title" in k: k["title"] = translate(k["title"])
            if "filetypes" in k: k["filetypes"] = [(translate(label), pattern) for label, pattern in k["filetypes"]]
            return _f(*a, **k)
        setattr(filedialog, name, wrapper)


class LanguageController:
    def __init__(self, root):
        self.root=root; self.original_title=root.title(); self._snapshot(root)
        f=tk.Frame(root,padx=12,pady=6); f.pack(fill="x"); self.button=tk.Button(f,width=12,command=self.toggle); self.button.pack(side="right")
        _CONTROLLERS.append(self); self.refresh()
    def _snapshot(self,w):
        try: w._i18n_original_text=w.cget("text")
        except Exception: pass
        for c in w.winfo_children(): self._snapshot(c)
    def _refresh(self,w):
        if w is not self.button and hasattr(w,"_i18n_original_text"):
            try: w.configure(text=translate(w._i18n_original_text))
            except Exception: pass
        for c in w.winfo_children(): self._refresh(c)
    def refresh(self):
        self.root.title(translate(self.original_title)); self._refresh(self.root); self.button.configure(text="English" if _LANGUAGE=="ja" else "日本語")
    def toggle(self): set_language("en" if _LANGUAGE=="ja" else "ja")


def install_bilingual_ui(root):
    _patch(); return LanguageController(root)
