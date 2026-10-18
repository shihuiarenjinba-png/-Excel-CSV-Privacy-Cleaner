# Windowsアプリケーション制御によるEXE起動拒否 — 調査記録

## 確認された事実（2026-10-18）
- 対象ソース: `5a11d5e50eed856a8948966a9e0886248b58c615`
- 対象EXE SHA256: `9a81e3a7deb5d8048cde49b164bf0596344469644a1e12c57a06281fc6010962`
- 元の検証候補は Windows自動テスト PASS・EXE生成 PASS・ハッシュ整合性 PASS。
- Authenticode: `NotSigned` (未署名・初期候補)。この事実だけでは起動ブロックの根本原因を断定しない。
- Windows PowerShellの `Start-Process -FilePath $exe` が「アプリケーション制御ポリシーによってこのファイルがブロックされました」と返し、**起動していない**。
- **原因調査中、GUI実機合格・アプリケーション制御互換・商品登録・Store販売はHOLD。**

## してはいけないこと
- Windows Defender/Smart App Control/AppLocker/App Controlを無効化しない。
- 既存ポリシーの例外・ホワイトリストを勝手に作らない。
- Windowsファイルの保護属性を解除したり、不審なファイルを名前変更・再梱包して起動回避したりしない。
- 本体コード、既存EXE、既存MSIX、mainを調査目的で上書きしない。
- テスト用自己署名と製品用の信頼を混同しない。

## GitHubに追加した読み取り専用診断
`store/diagnose-application-control.ps1` を、ソースコードとは別の既存のWindows検証用cloneで実行する。EXEのSHA256一致を最初に検査し、次に過去24時間の次のイベントを**参照のみ**で検索する:

- `Microsoft-Windows-CodeIntegrity/Operational` : 3077 (強制ブロック), 3089 (関連署名情報), 3033 (署名/整合性問題候補)
- `Microsoft-Windows-AppLocker/EXE and DLL` : 8004 (EXE/DLLブロック)
- `Microsoft-Windows-Windows Defender/Operational` : 1116/1121 (マルウェア/ASRの手掛かり)

結果が空欄でも原因が存在しないことを証明しない。イベントの時間が古い場合は`-HoursBack`で最大168時間まで延長可能。イベントログが権限不足で見えない場合は管理者または組織のIT管理者に確認し、権限昇格のために設定を変更しない。

PowerShell実行例（ユーザーの既存検証用cloneがある場合のみ）:

```powershell
$repo = Join-Path $HOME 'ExcelCSVPrivacyCleaner-Validation\source'
git -C $repo pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'GitHub pull failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repo 'store\diagnose-application-control.ps1') -HoursBack 24
```

この`-ExecutionPolicy Bypass`は既存のQAと同様に個別PowerShellプロセスで診断用.ps1を実行するためのオプションであり、**Windowsアプリケーション制御のブロック解除・保護機能の無効化はしない**。運用ポリシーでPowerShell自体が禁止されている場合は管理者に相談する。組織管理端末では承認された方法だけを使用する。

GUIでも `Windowsセキュリティ → アプリとブラウザーコントロール → Smart App Control` の状態（オン/評価/オフ）を**確認のみ**する。`Windowsセキュリティ → ウイルスと脅威の防止 → 保護の履歴`に検知がないか**確認のみ**する。

共有される診断テキストから、Windowsユーザー名、PC名、個人ファイルパス、製品に無関係の検知情報等を削除する。

## 分岐と対応
1. **3077が対象EXEに一致:** App Control/Smart App Control等が拒否。実行環境の設定と署名・配布形式を整理する。セキュリティ機能を弱めない。
2. **8004が対象EXEに一致:** AppLocker拒否。組織ポリシーの制約を確認し、製品配布方式・必要な承認の検討へ。
3. **Defenderが検出:** 検出内容を調べ、実体の安全性、誤検知の可能性、PyInstallerで同梱した依存物を監査。勝手に「除外」しない。
4. **イベント不明:** 発生時刻直近のイベントを管理者と照合。根拠のない署名購入や環境変更には進まない。

## 正式なMicrosoft Store用MSIXとの違い
これは**未署名の単独EXEを直接起動する検証**。販売予定の **Microsoft Store経由MSIX** では、認定後にMicrosoftがMSIXパッケージを再署名する。StoreへのMSIX提出だけが目的なら、CA証明書を独自購入することは通常不要。**ただし今回の拒否が必ず解消するとは限らない**ため、実際にStoreの配布物・対象端末ポリシーで動作確認が必要。

公式資料:
- https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/appcontrol-debugging-and-troubleshooting
- https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/applocker/using-event-viewer-with-applocker
- https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions
- https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/package-version-numbering

この調査が完了するまでは、商品枠予約の前提としたGUI実機テストには合格していない。
