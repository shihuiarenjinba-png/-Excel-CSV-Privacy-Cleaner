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
    "Privacy Cleaner": ("Privacy Cleaner", "プライバシークリーナー"),
    "Create a safer copy locally. Original files are never overwritten.": ("Create a safer copy locally. Original files are never overwritten.", "ローカルで安全化したコピーを作成します。元ファイルは上書きしません。"),
    "Choose CSV/XLSX": ("Choose CSV/XLSX", "CSV/XLSXを選択"), "Export safer copy": ("Export safer copy", "安全化コピーを出力"),
    "Columns to process (comma separated; blank = all columns):": ("Columns to process (comma separated; blank = all columns):", "処理する列（カンマ区切り、空欄=全列）:"),
    "Mode: mask / pseudonymize / drop": ("Mode: mask / pseudonymize / drop", "モード: mask / pseudonymize / drop"),
    "Pseudonym salt (keep stable if you need consistent IDs):": ("Pseudonym salt (keep stable if you need consistent IDs):", "仮名化ソルト（同じID対応が必要なら固定してください）:"),
    "Remove hidden worksheets (XLSX)": ("Remove hidden worksheets (XLSX)", "非表示ワークシートを削除 (XLSX)"),
    "Remove cell comments (XLSX)": ("Remove cell comments (XLSX)", "セルコメントを削除 (XLSX)"),
    "Choose CSV or XLSX": ("Choose CSV or XLSX", "CSVまたはXLSXを選択"), "Choose a file first.": ("Choose a file first.", "先にファイルを選択してください。"),
    "Mode must be mask, pseudonymize, or drop.": ("Mode must be mask, pseudonymize, or drop.", "モードは mask、pseudonymize、drop のいずれかにしてください。"),
    "Only CSV and XLSX are supported.": ("Only CSV and XLSX are supported.", "CSVとXLSXのみ対応しています。"),
}
PHRASES = (("Unsupported or undecodable CSV encoding", "未対応またはデコード不能なCSV文字コード"), ("CSV header row is missing or could not be parsed.", "CSVヘッダー行がないか解析できません。"), ("Requested column(s) not found", "指定列が見つかりません"), ("Refusing to drop every CSV column.", "CSVの全列削除は拒否しました。"), ("is missing requested column(s)", "に指定列がありません"), ("Refusing to drop every column", "全列削除は拒否しました"), ("All worksheets would be removed. Keep at least one visible sheet.", "すべてのワークシートが削除対象です。少なくとも1つ表示シートを残してください。"), ("SAVED", "保存済み"), ("Safer copy saved:", "安全化コピーを保存しました:"), ("ERROR", "エラー"))

def translate(text):
    if not isinstance(text, str): return text
    if text in TEXTS: return TEXTS[text][1 if _LANGUAGE == "ja" else 0]
    if _LANGUAGE == "ja":
        for en, ja in PHRASES: text = text.replace(en, ja)
    return text

def set_language(lang):
    global _LANGUAGE; _LANGUAGE = lang
    for c in tuple(_CONTROLLERS): c.refresh()

def _patch():
    global _PATCHED
    if _PATCHED: return
    _PATCHED = True
    oi = tk.Listbox.insert
    tk.Listbox.insert = lambda self, index, *items: oi(self, index, *(translate(x) for x in items))
    for name in ("showinfo", "showwarning", "showerror"):
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
