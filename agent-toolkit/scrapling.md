# Scrapling：資料蒐集與網頁擷取

安裝日期：2026-10-18。來源：[d4vinci/Scrapling](https://github.com/d4vinci/Scrapling)。

- PyPI：`scrapling[ai,shell]==0.5`，以 `uv tool` 建立獨立環境。
- 指令：`scrapling`、`scrapling-mcp`，位於 `~/.local/bin`。
- 官方 Skill：`~/.agents/skills/scrapling-official`；來源 commit 見 `scrapling-source.json`。Claude 透過符號連結共用，Codex、Pi、Gemini 使用原生共用目錄。
- MCP `scrapling` 已登錄到 Codex、Claude、Gemini、Pi，使用 stdio；沒有另開對外 HTTP 服務。
- 瀏覽器功能透過 `--executable-path` 沿用現有 Playwright Chromium 1248。沒有另外執行整套 `scrapling install`。

## 使用

```sh
scrapling --help
scrapling extract --help
scrapling shell
```

使用 Python API 時，採用專屬環境中的 Python：

```sh
~/.local/share/uv/tools/scrapling/bin/python your_script.py
```

例如：

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get("https://example.com")
print(page.status)
print(page.css("title::text").get())
```

重新啟動 Agent 後可使用 `scrapling` MCP 與 `scrapling-official` Skill。此工具不需要 API 金鑰；特定網站的登入需求另依網站而定。

## 驗證

1. 公開頁面 HTTP 擷取回傳 200，CSS 選取取得標題 `Example Domain`。
2. MCP `initialize` 與 `tools/list` 通過，共 16 個工具。
3. 本機測試頁面內的 `#result` 原始文字為 `before-js`；JavaScript 執行後改為 `after-js`。
4. MCP `make_request` 正確選取 `before-js`；`browser_fetch_once` 正確選取 `after-js`。
5. Pi 實際載入 `scrapling-official`，無診斷警告；Gemini `skills list --all` 顯示啟用。

結果見 `scrapling-http-smoke.json`、`scrapling-mcp-smoke.json`、`scrapling-e2e.json`。本次沒有驗證大量並行爬取、代理伺服器、登入狀態保存或網站驗證碼處理。

## 重裝

```sh
uv tool install 'scrapling[ai,shell]==0.5'
python3 agent-toolkit/restore-skills.py --apply
```

完整 Python 相依版本見 `scrapling-requirements.lock.txt`。MCP 設定等同於：

```json
{
  "command": "<HOME>/.local/bin/scrapling-mcp",
  "args": ["--executable-path", "<installed-chromium-executable>"]
}
```

請把佔位符換成本機絕對路徑。新機器若沒有現成 Chromium，可依上游文件執行 `scrapling install` 下載瀏覽器；本機沿用的 Chromium 路徑包含版本，清除 Playwright 快取後需重新設定。
