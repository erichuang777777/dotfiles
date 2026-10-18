# Mac Studio 本機模型與 Agent 工具呼叫測試

整理日期：2026-10-18。硬體：Mac Studio、Apple M5 Max、18 核心 CPU、128 GiB 統一記憶體。推論後端為本機 oMLX。目前軟體快照為 oMLX 0.7.0（build 2987）；其他套件版本同樣收錄，不能假定所有歷史輪次使用相同版本。完整硬體與目前模型設定見 [environment/current.json](environment/current.json)。

此報告收錄 **21 輪、684 個計分案例**，另外附上繁中代理測試與 Pi 端到端事件。這是特定模型量化、聊天範本、推論後端及測試程式的組合結果，**不是通用智慧排行榜，也不是 ARC-C／GSM8K 分數**。

## 目前建議

- **本機 Agent 主力：Nemotron 3.5 Lightning 30B-A3B 8-bit。** 在這輪基礎及進階合成工具測試共 36／36 通過，嚴格格式也全數通過。Pi 已安裝並設定為使用此模型。
- **一般文字、程式、計算與指令遵循：保留 gpt-oss-120b。** 最近基礎題為 24／24，但多步工具任務曾反覆改寫最終訂單編號，需要程式驗證工具資料與最終答案。
- **Muse Glimmer 30B：可作 Agent 備選。** 本輪也是 36／36，但此環境的任務耗時中位數較 Nemotron 高。
- **Gemma 4 31B：內容多數正確，但格式遵循較不穩定。** 自動驗證未通過的兩題是詢問日期時混入英文「which」，不應把它們描述成選錯工具。
- GLM-4.7-Flash 8-bit 在最近一輪基礎代理案例為 12／12，但不同輪次仍出現捏造資料、計算或格式問題。

以上建議尚未經長時間真實專案、實際瀏覽器操作或接近滿載上下文驗證。此報告不直接比較雲端 OpenAI 模型，也不宣稱 Pi 優於 Codex。

## 上下文：目前是否為原生上限？

依目前下載檔案的 `config.json`（`max_position_embeddings` 或 `text_config.max_position_embeddings`）及 oMLX 設定，五款模型都已對齊該份 checkpoint 的原生設定上限：

| 模型 | 原生設定／目前設定 | 權重大小約（十進位 GB） |
|---|---:|---:|
| Nemotron 3.5 Lightning 30B-A3B 8-bit | 262,144 tokens（256K） | 33.6 |
| Muse Glimmer 30B 8-bit | 131,072 tokens（128K） | 33.4 |
| Gemma 4 31B IT 8-bit | 262,144 tokens（256K） | 33.8 |
| gpt-oss-120b MXFP4/BF16 | 131,072 tokens（128K） | 65.3 |
| GLM-4.7-Flash 8-bit | 202,752 tokens（198K） | 31.8 |

Pi 的 Nemotron `contextWindow` 亦為 **262,144**。目前每款預設單次生成上限為 131,072 tokens。輸入、系統指令、工具描述、歷史、工具結果、思考與輸出仍須納入整體容量規劃；不能把上下文與生成上限相加，當成可同時用滿的總長度。Pi 也會為生成及壓縮保留空間。

oMLX 的 `max_context_window` 欄位用來檢查提示 token 數。把此欄位設到原生值只代表解除較低的設定限制，**沒有證明模型可在原生總長度之外繼續生成，也沒有證明滿載時記憶體足夠**。本次沒有進行 RoPE 延伸或 128K／256K 滿載壓力測試。

目前設定快照不等於所有歷史測試當時的設定。較早 GLM 測試曾限制為 32K；後來才提高到 202,752。

## 新增三款模型：相同測試套件的結果

Chat Completions 與 Responses API 都測。基礎套件是 6 種情境 × 2 API × 2 輪＝24 個案例；進階套件是 6 種情境 × 2 API × 1 輪＝12 個案例。

| 模型（皆為 MLX 8-bit） | 基礎內容／嚴格格式 | 進階內容／嚴格格式 | 合計內容 | 合計嚴格格式 | 案例耗時中位數 |
|---|---:|---:|---:|---:|---:|
| Nemotron 3.5 Lightning 30B-A3B | 24／24、24／24 | 12／12、12／12 | **36／36** | **36／36** | **2.43 秒** |
| Muse Glimmer 30B | 24／24、24／24 | 12／12、12／12 | **36／36** | **36／36** | 19.73 秒 |
| Gemma 4 31B IT | 22／24、9／24 | 12／12、5／12 | 34／36 | 14／36 | 14.90 秒 |

耗時是一個案例的完整多輪流程時間中位數，**不是 token／秒、首字延遲或模型載入時間**。在本輪案例中，Muse／Nemotron 的中位數比約 8.1；不能推廣為所有工作負載都相差八倍。模型架構、思考長度及輸出內容均可能影響時間。

來源：[候選測試逐輪資料](results/candidates/)、[所有輪次 CSV](run-summary.csv)、[所有案例 CSV](case-results.csv)。

### 測試情境

基礎：客戶→訂單→狀態三步鏈、暫時錯誤重試、工具資料內的提示注入、資訊不足時詢問日期、Unicode 與引號路徑、查無資料不捏造。

進階：巢狀物件／陣列及布林參數、易混淆 ID 原樣保留、永久性錯誤不得重試、先搜尋再讀文件、數值與列舉參數、明確禁止工具時不呼叫。

所有工具回傳都是測試程式注入的固定合成資料。**沒有查詢真實客戶、修改真實訂單、讀取提示中的 `/tmp` 文件，或呼叫外部天氣等服務。** 人名及門診情境屬測試字串，不是醫療資料或事實陳述。

### 取樣與模型版本

此輪三款統一使用 temperature=1.0、top_p=0.95；Gemma top_k=64，其餘 top_k=0。每次生成最多 4,096 tokens，與模型設定可用的 131,072 上限分開。這可控制案例規模，但**不是每款模型的官方最佳化設定對決**；例如 Muse 的 generation_config 有 `do_sample=false`。思考模式及模型範本也不完全相同。

Nemotron 設定 `enable_thinking=true`、`force_nonempty_content=true`；Gemma 設定 `enable_thinking=true`。MTP 關閉。請從 [environment/current.json](environment/current.json) 查看設定快照，從逐題 raw 回應查看實際輸出與 usage。

| 模型來源 | 固定 revision |
|---|---|
| [mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit](https://huggingface.co/mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit) | `881a85f9e84dac5ab1a61d4493739b5ef67efeaa` |
| [mlx-community/Muse-Glimmer-30B-8bit](https://huggingface.co/mlx-community/Muse-Glimmer-30B-8bit) | `679c45e1b331a6514a6e38076a353cc5fed21bf6` |
| [mlx-community/gemma-4-31b-it-8bit](https://huggingface.co/mlx-community/gemma-4-31b-it-8bit) | `f5f3dc92ab4af76724c36c21eb6bedadb3a851be` |

下載完成後，執行流程核對所有檔案大小及 manifest 中的 LFS SHA-256，再進行載入與測試。manifest 收錄於 [environment/](environment/)。

## gpt-oss 與 GLM：最新重測與歷史資料

最新基礎文字套件每款 24 題，涵蓋繁中、姓名、結構化擷取、避免捏造、計算、提示注入、程式、多輪狀態、長文擷取及單步工具。與上述「基礎代理套件」是**不同套件**。

| 模型 | 最新文字套件嚴格通過 | 僅去除額外 Markdown 後 | 最新基礎代理內容 | 最新代理嚴格格式 | 文字題耗時中位數 |
|---|---:|---:|---:|---:|---:|
| gpt-oss-120b | 24／24 | 24／24 | 10／12 | 10／12 | 1.85 秒 |
| GLM-4.7-Flash 8-bit | 18／24 | 23／24 | 12／12 | 10／12 | 7.29 秒 |

這兩款最新代理套件各只有 6 情境 × 2 API × 1 輪＝12 個案例，**未跑新增三款的進階套件**，因此不要把 12／12 與 36／36 當成同樣強度的證據。

gpt-oss 的三步工具呼叫曾成功，但最終回答把工具回傳 `O-204B` 改寫成 `O-202`、`O-202204` 等；這是資料保留問題，不應只檢查工具是否被呼叫。GLM 歷史測試曾把 47,012 算成 47,112、回傳修改輸入資料的程式，以及在未查工具時輸出捏造診間。最新一輪通過不能抹去先前失敗。

所有歷史文字測試（包含早期 Qwen）列於下表；可直接從 CSV 與逐題 JSON 檢查，**不跨輪次合併成一個智慧分數**：

| 輪次識別碼 | 模型 | 嚴格通過 |
|---|---|---:|
| 20261014-195204 | Qwen3.8 Flash Next REAP320 oQ3e DWQ MTP Vision | 59／72 |
| 20261014-200024 | Qwen3.8 27B NVFP4 | 60／72 |
| 20261014-201213 | Qwen3.8 Flash Next oQ4e MTP | 66／72（另記錄 1 次 API 錯誤） |
| 20261014-234528 | gpt-oss-120b | 71／72 |
| 20261015-172714 | GLM-4.7-Flash 8-bit | 50／72 |
| 20261015-185024 | GLM-4.7-Flash 8-bit | 16／24 |
| 20261015-185559 | gpt-oss-120b | 23／24 |
| 20261018-085221 | GLM-4.7-Flash 8-bit | 18／24 |
| 20261018-085757 | gpt-oss-120b | 24／24 |

Qwen 歷史資料供追溯，不代表已在目前設定重新測試；這些模型已不在現有五款模型清單中。

## 繁中代理與 Pi 端到端測試

- 模型能力測試使用 `http://127.0.0.1:8005` 的原始輸出，未套用 OpenCC。
- 繁中代理在 `8003`，將一般回答轉換成臺灣繁體中文；工具參數、路徑等機器字串應保留。附上的代理測試主要是 gpt-oss／GLM，不能假定三款新增模型都做了同樣的長回答代理測試。
- gpt-oss 的 2,048-token 較長回答測試曾被截斷；提高到 4,096 後正常結束。最新代理重測兩款都正常結束，沒有在那些最終回答中偵測到明顯重複字尾或亂碼；不代表永遠不會發生。
- Pi 1.3.0 已透過 `8003` 接上 Nemotron；模型 `contextWindow=262144`，備選為 gpt-oss。Pi 的 API 金鑰從私密檔案讀取，沒有附在此儲存庫。
- **Pi 初次實測出現兩次無效的 edit 參數**：把陣列傳成格式錯誤的字串。模型改用 bash 完成修改。補上工具參數結構指令後，再測 `read → edit → read → write → bash` 全數成功，並驗證姓名與易混淆編號未變。
- 因此，Nemotron 的合成工具 36／36 **不等於實際 Agent 的所有工具格式都一定正確**。應繼續測真實工作流程，特別是含引號的編輯與大型檔案。

Pi 的三輪原始事件與安裝結果見 [results/pi-smoke/](results/pi-smoke/)。第一輪失敗紀錄保留，沒有只挑最後成功的一輪。

## 記憶體與 H3 共用

本機為 128 GiB＝137.44 十進位 GB。Nemotron 與 gpt-oss 權重合計約 98.8 GB，尚未計上下文快取、暫存、OS 及其他軟體。oMLX 目前有 96 GiB 的記憶體保護上限、一次處理 1 個請求。

本機 `h3.c/README.md` 記載特定 MiniMax H3 生成案例約 40.1 GB 實體記憶體峰值；這不是本套 LLM bench 的測量，也不是 H3 所有工作負載的固定需求。三者粗加約 138.9 GB，已接近或超出整機物理容量，且未計 OS／語言模型上下文。H3 的映射權重可回收、各階段峰值也不同，所以不能把此粗加視為精準的並行峰值，但足以說明需要共跑實測。

建議 Nemotron 作常用 Agent；H3 生成與 gpt-oss 載入按工作負載安排。H3 的 SSD streaming 可降低部分常駐權重需求，但有速度代價。oMLX 的保護設定**不會替獨立 H3 程序保留記憶體**。本次沒有做三程序同時滿載測試，也沒有在整理報告時更動常駐設定。

## 評分限制與資料處理

1. `passed`：工具名稱、順序、參數及最終結果符合測試程式；最終 JSON 可容許一層完整 Markdown fence。`strict_passed`：最終回答須可直接解析成預期 JSON，沒有額外 Markdown 或多餘鍵。它不是供應商的 constrained decoding／JSON Schema 保證。
2. 工具參數及結果主要以 Python `json.loads(...) == expected` 比較；**不是完整 JSON Schema 型別驗證**，例如 Python 中 `true` 與 `1`、`1` 與 `1.0` 可能相等。進階套件有型別相關題目，但不應稱為嚴格型別證明。
3. 日期澄清題使用固定關鍵字判斷；Gemma 的 `which 一天` 仍有澄清意圖，卻未被驗證器接受，且不符合預期繁中表達。34／36 是自動驗證分數，不代表兩次危險操作。
4. 簡體、重複與思考洩漏檢查是啟發式，不是完整語言學或 Unicode 正確性驗證。程式題使用有限 AST 與封閉測例，可能拒絕驗證器未支援但有效的寫法。
5. 所有延遲採每案例 `time.monotonic()`。本機牆上時鐘紀錄有回撥跡象，部分 started／finished 或下載 log 時間會倒退；**以檔名／輪次識別資料，不以這些時間戳推算下載總時長或跨輪排序**。
6. 排除暖機與多輪中間步驟後，共 684 個計分案例。Pi、代理較長回答與校準不併入此總數。沒有收錄未計分的 harness calibration 當成正式成績。
7. 只發布測試 JSON、CSV、必要環境快照與程式；移除本機使用者絕對路徑及憑證欄位，不附 API 金鑰、機器序號、UUID、下載權重或一般服務 log。原始回應內容及思考欄位保留供診斷，屬合成測試輸出。
8. [provenance.json](provenance.json) 記錄本機來源相對路徑、原始 SHA-256 與發布檔 SHA-256。發布版已做去識別化，因此其 hash 與本機原檔不同。

## 資料索引與重跑

- [run-summary.csv](run-summary.csv)／[JSON](run-summary.json)：21 輪摘要。
- [case-results.csv](case-results.csv)／[JSON](case-results.json)：684 個案例，含 API、輪次、通過與延遲。
- [results/](results/)：逐題提示、工具回應、模型原始回應及 usage。
- [environment/](environment/)：目前設定、固定 revision 及下載 manifest。
- [harness/](harness/)：實際評分邏輯的可攜版本，只調整 API 位址、金鑰檔案、輸出及 import 路徑。

請先在 oMLX 載入對應模型，設定可讀的私密金鑰檔案；環境變數裡填的是**金鑰檔案路徑**，不是金鑰值。模型 ID 必須與 `/v1/models` 相同。

```sh
export OMLX_BASE_URL=http://127.0.0.1:8005
export OMLX_API_KEY_FILE="$HOME/.omlx/api-key"
export BENCH_OUTPUT_DIR="$(mktemp -d)"
python3 harness/agent_suite.py NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit 0.95
```

上述基礎代理預設各 API 3 輪，會產生 36 個基礎案例。要精確重現新增三款的 24＋12 配置：

```sh
python3 harness/run_agent.py --model NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit --repeats 2 --advanced-repeats 1
```

重跑文字套件（每 API 一輪，24 個計分案例）：

```sh
python3 harness/benchmark_four_models.py --model gpt-oss-120b-mxfp4-bf16 --top-p 1.0 --repeats 1
```

測試會送出多次本機推論請求；進階工具是模擬工具，不會執行草稿建立、帳戶查詢等外部操作。歷史資料為既有成績，重跑只寫入 `BENCH_OUTPUT_DIR` 或預設的 `new-runs/`，不覆蓋已發布資料。

離線檢查本報告的 JSON、hash、摘要與案例總數：

```sh
python3 harness/verify_report.py
```
