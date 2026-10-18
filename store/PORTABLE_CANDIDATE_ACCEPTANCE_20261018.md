# Excel / CSV Privacy Cleaner — 検証候補EXEの受入判定（2026-10-18）

## 現在確認できる証拠
- Windowsのユーザー実行結果: `PORTABLE CANDIDATE COMPLETE FOR QA. NOT A STORE MSIX OR SALE APPROVAL.`
- ユーザーが報告した構築元のソースSHA: `5a11d5e50eed856a8948966a9e0886248b58c615`
- ユーザーが報告したEXE SHA256: `9a81e3a7deb5d8048cde49b164bf0596344469644a1e12c57a06281fc6010962`
- ビルド処理は自動テスト成功後にのみ起動する設計。Windowsから結果の文字列が出ているため、**当該ソース版ではローカル自動QAとポータブル候補生成が成功したと合理的に判断できる**。ただし、現物のEXEとログはGitHub側にはなく、第三者による再検証・GUI実機受入は未実施。
- 現在の判定: **登録HOLD、販売HOLD。** 既存の候補EXEを改変・削除・再署名しない。

## まずEXEの完全性を読むだけで検証
PowerShellで、GitHubの改良ブランチを別の検証フォルダーへpullした後:

```powershell
$repo = Join-Path $HOME 'ExcelCSVPrivacyCleaner-Validation\source'
git -C $repo pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'GitHub update failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repo 'store\review-portable-candidate.ps1') -SourceSha '5a11d5e50eed856a8948966a9e0886248b58c615'
```

このスクリプトは`Documents\ExcelCSVPrivacyCleaner-Candidates`内から**ソースSHAが一致する候補を1件だけ**見つけ、実際のEXEハッシュとmanifestのEXEハッシュが一致するか確認する。Authenticode状態は表示するが、`NotSigned`は販売用署名の完了を意味しない。ソース・EXE・データは一切変更しない。

## 次は実際にGUIを操作する受入試験
- [ ] できたEXEをWindowsで手動起動できる。
- [ ] 一目で「ファイル選択 → 列選択 → マスク/仮名化/削除 → プレビュー → 別名保存」が分かる。
- [ ] 合成CSVを開き、email列だけ選んでマスク→新規保存。元データのSHA256は不変、既存の出力も上書きされない。
- [ ] 合成XLSXの複数シートで、加工したシートと未加工シートが分かる。
- [ ] 数式・複雑構造を含むXLSXはエラーの日本語が理解でき、壊れた出力を生成しない。
- [ ] 日本語/英語、DPI100/125/150%、キーボード操作、Windows10/11（サポート対象版）で操作を確認する。
- [ ] 初見利用者が想定業務を説明なしで完遂できる。ログやスクリーンショットは**架空データのみ**で作成する。

具体的な手順: [USER_ACCEPTANCE_SCENARIOS.md](USER_ACCEPTANCE_SCENARIOS.md)

## ソフトウェア・運用安全
- [ ] Windows Defenderまたは承認済みAVで、**EXE現物**をスキャン。検知なし=絶対安全の証明ではない。
- [ ] アプリの起動→選択→変換→保存時に、実行バイナリの外部送信、子プロセス、一時データ、クラッシュログを観察。ネットワーク監査はResource Monitorだけでは瞬間的な接続を見落とすため、必要に応じProcess Monitor等で補完。通信が観測されても内容を調べるまで「機密流出」とは断定しない。
- [ ] ロックした依存ライブラリ、PyInstaller同梱バイナリ、Pythonランタイム、アイコン・フォント・画像などのLICENSE/NOTICE、独自利用規約を法務/販売責任者が承認。
- [ ] プライバシーポリシー、連絡先・有効なサポートURL、商品説明の表示範囲が本体と一致する。
- [ ] 少なくとも1人の初見利用者に架空データで操作してもらい、商用で買う価値があるか確認する。

## 商品登録の条件
上記のGUI・安全・法務・商品説明の重要項目がPASSとなり、購入理由・販売形態・商品名の権利を確認できたら、**Microsoft Partner Centerに製品枠を作成**する。その時点で実際のIdentityName/Publisherが得られる。

その後、正式なMSIX、インストール/起動/アップデート/アンインストール、WACK/Store認定、実際の価格設定まで進める。**EXE完成とMSIX完成を混同しない**。

## 改修方針
当面、`5a11d5e`の候補を後から静かに変更しない。不合格が発見された場合は独立改良ブランチで修正し、新たなソースコミットと検証結果と候補EXEを**別名で**作成して評価し直す。mainと過去の検証候補は保護する。
