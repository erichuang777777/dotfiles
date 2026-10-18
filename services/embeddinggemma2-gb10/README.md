# GB10：EmbeddingGemma 2 文字向量服務

部署日期：2026-10-18。模型：[google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2)，固定 revision 見 `model-source.json`。使用 Google 官方的 Sentence Transformers 路徑，BF16／CUDA。

## 已部署

- GB10 容器：`local-inference-embeddinggemma2`，`restart: unless-stopped`。
- 專案：GB10 的 `~/local-inference/embeddinggemma2-gb10`。
- 僅綁定 GB10 的 Tailscale IP、8011 連接埠，所有 API 均需 Bearer API key；未綁定所有主機介面的對外位址。
- 使用非 root UID 1000、移除 Linux capabilities、禁用權限提升。沒有變更既有 ComfyUI。
- Docker 的預設網段池已滿，因此沿用既有 `bridge` 網路，不建立新網段，也未刪除其他網路。
- 模型快取使用此服務的獨立資料夾，未掛入其他模型的完整 HF 快取或帳號 token。

## API

Base URL：`http://<GB10_TAILSCALE_IP>:8011/v1`。

| 路徑 | 用途 |
|---|---|
| `GET /health` | 模型 revision、CUDA 裝置及當前配置／保留記憶體 |
| `GET /v1/models` | 模型清單 |
| `POST /v1/embeddings` | OpenAI 風格的文字 embedding 請求 |

請求範例（JSON 本身不含金鑰）：

```json
{
  "model": "google/embeddinggemma-2",
  "input": ["這是一段要建立索引的文字。"],
  "input_type": "document",
  "dimensions": 768,
  "encoding_format": "float"
}
```

查詢用 `input_type: query`，文件用 `document`，服務採用模型內建的對應提示前綴。支援 128、256、512、768 維，縮減後重新正規化。每次最多 16 筆，GPU 批次為 8，同時序列化 GPU 推論。每筆最多 8,192 tokens，包含任務前綴；超長直接拒絕，不默默截斷。

**本次部署僅啟用文字編碼器；沒有提供圖片、音訊或影片 API。** 服務停用 vision／audio encoders，以減少常駐占用。官方完整模型支援多模態，不等於此服務已啟用所有模態。

## Mac 端設定與金鑰

- `~/.config/gb10-embedding/config.json`：實際 endpoint、模型與金鑰檔案位置。
- `~/.config/gb10-embedding/api-key`：私人金鑰，權限 0600。
- GB10 另存相同金鑰於 `~/.config/gb10-embedding/api-key`，唯讀掛入容器。

金鑰沒有放入 Git、模型參數、命令列或測試輸出，也沒有讀取或寫入使用者的 1Password 保管庫。後續可由使用者將此金鑰納入 1Password 管理。

Mac 端 Python 使用範例：

```python
import json
import urllib.request
from pathlib import Path

config = json.loads((Path.home() / '.config/gb10-embedding/config.json').read_text())
key = Path(config['api_key_file']).read_text().strip()
request = urllib.request.Request(
    config['base_url'] + '/embeddings',
    data=json.dumps({'model': config['model'], 'input': '文字查詢', 'input_type': 'query'}).encode(),
    headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
)
result = json.load(urllib.request.urlopen(request, timeout=30))
print(len(result['data'][0]['embedding']))
```

Mac 僅處理 API 請求及回傳向量，不載入 embedding 模型；目前尚未把此 endpoint 接到特定 RAG／向量資料庫應用。

## 驗證結果

Mac 透過 Tailscale 呼叫 GB10，已通過：

- 三筆繁體中文文件產生 768 維有限數值向量。
- 查詢與文件使用各自前綴，貓咪查詢在三筆文件中正確選到貓咪文件。這是小型整合測試，不是 embedding 品質排名。
- 128 維 MRL 縮減。
- 缺少金鑰回傳 401；空批次、超過 16 筆、超過 8K tokens 均拒絕；不支援的維度拒絕。
- 容器透過 Compose 重建啟動後可再次回傳向量。

三筆短文件首次測量約 0.51 秒，包含網路與啟動後第一次推論，不能當作穩定吞吐量。短輸入測試後 CUDA allocated 約 0.54 GiB；這不包含所有 CPU、驅動與長批次暫存，不能當作服務總記憶體上限。

完整結果見 `verification.json`。測試曾發現單靠上游 `max_seq_length` 不能可靠拒絕超長輸入，已明確限制為原生 8,192，並關閉計數時的截斷後通過測試。

## 重建

本 Dockerfile 以這台 GB10 既有 CUDA／PyTorch 基底 `local-inference/comfyui:gb10-20261012` 建立隔離映像，不修改原映像或正在執行的 ComfyUI。基底與服務映像 ID、實際套件版本見 `runtime.json`；新機器須先準備相容的基底，這不是通用的跨平台 Dockerfile。

```sh
cp .env.example .env
# 填入 GB10 Tailscale IP、私人金鑰檔案位置與 UID/GID。
mkdir -p cache
docker compose config --quiet
docker compose up -d --build
```

新部署前另行產生私人金鑰檔案，並限制檔案權限為 0600。不要把金鑰內容填進 `.env` 或這份 repo。
