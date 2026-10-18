# Agent 工具與 Skills 安裝紀錄

更新日期：2026-10-18。Mac Studio／Apple Silicon。

## 共用 Skills

共 77 個 skills，來源固定於 Git commit。Codex、Pi、Gemini 共用 `~/.agents/skills`；Claude 透過 `~/.claude/skills` 符號連結載入。重新啟動 Agent 後生效。

| 類別 | 專案 | Skills 數 | 狀態 |
|---|---|---:|---|
| 設計與介面 | [s0xDk/refactoring-ui-skill](https://github.com/s0xDk/refactoring-ui-skill) | 1 | 已安裝 |
| 研究方法與科學繪圖 | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | 23 | 已安裝 |
| 設計與介面 | [lucasmarkes/hairline](https://github.com/lucasmarkes/hairline) | 2 | 已安裝 |
| 研究方法與科學繪圖 | [ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers) | 1 | 已安裝 |
| 動畫與影片 | [Jakubantalik/transitions.dev](https://github.com/Jakubantalik/transitions.dev) | 3 | 已安裝 |
| 程式理解與上下文最佳化 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 6 | 已安裝 |
| 設計與介面 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 1 | 已安裝 |
| Agent 工作流程與輸出 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 3 | 已安裝 |
| 設計與介面 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 1 | 已安裝 |
| 設計與介面 | [21st-dev/skill](https://github.com/21st-dev/skill) | 7 | 已安裝 |
| 動畫與影片 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 21 | 已安裝 |
| 設計與介面 | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | 1 | 已安裝 |
| 程式理解與上下文最佳化 | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | 1 | 已安裝 |
| 文件與簡報 | [simonliu-ai-product/open-doc](https://github.com/simonliu-ai-product/open-doc) | 5 | 已安裝 |
| 資料蒐集與網頁擷取 | [d4vinci/Scrapling](https://github.com/d4vinci/Scrapling) | 1 | 已安裝 |

## CLI、MCP 與雲端

請參照 [雲端與研究整合](cloud-and-research.md)，包含 GitHub、Netlify、Wrangler、Workspace／Drive、Colab、Gemini、ClaudeR，以及 open-doc。固定 CLI 版本見 cli-versions.json。

## 分類補充

除了設計、研究、上下文最佳化及系統評測，再補上「動畫與影片」、「文件與簡報」、「Agent 工作流程」、「雲端與協作」、「安裝與重現」。同一工具可以有多個標籤。

## 系統與推論評測

現有 oMLX／Pi 設定、模型原生上下文與測試資料見 [本機 Agent 評測](../benchmarks/local-agents-2026-10/README.md)。vLLM、SGLang 列為其他硬體的未來部署項目，本機未新增部署。

## 尚未啟用與名稱修正

- ToolRush：[OnlyTerp/toolrush](https://github.com/OnlyTerp/toolrush) 原始碼已下載。現行流程依賴 Windows／Hermes，未套用到 Pi、Codex、Claude 或 Gemini。
- AOIC CODE 更正為 [AOCI Code](https://github.com/aoci-spec/aoci-code)。
- impactable 更正為 [Impeccable](https://github.com/pbakaus/impeccable)。
- 使用者指定文件類改成 open-doc，DOT、OpenWord、OpenFormula、OpenSlide 不列為已啟用。
- RStudio 整合依使用者連結選用 [ClaudeR](https://github.com/imnmv/clauder)，未安裝先前候選 rstudiomcp。

## 重現

`skills.lock.json` 記錄來源 SHA 與安裝路徑，`inventory.json` 記錄實際 SKILL.md SHA256。`restore-skills.py` 預設只顯示計畫，加入 `--apply` 才會安裝缺少的 skills；需要官方 OpenAI skill-installer helper，Transitions 中繼資料調整另需 PyYAML。已有的 skills 與連結均保留。

```sh
python3 agent-toolkit/restore-skills.py
python3 agent-toolkit/restore-skills.py --apply
```

`research-requirements.lock.txt` 是獨立 Python 3.12 環境套件鎖定清單。不要套用到系統 Python。

## 驗證範圍

- Pi 實際載入 78 個 skills（含原有 ego-browser），沒有格式診斷警告。
- Gemini CLI 實際列出共用 skills。
- CodeGraph 範例 TypeScript 索引與 square 符號查詢通過；僅範例專案建立索引。
- ClaudeR MCP 與 CodeGraph MCP 的 initialize／tools/list 通過。ClaudeR 有 41 個工具。
- 研究 Python 已產生並讀回 PNG、PDF、DOCX、PPTX、XLSX；未驗證試算表公式重新計算。
- open-doc 範例工作區已完成正式建置。
- AOCI 執行檔通過 SHA256 與 GitHub provenance attestation 驗證；範例 init／scan／status 通過。
- Skills 安裝與格式驗證不代表所有上游功能都做過端到端測試。
- Transitions 的 description 過長，僅縮短 YAML 中繼資料，保留完整指令本文；詳見 local-adaptations.json。

Scrapling CLI、MCP、JavaScript 擷取測試與 Python 使用方式見 [Scrapling](scrapling.md)。
