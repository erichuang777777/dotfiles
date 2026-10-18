# Dotfiles & Cloud VPS Bootstrap

借鑑經典 dotfiles 架構，將「安裝環境 (Bootstrap)」與「掛載設定 (Dotfiles Link)」分離，並使用「軟連結 (Symlink)」來達到系統設定與 Git 即時連動的自動化初始化環境與設定檔。

## 架構說明

- `os/`: 平台專屬的套件安裝腳本（只跑一次，例如 `os/ubuntu.sh`）
- `shell/`: 終端設定，共用別名及本機私密環境變數範本 (`.bashrc.local.example`)
- `tools/`: 開發工具設定檔 (`.tmux.conf`, `daemon.json`, `.gitconfig`)
- `dot_ssh/config`: SSH 主機設定，`gb10` 與 `gb-10` 使用 `altos` 帳號
- `services/`: 隨插即用的 Docker Compose 服務模組
- `install.sh`: 核心掛載腳本，負責建立 Symlink

## 快速使用

新機器開箱時，取得專案：
```bash
git clone https://github.com/<你的GitHub帳號>/vps-bootstrap.git ~/vps-bootstrap
cd ~/vps-bootstrap
```

### 第一步：安裝環境套件（以 Ubuntu 為例）
只在機器剛開箱時跑一次：
```bash
chmod +x os/ubuntu.sh
./os/ubuntu.sh
```

### 第二步：建立軟連結設定
掛載並連結設定檔：
```bash
chmod +x install.sh
./install.sh
```

安裝腳本會將 `~/.ssh/config` 連結至 `dot_ssh/config`；原有設定會先備份到 `~/.dotfiles-ssh-backup.XXXXXXXX/config`。之後執行 `ssh gb10` 即會使用 `altos` 帳號。其他主機的 `IdentityFile` 請依本機私鑰路徑調整。

### 隱私設定與私鑰
安裝腳本會自動產生一份 `~/.bashrc.local`，請將您單機專用的金鑰（如 API Key）放在此處，此檔案不會被 Git 追蹤。
