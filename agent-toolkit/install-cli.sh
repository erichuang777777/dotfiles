#!/bin/sh
set -eu
# Explicit tool installation; does not sign in, publish, or provision cloud resources.
npm install --global --prefix "$HOME/.local" netlify-cli@27.13.0 wrangler@4.151.1 @googleworkspace/cli@0.22.5 @google/gemini-cli@0.64.0 @colbymchenry/codegraph@1.6.2 @21st-dev/cli@1.18.0 hyperframes@0.8.170 @open-document/cli@0.2.1
uv tool install google-colab-cli==0.7.4
uv tool install clauder-mcp==0.16.1
uv tool install "scrapling[ai,shell]==0.5"
printf '%s\n' 'GitHub CLI：brew install gh' 'R 與 RStudio：brew install r && brew install --cask rstudio' 'R 套件與 MCP 設定請參照 cloud-and-research.md。'
