#!/usr/bin/env bash
# Instala dependências: pycairo, numpy, fontes (ffmpeg precisa existir no sistema)
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q pycairo numpy 2>/dev/null || pip install -q pycairo numpy
mkdir -p ~/.fonts && cp fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null
command -v ffmpeg >/dev/null || echo "ATENÇÃO: instale o ffmpeg"
echo "ok"
