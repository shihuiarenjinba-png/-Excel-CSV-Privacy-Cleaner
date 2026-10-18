# 2026-10-18 販売仮説と利益検証（決定ではない）

## 先行商品とターゲット

**第1候補: Excel / CSV Privacy Cleaner**
対象は外部委託・テスト・社内分析用のCSV/XLSXを日常的に編集する事務担当者、個人事業主、少人数のチーム。購入価値は「不要な列を誤って残さず、指定列を簡単に加工して別コピーにする」手間の削減。万能の個人情報削除やGDPR認証を売りにしない。

**第2候補: Secure Share Packager**
変換後のファイルをZIPへまとめ、SHA256・処理範囲を記録する補助。暗号化・機密削除済みとは限らない。第1製品の品質検証が終わった後に価格検証。

**無料競合が強い商品**: PDF単純結合/分割、EXIFメタデータ除去のみ、ディスク容量表示のみ。これらを最初の単品売上の柱にしない。

## 仮の国内買い切り価格（現時点では未設定）

- Excel / CSV Privacy Cleaner: **980円**（初期試験価格の第一案。1,480円は比較案）
- Secure Share Packager: **1,280〜1,980円**（別途価値検証が必要な価格帯）
- 両者の組み合わせ: **1,980〜2,980円**（両製品の品質・ライセンス確認後に検討）
- Partner Centerの日本円価格設定と各市場価格、消費税・返金条件は実際の画面で再確認。記載額が選べることは未確認。
- 初期段階では多品種を同時発売せず、1製品の評価・問い合わせ・不具合を測ってから追加。

## 販売数別の簡易シナリオ（Excel単品980円／月、売上予測ではない）

| 月間販売本数 | 売上総額（980円） | Microsoft commerce 15%控除後の単純計算 |
|--:|--:|--:|
| 10 | 9,800円 | 8,330円 |
| 30 | 29,400円 | 24,990円 |
| 50 | 49,000円 | 41,650円 |
| 100 | 98,000円 | 83,300円 |

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

## 追加の直接競合と検証上の注意

- Scrubsheet for Excel は500行まで無料、Proには仮名化とプレビューがある。こちらは**Excel本体を要求しない独立アプリ**として比較する。ただし複雑なブック構造や大量データの性能は本製品の未検証事項。https://marketplace.microsoft.com/en-us/product/wa200012522
- IRI CellShield はExcel向け買い切り$35、商用利用制限がある。https://www.iri.com/products/cellshield/cellshield-addin
- Microsoft Storeでは類似CSV・事務ツールが低価格帯で販売されている。購入理由が確認できなければ980円でも高い可能性がある。https://www.microsoft.com/en-na/store/new/apps/pc?category=Productivity&price=2To6
- **価格の仮説は購入証拠ではない。** 1,480円は操作性・品質・サポート評価が支持した場合の比較価格とする。
