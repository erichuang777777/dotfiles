#!/usr/bin/env bash
set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> 建立設定檔軟連結 (Symlinks)..."

# 1. 連結 tmux 設定
ln -sf "$DOTFILES_DIR/tools/.tmux.conf" "$HOME/.tmux.conf"

# 2. 連結自訂 Shell 設定
if ! grep -q "bashrc_custom" "$HOME/.bashrc" 2>/dev/null; then
    echo "source $DOTFILES_DIR/shell/.bashrc_custom" >> "$HOME/.bashrc"
fi

# 3. 如果本地還沒有 .bashrc.local，建立一個空白範本
if [ ! -f "$HOME/.bashrc.local" ]; then
    cp "$DOTFILES_DIR/shell/.bashrc.local.example" "$HOME/.bashrc.local" 2>/dev/null || touch "$HOME/.bashrc.local"
    echo "==> 已建立 ~/.bashrc.local，私密環境變數請放在此檔案中。"
fi

echo "==> 建立自訂設定檔案目錄與檔案連結..."
# 可以繼續加入其他的連結，例如 gitconfig
ln -sf "$DOTFILES_DIR/tools/.gitconfig" "$HOME/.gitconfig"

echo "==> 設定檔掛載完成！"
