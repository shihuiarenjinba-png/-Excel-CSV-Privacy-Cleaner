# 第1工程：Microsoft Store商品枠の作成前に必要な品質判定

2026-10-18 / 対象: Excel / CSV Privacy Cleaner
ブランチ: `improve/simple-column-ui-20261018`

## 今回のコード側の追加・修正（実装済み、テスト実行は未証明）
- CSVの見出しに前後の空白があっても、プレビュー・列チェック・加工結果の対応を一致させる。
- 最大25MiBのCSVは、行全体の辞書を蓄積せず、同じデコード済み入力の全行を事前検証してから新規出力する。
- CSVの数式に見えるセルは未選択列・遅い行も含めて出力前に拒否。
- 出力後のCSVを再度開き、全行・全列の値を比較し、誤りがあれば新規出力を消す。
- 処理方法は「マスク」「仮名化」「列削除」の独立したラジオ選択肢にし、日英表示を対応。
- 破損したファイルへ切り替えた場合、過去の選択を残さず誤出力を防止。
- 重要な追加テスト: `tests/test_csv_integrity_streaming.py`、GUI操作は `gui_smoke_test.py`。

## Windows上での初回自動試験

Windows検証用フォルダーへのcloneとQAスクリプトの実行はユーザー側で成功し、「LOCAL TESTS PASS ONLY」と報告された。ただし、これは**当時のコミット**の結果であり、本書の作成後に仮名化方式・出力拒否条件などを改善した**最新のコードの試験合格とはみなさない**。最新コードを `git pull --ff-only` で更新した後、`store/verify-and-build.ps1` で新しいコミットの自動試験を再実行し、PASSのときだけ独立フォルダーに候補EXEを作る。

## 最新のWindowsテスト失敗（2026-10-18）

以前のコミットではユーザー側のWindows実行がPASSしたが、コミット `5401a6e70af99000c404bdaf79b0480f4c22bf71` の `store/verify-and-build.ps1` はQA段階で停止し、検証用EXEは作成されなかった。**原本のtests.logはユーザーのPCだけに存在するため、テスト失敗の正確な一覧はまだ不明。** 少なくとも実装上、数式セル全体の仮名化を拒否する条件と既存の回帰テストの間に矛盾があり、改良ブランチに修正した。追跡: [Issue #3](https://github.com/shihuiarenjinba-png/-Excel-CSV-Privacy-Cleaner/issues/3)。

その後のコードは未実行のため **登録HOLD**。次のWindows実行では、更新後の`run-windows-qa.ps1`が不合格テスト名とログ末尾を画面に表示する。詳細は合成データのテスト例外だけを共有し、個人情報は共有しない。

## 最新のローカル検証結果（2026-10-18）
ユーザー提供の実行結果では、コード `5a11d5e50eed856a8948966a9e0886248b58c615` のWindows QAが完了し、`PORTABLE CANDIDATE COMPLETE FOR QA` と表示された。EXEの報告されたSHA256は `9a81e3a7deb5d8048cde49b164bf0596344469644a1e12c57a06281fc6010962`。このため、**当該ソースの自動テストおよび署名前の候補EXE生成はPASS（ユーザー実行報告）**として扱う。GitHub上では現物EXE/ローカルテストログを取得していないので、EXEの独立ハッシュ照合、GUI手動受入、ランタイム通信、第三者ライセンスは**未確認**のまま。販売/商品登録判断: **HOLD**。

詳細: [PORTABLE_CANDIDATE_ACCEPTANCE_20261018.md](PORTABLE_CANDIDATE_ACCEPTANCE_20261018.md)。改良ブランチの後続ドキュメント追加コミットは元候補EXEのバイト列を変えない。テスト証拠は**ソースSHAで紐づけて**保持し、異なるソースコードを作り直した場合は再試験が必要。

## 登録可能にするための残りの仕事

| ゲート | 必要な実行証拠 | 現在 |
|---|---|---|
| 機能テスト | 元のsmoke、全unittest、GUI自動操作のPASSログ、正確なSHA | 未確認 |
| 異常系・ストレス | 数式注入、途中行エラー、破損XLSX、文字コード、データ量上限、原本不変、出力の再読込 | 未確認 |
| 実機GUI | Windows 10/11、日英、DPI100/125/150%、キーボード、初見操作 | 未確認 |
| ローカル処理 | 最終実行バイナリのネットワーク送信・ログ・一時ファイル監査 | 未確認 |
| 再配布権利 | Python・openpyxl等のライセンス/SBOM、アプリ独自の権利・表示 | 未確認 |
| 商業性 | 無料競合との差、想定顧客・買い切り価格の合理性、利用者の購入意向 | 仮説作成、未検証 |

**2026-10-18判定: 登録HOLD。** この文書はQA実行証拠ではない。

## Windowsの実行手順
対象ブランチをクリーンにcheckoutして、Windows PowerShellで:

```powershell
git rev-parse HEAD
powershell -NoProfile -ExecutionPolicy Bypass -File .\store\run-windows-qa.ps1
```

作業用ブランチから実行する場合は `-ExpectedBranch '実際のブランチ名'` を追加。元ブランチのSHAとの関係を確認し、変更内容と証拠をコミットする。検証スクリプトはローカルテストPASSのみを記録し、実機目視・MSIX・Store認定は自動でPASSにはしない。

テスト後に `store/evidence.template.json` を元に、リポジトリ外のローカルな専用証拠フォルダー内で実際の証拠マニフェストを作り、対象SHA、各項目の根拠ファイルの相対パスとSHA256を記入する。`store/GETTING_STARTED_WINDOWS.md`を参照し、個人情報を含む可能性があるログをGitHubにコミットしない。製品データは添付しない。証拠が確定したら:

```powershell
py -3 .\store\release_gate.py --stage registration --evidence .\store\actual-evidence.json
```

このコマンドは `functional_tests`、`human_gui`、`hostile_fixtures`、`privacy_egress`、`dependencies_license` の5項目を照合する。**すべてが揃っても自動登録・販売承認はしない**。実際の購入価値、商品名の権利・予約期間、提出時期を最終判断する。

## 第1工程から第2工程への移行
上記5項目が実行済みで問題なく、単品で購入理由が説明できれば、Partner Centerに **Excel / CSV Privacy Cleaner** の商品枠を作成してよい。

商品枠が作成された後は正式 `Package Identity Name` と `Publisher` を利用してMSIXを作成し、実機でインストール・起動・更新・アンインストールを確認し、正式にStore認定を受ける。MSIXや認定は第1工程完了の前提ではない。

## 今回追加の商用品質対策（再テスト必須）
- 数式参照を壊す列削除、数式依存の検証ができないマスク・仮名化、結合セル・Excelテーブル・画像・グラフ・ピボットを含む複雑なブックはプレビュー時から拒否する。
- CSVの空欄の仮名ID生成を停止し、空欄のまま保存する。
- `tests/test_xlsx_complex_workbook.py` と `tests/test_csv_integrity_streaming.py` の追加テストを実行すること。以前のWindows自動テストPASSは改良前のコミットであり、最新の品質証拠には使わない。
- 登録前に利用者が複雑Excelの制限を理解できるよう、商品説明を更新した。

## 重大な未検証リスク
- Excelの数式、参照、画像、チャート、外部リンク、非表示内容を含む複雑なブックでのデータ完全性は未証明。
- CSVの変換・3段階の検証は最大25MiBのデータで時間がかかる場合があり、GUIの応答性・進捗表示を実機で確認すること。
- プレビューは少数行であって完全なプライバシー監査ではない。
- 競合価格比較と980円の案は売上見込みを証明しない。

既存main・既存配布物の上書き禁止。すべて独立改良ブランチ上で進める。
