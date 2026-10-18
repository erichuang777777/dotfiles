# 雲端、協作與研究整合

安裝日：2026-10-18。CLI 安裝與帳號授權分開記錄；以下安裝不代表已登入、部署或啟動付費 GPU。

| 工具 | 版本 | 專案 | 本機驗證／狀態 |
|---|---|---|---|
| GitHub CLI | 2.102.0 | [cli/cli](https://github.com/cli/cli) | 原已安裝，既有 GitHub 認證可用 |
| Netlify CLI | 27.13.0 | [netlify/cli](https://github.com/netlify/cli) | 版本指令通過；尚未登入 |
| Cloudflare Wrangler | 4.151.1 | [cloudflare/workers-sdk](https://github.com/cloudflare/workers-sdk) | 版本、whoami、本機 Worker HTTP 200 通過；尚未登入 |
| Google Workspace CLI | 0.22.5 | [googleworkspace/cli](https://github.com/googleworkspace/cli) | 版本與 auth status 通過；尚未設定 OAuth |
| Google Colab CLI | 0.7.4 | [googlecolab/google-colab-cli](https://github.com/googlecolab/google-colab-cli) | help 可執行；未授權、未建立運算執行階段 |
| Gemini CLI | 0.64.0 | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | 版本與 skills list 通過；未替使用者登入 |
| ClaudeR MCP 橋接 | 0.16.1 | [imnmv/clauder](https://github.com/imnmv/clauder) | MCP initialize 與 tools/list 通過，41 個工具 |
| ClaudeR R 套件 | 0.16.1 | [imnmv/clauder](https://github.com/imnmv/clauder) | R 載入與版本驗證通過 |
| RStudio | 2026.10.0+233 | [Posit RStudio](https://posit.co/products/open-source/rstudio/) | 已安裝並實際開啟，R 4.6.1 載入正常 |
| R | 4.6.1 | [R Project](https://www.r-project.org/) | Homebrew 安裝；Rscript 通過 |

Cloudflare CLI 在本清單以 Wrangler 為主。Google Drive 功能已包含於 Workspace CLI，沒有額外安裝另一套同名 Drive CLI。Workspace CLI 位於 googleworkspace 組織，但執行檔註明並非 Google 官方支援產品。

## 登入

```sh
netlify login
wrangler login
gws auth setup
gws auth login
colab --help
gemini
```

`gws auth setup` 會引導 Google Cloud／OAuth 設定；僅需要 Drive 時，以最小必要的 Drive 權限授權。Colab 請依 `colab --help` 的 auth 子命令或首次連線流程授權。本次未建立 Google Cloud 專案、啟用 API、部署網站、傳送郵件或申請 GPU。

## ClaudeR

R 套件來源固定為 `clauder-source.json` 的 commit。R 相依套件安裝遇到預設 60 秒下載逾時，重試時把該次 R 程序的 timeout 調為 600 秒後完成，未改全域下載逾時。

使用者 R 套件目錄為 `~/Library/R/4.6/library`；`~/.Renviron` 增加 `R_LIBS_USER=~/Library/R/%v/library`，讓 Homebrew R 與 RStudio 能找到套件。既有檔案已先備份，沒有將其私密內容放進此 repo。

在 RStudio 的 Console 執行：

```r
library(ClaudeR)
claudeAddin()
```

接著在 Viewer 按「Start Server」。Codex、Claude、Gemini、Pi 已登錄 stdio MCP `r-studio`，執行 `~/.local/bin/clauder-mcp`，由橋接程式尋找實際的 R 工作階段。尚未啟動工作階段時，MCP 工具清單可載入，但不能執行該工作階段的 R 程式。

## open-doc

CLI `@open-document/cli@0.2.1` 已安裝。工作區：`~/Documents/open-doc`，其中 core 為 0.13.1；實際套件鎖定於該工作區 package-lock.json。

```sh
cd ~/Documents/open-doc
npm run dev -- --mcp
```

本機頁面：`http://localhost:5273/`；MCP：`http://localhost:5273/mcp`。MCP initialize／tools/list 通過，共 26 個工具。未設定登入時自動啟動。

## 其他 CLI

CodeGraph 1.6.2 已登錄於 Codex、Claude、Gemini、Pi。只在範例專案執行 `codegraph init`；其他專案是否建立索引由使用者決定。安裝使用 `--no-permissions`，沒有新增 Claude 全域自動允許清單。

AOCI Code 0.1.0-rc21 已安裝，為預覽版本；先在專案執行 `aoci init`。未對整個家目錄建立索引。發行版授權為 FSL-1.1-MIT，不能將整份清單一律稱為 MIT 開源工具。

21st CLI 1.18.0 與 Hyperframes 0.8.170 已安裝。21st 的雲端功能仍需使用者登入。Hyperframes 本機需要瀏覽器；Docker 用於選用流程，未另外安裝 Docker。

open-doc 匯出驗證：上游中文範例 13 頁 PDF，版面檢查 0 錯誤；英文範例 14 頁 PDF 可匯出，但有 12 個上游交叉參照錯誤。未修改上游範例來隱藏錯誤，詳見 open-doc-layout-check.json。

RStudio 已實際載入 ClaudeR 控制面板，顯示工作階段 `default` 與 Start Server 按鈕。尚未啟動 R 執行伺服器，因此沒有宣稱完成 RStudio 工作階段內的端到端程式執行。下次可開啟 `~/Documents/ClaudeR/ClaudeR.Rproj`，執行同資料夾的 start.R，再按 Start Server。

Hyperframes 已完成 Chrome Headless Shell 安裝；本機範例的 lint、runtime、layout、contrast 檢查通過，未產生正式影片。詳細結果見 hyperframes-check.json。
