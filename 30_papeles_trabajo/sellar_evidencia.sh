#!/usr/bin/env bash
# SI-084 · Semana 03 — Sellado de la evidencia y cadena de custodia digital.
#
# Fija criptográficamente el contenido de cada archivo de evidencia en el
# momento de su obtención. Cualquier alteración posterior se detecta con
#     sha256sum -c 20_evidencia/SHA256SUMS_E03.txt
set -euo pipefail
cd "$(dirname "$0")/.."

SUMS="20_evidencia/SHA256SUMS_E03.txt"

{
  echo "# SI-084 · Auditoría de Sistemas · Semana 03"
  echo "# CADENA DE CUSTODIA DIGITAL — evidencia del taller de laboratorio 03"
  echo "# Sellado: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "# Alcance del escaneo: red Docker audit_net, según 20_evidencia/E03_scan/objetivos.txt"
  echo "# Verificación: sha256sum -c $SUMS"
  echo "#"
} > "$SUMS"

sha256sum \
  20_evidencia/E03_scan/* \
  40_hallazgos/PT03_registro_riesgos.csv \
  30_papeles_trabajo/PT03_tecnico_a_riesgo.py \
  30_papeles_trabajo/PT03_soa_extracto.md \
  docs/evidencias/S03/*.png \
  2>/dev/null >> "$SUMS"

echo "Sellados $(grep -c '^[0-9a-f]' "$SUMS") archivos en $SUMS"
echo
sha256sum -c "$SUMS" 2>/dev/null | sed 's/^/  /'
