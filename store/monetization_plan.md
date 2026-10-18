# 2026-10-18 販売仮説と利益検証（決定ではない）

## 先行商品とターゲット

**第1候補: Excel / CSV Privacy Cleaner**
対象は外部委託・テスト・社内分析用のCSV/XLSXを日常的に編集する事務担当者、個人事業主、少人数のチーム。購入価値は「不要な列を誤って残さず、指定列を簡単に加工して別コピーにする」手間の削減。万能の個人情報削除やGDPR認証を売りにしない。

**第2候補: Secure Share Packager**
変換後のファイルをZIPへまとめ、SHA256・処理範囲を記録する補助。暗号化・機密削除済みとは限らない。第1製品の品質検証が終わった後に価格検証。

**無料競合が強い商品**: PDF単純結合/分割、EXIFメタデータ除去のみ、ディスク容量表示のみ。これらを最初の単品売上の柱にしない。

## 仮の国内買い切り価格（現時点では未設定）

- Excel / CSV Privacy Cleaner: **1,480円**（試験価格案）
- Secure Share Packager: **1,980円**（試験価格案）
- 両者の組み合わせ: **2,980円**（両製品の品質・ライセンス確認後の案）
- Partner Centerの日本円価格設定と各市場価格、消費税・返金条件は実際の画面で再確認。記載額が選べることは未確認。
- 初期段階では多品種を同時発売せず、1製品の評価・問い合わせ・不具合を測ってから追加。

## 販売数別の簡易シナリオ（Excel単品／月、売上予測ではない）

| 月間販売本数 | 売上総額（1,480円） | Microsoft commerce 15%控除後の単純計算 |
|--:|--:|--:|
| 10 | 14,800円 | 12,580円 |
| 30 | 44,400円 | 37,740円 |
| 50 | 74,000円 | 62,900円 |
| 100 | 148,000円 | 125,800円 |

上記は**需要予測ではない**。価格・購入率・実際の手数料・税・返金・為替・サポート費・開発人件費を考慮していない単純試算。Microsoft commerceを使う非ゲームアプリは原則15%のプラットフォーム手数料、独自commerceは別の条件で運用できるが、今回の前提はMicrosoft commerceでの買い切り価格。正式な収入はPartner Centerの計算による。

## 発売判断とKPI

1. **製品適合**: 合成データから外部共有準備までの一連の操作を初見で完遂できること。
2. **品質**: 列取り違え、既存ファイル上書き、CSV数式注入、誤った「完全除去」表示がないこと。
3. **市場**: 比較ページを見たテスターに「どの業務で使用するか」「買い切りならいくらまで払うか」を尋ね、価格を見直す。実売データが得られるまで収益は確定しない。
4. **販売後**: Storeページ閲覧数、購入数、返金数、レビュー評価、問い合わせ件数/販売本数、更新費用を月ごとに評価。
5. **拡張判断**: Secure Share Packagerの購入理由が独立して成立するか調査。単なるZIP生成やハッシュ計算だけならバンドルの上乗せ価値を再検討。

## 公式の競合・ルール参照（2026-10-18確認）

- 無料PDF編集: https://tools.pdf24.org/en/creator
- 無料PDF基本機能: https://pdfsam.org/downloads/
- 無料EXIF処理: https://exifcleaner.com/
- 容量解析価格: https://www.jam-software.com/treesize
- Windows Store価格: https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/schedule-pricing-changes
- Microsoft Store収益分配: https://learn.microsoft.com/en-us/windows/apps/publish/faq/get-started-with-the-microsoft-store
- Storeポリシー: https://learn.microsoft.com/en-us/windows/apps/publish/store-policies-and-code-of-conduct

**売上ゼロからの初回販売は未達。現段階の評価はPRE-LAUNCH/HOLD。**
