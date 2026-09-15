import i18n

original = getattr(i18n, "get_language", lambda: getattr(i18n, "_LANGUAGE", "en"))()
try:
    i18n.set_language("ja")
    assert i18n.translate("Choose CSV/XLSX") == "CSV/XLSXを選択"
    assert i18n.translate("Export safer copy") == "安全化コピーを出力"
    i18n.set_language("en")
    assert i18n.translate("Choose CSV/XLSX") == "Choose CSV/XLSX"
    assert i18n.translate("Export safer copy") == "Export safer copy"
finally:
    i18n.set_language(original)

print("Excel CSV Privacy Cleaner bilingual UI smoke test: OK")
