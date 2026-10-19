# Microsoft Store掲載文｜Excel / CSV Privacy Cleaner｜レビュー準備稿
対象ブランチ: `ui/safe-product-upgrade-20261019`
状態: **文案完成 / 公開未承認 / Store ID・価格の実入力未済**
価格の仮設定: **¥2,480（仮）**。正式価格・対応市場は権限のある販売者が承認し、Partner Centerで指定する。

## ja-JP
**製品名（候補）:** Excel / CSV Privacy Cleaner

**短い説明:**
CSVやExcelの指定列を選んでマスク・仮名化・削除し、元ファイルとは別に処理コピーを保存します。

**詳細説明（そのまま編集欄へ転記可能）:**
顧客名簿の共有や検証データの作成に向けて、CSV・XLSXの列をチェック方式で選び、マスク・仮名化・削除を実行します。加工前後のプレビューと保存前の確認があり、元のファイルと既存の出力ファイルは上書きしません。

・CSV・XLSXから加工したい列を選択
・マスク・仮名化・列削除の3方式
・プレビューと新規出力、危険な入力の拒否

**対応範囲と重要な注意事項:**
仮名化は完全な匿名化ではありません。非表示データ、式、図・画像、外部リンクなどのすべてを消去する機能ではなく、複雑なXLSXは安全のため出力を拒否します。XLSMは非対応です。

**What's new:** 初回提出時は空欄。製品更新の場合のみ新旧の違いを事実確認して記載。

## en-US
**Suggested title:** Excel / CSV Privacy Cleaner

**Short description:**
Choose columns in CSV or Excel, mask, pseudonymize or remove values, and save a separate local copy.

**Full description:**
Prepare selected columns in CSV and XLSX files for sharing or testing. Choose columns, select Mask, Pseudonymize or Remove, review a preview, and save a new copy without overwriting the source. Files with structures that cannot be handled safely may be rejected.

• Select the CSV/XLSX columns to process
• Mask, pseudonymize, or remove selected columns
• Preview changes and save a separate copy

**Important limitations:**
Pseudonymization is not guaranteed anonymization. The app does not detect or remove all sensitive data, formulas, images, hidden content or external references. Complex XLSX structures may be refused. XLSM is unsupported.

**What's new:** Leave blank for the initial submission.

## Partner Center 編集チェック
- 描写の対象は各製品の現行ブランチで**実装が確認できる機能のみ**。未知の機能や完全安全保証を足さない。
- 正式名の重複確認、年齢区分質問票、価格、カテゴリ、地域、検索キーワード、機能欄は提出画面で設定する。価格は購入実績の裏付けがない仮説。
- スクリーンショットは実機撮影5枚。本文に外部URL、HTML、未確認の商標や第三者との提携表現を入れない。
- 最終チェック: ユーザー向けの日本語/英語を実画面と照合。英語UIが未合格なら対応言語を無理に追加しない。
- ソースWindows QA、MSIX、Store Identity、プライバシー・サポート情報、ライセンス承認が揃うまで掲載しない。

公式: https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/add-and-edit-store-listing-info
