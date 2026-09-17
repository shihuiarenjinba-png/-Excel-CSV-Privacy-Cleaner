# Excel / CSV Privacy Cleaner

CSV・ExcelをAIや外部会社へ渡す前に、**列・セル構造を使って決定的に削除・マスキング・仮名化する専用Sanitizer**として設計します。

## 専門方針

画像OCRや曖昧なAI判定には依存せず、表形式データだからこそできる高精度処理に集中します。

- 列名ルール: 氏名 / email / phone / customer_id / address / api_key等
- 型・正規表現ルール: email / 電話 / UUID / token候補
- allowlist方式: 外部へ残してよい列だけを明示
- denylist方式: 削除 / mask / pseudonymize対象を明示
- 固定仮名化: HMAC-SHA256等で同じ入力を同じ仮名へ変換可能
- mapping fileを作らないモードを優先し、復元表の漏えいを避ける
- hidden / veryHidden sheet、コメント、Defined Name、外部リンク、数式を別監査
- 元ファイル非変更、新規sanitized copyのみ生成
- Before/After SHA256、処理ルール、件数をaudit reportへ保存

## Excelで特に注意するもの

見えているセル値だけ削除しても、以下に情報が残る可能性があります。

- hidden / veryHidden sheets
- cell comments / notes
- formulas内の文字列・参照
- external workbook links
- defined names
- document properties / metadata
- embedded objects / charts / images
- VBA / macros (XLSM)

販売版では「検査できた領域」と「検査できない領域」を分離し、未検査要素があるファイルを自動で「安全」と判定しません。XLSMや埋め込みobjectは別途Review/Block対象とします。

## 出力モード

1. **Allowlist Export** — 指定列だけ新規CSV/XLSXへ書き出す。最も安全。
2. **Rule Sanitization** — 指定列を削除・mask・HMAC仮名化。
3. **Audit Only** — 元ファイルを変更せず、外部共有前の要確認箇所だけ一覧化。

## 販売上の約束

「個人情報を完全自動検出する」「100%安全化する」とは表現しません。構造化データに対して、**明示ルールを確実に適用し、何を処理したか追跡できること**を価値にします。
