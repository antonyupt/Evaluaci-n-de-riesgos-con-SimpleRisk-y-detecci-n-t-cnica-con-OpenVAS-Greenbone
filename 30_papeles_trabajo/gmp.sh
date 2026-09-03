#!/usr/bin/env bash
# SI-084 · Semana 03 — Envoltorio para hablar GMP con Greenbone desde el host.
#   uso:  ./gmp.sh '<get_version/>'
set -euo pipefail
cd "$(dirname "$0")/../entorno/greenbone"
export DOWNLOAD_DIR="${DOWNLOAD_DIR:-$HOME/greenbone-community-container}"
MSYS_NO_PATHCONV=1 docker compose -p greenbone-community-edition run --rm -T gvm-tools \
  gvm-cli --gmp-username admin --gmp-password SI084_lab_2026 \
  socket --socketpath //run/gvmd/gvmd.sock --xml "$1" 2>/dev/null
