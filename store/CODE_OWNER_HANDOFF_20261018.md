# コード担当への引き継ぎ — Windows実機検証からMicrosoft Store商用品質へ

**引き継ぎ日: 2026-10-18**
**目的: Windows向け買い切り有料販売の最初の1商品を完成させる。**
作業対象: `shihuiarenjinba-png/-Excel-CSV-Privacy-Cleaner`
改良ブランチ: `improve/simple-column-ui-20261018`

## 厳守事項
- `main` と過去のリリース・MSIX・監査記録・顧客データを上書きしない。
- 作業は対象改良ブランチからさらに検証ブランチを切って行い、修正・テスト・証拠をコミットする。既存mainへのマージは明示的な承認を得た後のみ。
- GitHubのソースが正。本体のWindows依存作業、仮想環境、EXE/MSIX作成、インストールは担当PCで行う。
- 個人データをGitHub、ログ、スクリーンショット、アーティファクトへアップロードしない。テストは合成データのみ。
- すべての機能を簡単に使えることを優先。「ファイルを選択 → 列をチェック → 処理方法 → プレビュー → 新規コピー保存」を維持し、詳細設定は隠しておく。
- 本ツールは全個人情報の完全除去・法的認証・完全匿名化を保証しない。

## P0 — 実際のテストを走らせ、バグを修正
1. リモート最新の `improve/simple-column-ui-20261018` を取得、コミットSHAを固定し、改良元の `windows-mvp-20260915` と差分確認。
2. GitHub Actionsがチェックアウト以前に止まる問題を確認（Issue #2）。課金・上限・Runner割当・GitHub Statusを調査。原因が不明ならWindows PCで検証を実行してHOLDと明記する。
3. Windows PowerShellで以下を実行する。
```powershell
git status --short
git rev-parse HEAD
powershell -NoProfile -ExecutionPolicy Bypass -File .\store\run-windows-qa.ps1
```
別の検証ブランチで検証する場合は、上記の実行時に `-ExpectedBranch 'そのブランチ名'` を指定し、改良ブランチから派生したことを `git merge-base` 等で検証する。
結果のJSON・ログSHA・実行時コミットSHAを保存し、失敗した項目を再現・修正。成功が確認できないテストをPASSと書かない。
4. CSVのCP932/UTF-8/UTF-16、引用符・改行、重複列、数式注入の全パターン、XLSXの数式・非表示シート・コメント・外部リンク・破損・大容量、入力/出力不変性、例外処理を再検証する。今回の追加制限: CSV 25MiB、XLSX 15MiB、展開160MiB、最大10万行/シート。
5. GUIで「壊れたファイルを選んだ後に前のファイルが残らない」「列選択の文字が見える」「未選択列の誤加工なし」「例示プレビューを完全監査と誤認しない」を確認する。
6. Windows 10/11、DPI 100/125/150%、日英切替、アクセシビリティ、キーボード操作、長いパス、日本語ファイル名で実機確認する。初見利用者が使えるか、合成データで記録する。

## P1 — 販売版MSIXとStore登録前確認
1. `store/README.md`, `store/build-store-msix.ps1`, `store/evidence.template.json`, `SALES_RELEASE_CHECKLIST.md` を確認。
2. 正しいPartner Center商品名、`Identity.Name`、`Publisher CN`、PublisherDisplayName、アプリアイコン、プライバシーポリシーURLとサポートURLを**実際の登録情報から確認**する。値が未確定なら勝手に埋めずにHOLD。
3. EXEをロック依存関係でビルドしてSHA256を取得。Windows SDKのMakeAppxで実在の識別情報を使用して候補MSIXを構築。パッケージ内容・属性・実ファイルのハッシュを確認し、使用するMSIXスクリプトに問題があれば修正。
4. 本物のMSIXを別途Windowsにインストール、起動、アップデート、言語設定保持、アンインストールまで確認。Windows App Certification KitおよびPartner Centerの正式認定完了まで販売GOにしない。
5. `store/listing_ja.md`, `store/listing_en.md`, `store/privacy_policy_draft.md`, `store/third_party_review.md` の草案を、実際の製品動作とライセンス権利の検証に合わせて確定。合成データでStoreスクリーンショットを撮影する。

## P2 — 収益化・横展開
- 最初の有料製品: Excel / CSV Privacy Cleaner。国内買い切りの**試験価格案980円**、比較案1,480円。価格は未設定・未承認。需要検証やPartner Centerの対応価格で調整する。
- 次の候補: `-Secure-Share-Packager` の `improve/store-safety-20261018` を同じ品質基準で検証。上書き防止、ZIP整合性、処理範囲説明、UIのシンプルさを評価してから販売可否を判断。
- その後: PDF、画像、AI Upload Guard、Folder Privacy Auditor、バンドルの順。重複の多い低単価ツールを無条件で増やさない。

## 完了報告の形式
- 対象ブランチ・修正コミットSHA・差分概要。
- 実行したコマンド／結果（PASS/FAIL/SKIP）とログ・証拠の保存先、テスト環境。
- 未解決エラーと、誰がいつ何を確認すれば解消できるか。
- EXE／MSIXの実在有無、署名状態、SHA256、Partner Center登録・インストール認定状況。
- 一言の販売判断: **GO** または **HOLD**。実行証拠、権利、正式MSIX、Store認定に不足がある限り**HOLD**。

最終目標は「継続的に売れるMicrosoft Store商品」の完成。実データの安全性と簡単な操作を犠牲にして機能数だけ増やさないこと。
