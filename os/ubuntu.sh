#!/usr/bin/env bash
set -e

echo "==> [1/7] 時區設定與系統更新"
sudo timedatectl set-timezone Asia/Taipei
sudo apt update && sudo apt upgrade -y
sudo apt install -y git tmux jq ripgrep btop ncdu unzip curl wget

echo "==> [2/7] 清理 Oracle 預設 iptables 防火牆"
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -F
sudo apt install -y iptables-persistent netfilter-persistent
sudo netfilter-persistent save

echo "==> [3/7] 安裝 Docker & Docker Compose"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    # 複製防日誌膨脹設定
    if [ -f "../tools/daemon.json" ]; then
        sudo cp ../tools/daemon.json /etc/docker/daemon.json
    fi
    sudo systemctl restart docker
fi

echo "==> [4/7] 安裝 Node.js 22 LTS 與 全域 CLI"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt install -y nodejs
fi
sudo npm install -g pnpm @anthropic-ai/claude-code netlify-cli

echo "==> [5/7] 安裝 uv 與 Python CLI 工具"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
# 使用 uv 隔離安裝命令列工具
uv tool install antigravity-cli 2>/dev/null || true

echo "==> [6/7] 安裝 Playwright 核心與相依環境"
mkdir -p "$HOME/playwright-env" && cd "$HOME/playwright-env"
npm init -y > /dev/null 2>&1
npm install playwright
npx playwright install --with-deps chromium
cd - > /dev/null

echo "==> [7/7] 安裝 GitHub CLI 與 Tailscale"
# GitHub CLI
if ! command -v gh &> /dev/null; then
    sudo mkdir -p -m 755 /etc/apt/keyrings
    wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
    sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update && sudo apt install gh -y
fi

# Tailscale
if ! command -v tailscale &> /dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
fi

echo "============================================="
echo " Ubuntu 基礎環境安裝完成！"
echo " 接下來請執行 ./install.sh 進行環境設定檔的連結。"
echo " 執行 'tailscale up' 以連結私人內網。"
echo "============================================="
