# Windowsテスト実行ガイド — リポジトリ未取得のPC向け

**目的:** まだGitHubからソースを取得していないWindows PCでも、既存の作業フォルダーに触れずにQAを実行する。
**対象:** \`shihuiarenjinba-png/-Excel-CSV-Privacy-Cleaner\`
**ブランチ:** \`improve/simple-column-ui-20261018\`
**Microsoft Store登録:** 品質検証が終了するまではHOLD。

## よくあるエラー
PowerShellの表示が \`PS C:\Users\aaron>\` の状態で
\`powershell -File .\store\run-windows-qa.ps1\` と実行しても、\`C:\Users\aaron\store\run-windows-qa.ps1\` は存在しないので失敗する。
これは**何も実行できていない状態**であり、アプリのテスト不合格ではない。
GitHubにコミットしたファイルは手元のPCへ自動で配置されない。

## 初回だけ（新しい独立フォルダーへclone）

PowerShellに次の一式を**そのまま**貼り付ける。Gitとサポート対象のPythonが必要。

\`\`\`powershell
$ErrorActionPreference = "Stop"
$branch = "improve/simple-column-ui-20261018"
$parent = Join-Path $HOME "ExcelCSVPrivacyCleaner-Validation"
$source = Join-Path $parent "source"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not in PATH. Install Git for Windows first."
}
if (Test-Path -LiteralPath $source) {
    throw "Existing source folder detected: $source. No overwrite performed. Use the existing clone or choose another QA folder."
}
New-Item -ItemType Directory -Path $parent -Force | Out-Null
git clone --single-branch --branch $branch "https://github.com/shihuiarenjinba-png/-Excel-CSV-Privacy-Cleaner.git" $source
if ($LASTEXITCODE -ne 0) { throw "Git clone failed. Check network and your GitHub permissions." }
$script = Join-Path $source "store\run-windows-qa.ps1"
if (-not (Test-Path -LiteralPath $script -PathType Leaf)) { throw "Script is missing after clone: $script" }
git -C $source rev-parse HEAD
powershell -NoProfile -ExecutionPolicy Bypass -File $script
\`\`\`

最後に\`QA report: ...\`が出た場合は、その**JSONの保存先と結果**だけコード担当に渡す。個人情報が混入していないことを確認しないままログを公開しない。

## 既にリポジトリがある場合
リポジトリの**本当の保存先**に移動し、\`Test-Path\`で存在確認してから実行する。

\`\`\`powershell
Set-Location "C:\YOUR\ACTUAL\PATH\-Excel-CSV-Privacy-Cleaner"
git branch --show-current
Test-Path -LiteralPath ".\store\run-windows-qa.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\store\run-windows-qa.ps1"
\`\`\`

上記\`C:\YOUR\ACTUAL\PATH\`は説明用で、実際に保存したフォルダーへ置き換えること。ブランチが異なる場合は実行を中断しコード担当に確認する。重要な既存リポジトリは勝手に\`git pull\`・\`git reset\`・\`git clean\`しない。

## テスト後
- **PASS:** ローカルの自動テストについてのみPASS。GUIの目視、Win10/11実機、通信監査、再配布ライセンスは別途必要。
- **FAIL:** \`QA report: ...\`のパスと\`tests.log\`のエラー箇所、\`git rev-parse HEAD\`のSHAを伝える。
- **GitHub ActionsのRunner停止:** 別の環境問題なので、ローカルQAの結果とは分ける。
- **未検証:** Microsoft Store商品枠の作成、MSIXアップロード、販売開始は行わない。

証拠を保管する場合は\`$HOME\Documents\ExcelCSVPrivacyCleaner-QA\`以下（Windows環境により実際の保存先を確認）。ここには合成データのみが含まれるべきで、GitHubにアップロードしない。
