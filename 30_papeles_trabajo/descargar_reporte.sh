#!/usr/bin/env bash
# SI-084 · Semana 03 — Descarga del reporte de Greenbone en CSV y XML.
#   uso:  ./descargar_reporte.sh <report_id>
set -euo pipefail
cd "$(dirname "$0")"
RID="${1:?Falta el report_id}"
OUT="../20_evidencia/E03_scan"

# Formatos de reporte estándar de Greenbone
CSV="c1645568-627a-11e3-a660-406186ea4fc5"   # CSV Results
XML="a994b278-1f62-11e1-96ac-406186ea4fc5"   # XML

echo "Descargando reporte CSV..."
./gmp.sh "<get_reports report_id=\"$RID\" format_id=\"$CSV\" details=\"1\"/>" \
  | python -c "import sys,re,base64; x=sys.stdin.read(); m=re.search(r'format=\"CSV\"[^>]*>([A-Za-z0-9+/=]+)</report>', x, re.S); open('$OUT/reporte_greenbone.csv','wb').write(base64.b64decode(m.group(1))) if m else print('CSV no encontrado')"

echo "Descargando reporte XML..."
./gmp.sh "<get_reports report_id=\"$RID\" format_id=\"$XML\" details=\"1\"/>" \
  > "$OUT/reporte_greenbone.xml"

echo "Listo:"
ls -la "$OUT"/reporte_greenbone.* 2>/dev/null
