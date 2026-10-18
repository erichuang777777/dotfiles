# 1Password：密碼與 API 金鑰管理

使用者已有付費 1Password，沿用既有帳號。此項不建立新帳號或訂閱，也不安裝另一套 Bitwarden。

## 安裝

```sh
brew install --cask 1password 1password-cli
op --version
```

桌面版與 CLI 的實際安裝版本、驗證範圍見 `1password-verification.json`。本次不讀取、匯出或遷移任何既有密碼、API 金鑰或保管庫內容。

## 首次設定：由使用者操作

1. 開啟 1Password，登入既有帳號並解鎖。
2. 到「Settings → Developer」勾選「Integrate with 1Password CLI」。
3. 在自己使用的終端機執行 `op whoami`，依提示授權。

若 macOS 27 出現「No accounts configured」，依官方排錯文件檢查「系統設定 → 隱私權與安全性 → 檔案與檔案夾」中的 1Password 共享資料權限；本次沒有代為變更這些權限。

官方指引：[桌面版與 CLI 整合](https://developer.1password.com/docs/cli/app-integration/)。

## API 金鑰

建議另建 `Agent-Development` 保管庫，儲存開發用途與有限權限的金鑰。正式環境金鑰另外管理。這是建議名稱，本次沒有替使用者建立保管庫。

在專案內以參照取代明文金鑰，例如 `.env.op`：

```dotenv
PROVIDER_API_KEY=op://Agent-Development/provider/api-key
```

以上為範例參照，需換成實際項目的保管庫、項目及欄位參照。然後只對需要金鑰的程式注入：

```sh
op run --env-file=.env.op -- your-command
```

實際金鑰會出現在子程序的環境中；這不是防止該程序或其 Agent 讀取金鑰的隔離機制。不要把完整保管庫內容、`op read` 的輸出或解密後設定放入聊天、日誌與公開 dotfiles。

官方指引：[執行時注入金鑰](https://developer.1password.com/docs/cli/secrets-scripts/)。

## 驗證範圍

僅驗證桌面版安裝、CLI 版本與不需登入的指令說明。登入、桌面版 CLI 整合與實際金鑰注入，需使用者完成首次設定後才可驗證。沒有將密碼庫註冊成可任意讀取所有項目的 MCP 工具。
