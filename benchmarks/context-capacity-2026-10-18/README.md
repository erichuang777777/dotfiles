# Mac Studio 128 GiB：gpt-oss 原生上下文容量實測

日期：2026-10-18。模型：`gpt-oss-120b-mxfp4-bf16`。本機 oMLX 記憶體保護上限 96 GiB、單一請求，沿用既有設定，未提高保護上限。

**結論：目前單跑 gpt-oss 120B，可處理原生 131,072 tokens 總上下文。** EmbeddingGemma 2 改部署於 GB10，沒有把 embedding 模型放入 Mac 記憶體。

| 輸入 tokens | 輸出 tokens | 重用前綴 tokens | 成功 | 首 token 秒數 | 請求耗時秒數 |
|---:|---:|---:|---|---:|---:|
| 32,768 | 1 | 0 | 是 | 16.09 | 29.92（含模型載入） |
| 65,536 | 1 | 32,767 | 是 | 19.14 | 19.26 |
| 130,560 | 1 | 65,535 | 是 | 53.74 | 53.98 |
| **131,071** | **1** | **0** | **是** | **85.37** | **86.54** |

最後一筆從不同的開頭建立輸入，API 回報 cached_tokens=0，總 tokens=131,072；不是只靠前綴快取推估容量。使用原始 completions API，沒有聊天模板與工具定義額外占用；實際 Agent 要把那些內容一起計入輸入。

## 記憶體

- 每 3 秒取樣 oMLX 的 macOS `phys_footprint`，包含 Metal 記憶體；不能只看 `ps` 的 RSS。
- 最後一筆請求期間取樣最高約 67.83 GiB。短暫峰值可能落在取樣間隔或快取收尾階段，因此另讀核心的程序最高水位。
- 冷輸入測試前，程序歷來最高水位約 72.09 GiB；測試及快取收尾後約 **76.56 GiB**。容量規劃採這個較高值，而非取樣值。
- Swap 測試前後均為 **3.69 MB**，沒有新增交換使用量。
- 記憶體保護上限 96 GiB，因此觀測峰值距此上限約 19.44 GiB；這不等於可以任意加入另一個大模型。

測試後的數值見 `post-cold-native-footprint.json`；逐次回應、取樣與時序見 `results.json`、`cold-native.json`、`summary.json`。

## 實際 Agent 配額

建議先以 **114,688 tokens 輸入＋16,384 tokens 輸出** 作為容量分配（總計 131,072）。輸入必須包含系統提示、工具定義、歷史、檔案與工具回傳，不能只計算貼入的文件。

這是依容量測試提出的分配，**沒有實測 16,384 tokens 長篇解碼或 Agent 品質**。長文件能放入，不代表全部內容都能被同樣準確地運用。

## 範圍與限制

- 測試時 oMLX 原本沒有已載入模型，本機模型目錄只剩 gpt-oss。API 仍列出其他已登錄模型，不能把 API 清單當作常駐狀態。
- 僅測單一 gpt-oss 請求，未同時運行 Nemotron、Gemma、Muse、GLM 或 MiniMax H3。
- 先前模型載入紀錄中 Nemotron 約需 31 GiB；若另保留它，不能沿用本次單模型的 128K 容量保證。
- 沒有測長上下文推理品質、多人併發或圖片輸入。

## 重跑

需 macOS、現有 oMLX app、8003 連接埠、`~/.omlx/api-key`、相同模型與 tokenizer。程式讀取金鑰但不輸出。

```sh
uv run --no-project --with tokenizers python context_capacity_probe.py
PROBE_PREFIX='COLD NATIVE CONTEXT PROBE. ' PROBE_TARGETS='[131071]' PROBE_RESULT=cold-native.json \
  uv run --no-project --with tokenizers python context_capacity_probe.py
```
