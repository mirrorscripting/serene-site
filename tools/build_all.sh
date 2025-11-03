#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p downloads/13
source ~/calenv/bin/activate

python3 tools/serene_13month_2026_production.py --variant core   --out downloads/13/core-2026-v1.pdf    --cfg tools/palettes_2026.json --text tools/text_2026.yml
python3 tools/serene_13month_2026_production.py --variant deluxe --out downloads/13/deluxe-2026-wgbs-v1.pdf --cfg tools/palettes_2026.json --text tools/text_2026.yml
python3 tools/serene_13month_2026_production.py --variant neon   --out downloads/13/colorpop-2026-v1.pdf --cfg tools/palettes_2026.json --text tools/text_2026.yml

google-chrome "file://$HOME/serene-site/downloads/13/core-2026-v1.pdf" \
               "file://$HOME/serene-site/downloads/13/deluxe-2026-wgbs-v1.pdf" \
               "file://$HOME/serene-site/downloads/13/colorpop-2026-v1.pdf" >/dev/null 2>&1 &
echo "Opened all three in Chrome."
