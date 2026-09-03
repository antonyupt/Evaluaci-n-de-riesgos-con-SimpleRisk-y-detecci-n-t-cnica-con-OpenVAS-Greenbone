#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SI-084 · Auditoría de Sistemas · Semana 03
PT03 — Conversión de hallazgos técnicos en riesgos de negocio.

Toma la evidencia técnica levantada en el Paso C y la convierte en un registro
de riesgos con activo, dueño, probabilidad, impacto y nivel.

Fuentes de evidencia (las que existan en 20_evidencia/E03_scan/):
  1. reporte_greenbone.csv   — escáner Greenbone/OpenVAS (fuente primaria)
  2. nuclei_raw.jsonl        — escáner nuclei (alternativa autorizada por la guía)
  3. postgres_autenticado.txt — prueba autenticada manual sobre si084_db

REGLA CENTRAL DEL PAPEL DE TRABAJO
El CVSS mide explotabilidad técnica en abstracto. El riesgo mide la consecuencia
para ESTA organización. Por eso la severidad del escáner solo alimenta la
PROBABILIDAD, y el IMPACTO lo determina el valor del activo, nunca el escáner.
"""

import csv
import json
import os
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EVID = BASE / "20_evidencia" / "E03_scan"
OUT = BASE / "40_hallazgos"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# CONTEXTO DE NEGOCIO: sin esto, el CVSS no significa nada.
# Declarado ANTES de mirar los resultados del escaneo.
# ---------------------------------------------------------------------------
ACTIVOS = {
    "si084_db": dict(
        ip="172.20.0.4", nombre="Base de datos ERP", dueno="Gerencia de Finanzas",
        clasificacion="Restringida", expuesto=False, criticidad=5),
    "si084_juiceshop": dict(
        ip="172.20.0.3", nombre="Portal de clientes", dueno="Gerencia Comercial",
        clasificacion="Confidencial", expuesto=True, criticidad=4),
    "si084_portal": dict(
        ip="172.20.0.5", nombre="Portal corporativo", dueno="Gerencia Comercial",
        clasificacion="Pública", expuesto=True, criticidad=2),
    "si084_dvwa": dict(
        ip="172.20.0.2", nombre="App legada interna", dueno="Gerencia de Operaciones",
        clasificacion="Interna", expuesto=False, criticidad=3),
}
POR_IP = {a["ip"]: (k, a) for k, a in ACTIVOS.items()}


def activo_de(host: str):
    """Resuelve un host (IP, IP:puerto o URL) al activo de negocio declarado."""
    if not host:
        return None, None
    m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", str(host))
    if m and m.group(1) in POR_IP:
        return POR_IP[m.group(1)]
    for k, a in ACTIVOS.items():
        if k in str(host):
            return k, a
    return None, None


# ---------------------------------------------------------------------------
# ESCALAS — las mismas registradas en SimpleRisk antes de evaluar
# ---------------------------------------------------------------------------
def probabilidad(cvss: float, expuesto: bool) -> int:
    """La exposición a Internet eleva la probabilidad de explotación."""
    base = 1 if cvss < 4 else 2 if cvss < 7 else 3 if cvss < 9 else 4
    return min(5, base + (1 if expuesto else 0))


def impacto(criticidad: int, clasificacion: str) -> int:
    """El impacto lo determina el valor del activo, no la severidad técnica."""
    extra = {"Restringida": 1, "Confidencial": 0, "Interna": 0, "Pública": -1}
    return max(1, min(5, criticidad + extra.get(clasificacion, 0)))


def nivel(v: int) -> str:
    return "Crítico" if v >= 20 else "Alto" if v >= 12 else "Medio" if v >= 6 else "Bajo"


# Severidad nominal de nuclei -> CVSS representativo, cuando la plantilla no trae score
SEV_A_CVSS = {"critical": 9.8, "high": 7.5, "medium": 5.3, "low": 3.1, "info": 0.0}

hallazgos = []   # (fuente, host, nvt, cve, cvss)

# --- FUENTE 1: Greenbone / OpenVAS -----------------------------------------
g = EVID / "reporte_greenbone.csv"
if g.exists():
    with open(g, newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            try:
                cvss = float(r.get("CVSS") or r.get("Severity") or 0)
            except ValueError:
                cvss = 0.0
            if cvss < 4.0:          # se descartan los informativos
                continue
            hallazgos.append((
                "Greenbone",
                r.get("IP") or r.get("Host") or "",
                (r.get("NVT Name") or "").strip(),
                (r.get("CVEs") or "N/D").strip() or "N/D",
                cvss,
            ))

# --- FUENTE 2: nuclei -------------------------------------------------------
n = EVID / "nuclei_raw.jsonl"
if n.exists():
    vistos = set()
    with open(n, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            info = d.get("info", {}) or {}
            sev = info.get("severity", "info")
            clas = info.get("classification") or {}
            cvss = clas.get("cvss-score") or SEV_A_CVSS.get(sev, 0.0)
            try:
                cvss = float(cvss)
            except (TypeError, ValueError):
                cvss = SEV_A_CVSS.get(sev, 0.0)
            if cvss < 4.0:
                continue
            cves = clas.get("cve-id") or []
            cve = cves[0].upper() if isinstance(cves, list) and cves else "N/D"
            clave = (d.get("host", ""), d.get("template-id", ""))
            if clave in vistos:      # el escáner repite plantilla por endpoint
                continue
            vistos.add(clave)
            hallazgos.append((
                "nuclei", d.get("host", ""),
                info.get("name", d.get("template-id", "")), cve, cvss,
            ))

# --- FUENTE 3: prueba autenticada sobre si084_db ----------------------------
# Verificada manualmente en el Paso C; el escáner no autenticado no la alcanza.
p = EVID / "postgres_autenticado.txt"
if p.exists():
    txt = p.read_text(encoding="utf-8", errors="replace")
    if "AUTENTICACION EXITOSA CON CREDENCIAL POR DEFECTO" in txt:
        hallazgos.append(("Prueba autenticada", "172.20.0.4",
                          "Credencial por defecto válida en PostgreSQL (postgres/postgres)",
                          "N/D", 9.8))
    if "md5 (DEBIL)" in txt:
        hallazgos.append(("Prueba autenticada", "172.20.0.4",
                          "Contraseñas almacenadas con md5 en lugar de scram-sha-256",
                          "N/D", 4.3))
    if "EN CLARO - SIN TLS" in txt:
        hallazgos.append(("Prueba autenticada", "172.20.0.4",
                          "Transmisión en claro: TLS no forzado en PostgreSQL (ssl=off)",
                          "CVE-2021-23214", 5.9))
    if re.search(r"^\s*host all all all md5", txt, re.M):
        hallazgos.append(("Prueba autenticada", "172.20.0.4",
                          "pg_hba.conf acepta md5 desde cualquier host de la red",
                          "N/D", 5.0))
    if "usesuper" in txt and re.search(r"postgres.*\|\s*t\s*$", txt, re.M):
        hallazgos.append(("Prueba autenticada", "172.20.0.4",
                          "La cuenta de servicio de la aplicación es superusuario",
                          "N/D", 7.2))

# ---------------------------------------------------------------------------
# AJUSTES DE AUDITORÍA (ISO/IEC 27005:2022 §7 — el juicio del evaluador
# se admite, pero debe quedar explícito y trazable).
# Clave: fragmento del nombre del hallazgo. Valor: (probabilidad, justificación).
# ---------------------------------------------------------------------------
AJUSTES = {
    "TLS no forzado": (
        4,
        "La fórmula automática asigna P=2 porque no modela rutas de movimiento "
        "lateral. si084_juiceshop está expuesto y comparte la red audit_net con "
        "si084_db: el compromiso del portal (ya calificado Crítico) coloca al "
        "atacante en la posición de adyacencia que esta vulnerabilidad requiere, "
        "y las credenciales del ERP viajan en claro. P real = 4."),
}

filas = []
for fuente, host, nvt, cve, cvss in hallazgos:
    clave, a = activo_de(host)
    if not a:
        continue
    p_auto = probabilidad(cvss, a["expuesto"])
    i = impacto(a["criticidad"], a["clasificacion"])
    v_auto = p_auto * i

    p_fin, just = p_auto, ""
    for patron, (p_aj, motivo) in AJUSTES.items():
        if patron.lower() in nvt.lower():
            p_fin, just = p_aj, motivo
            break
    v_fin = p_fin * i

    filas.append({
        "id_riesgo": "",
        "fuente_evidencia": fuente,
        "host": host,
        "contenedor": clave,
        "activo": a["nombre"],
        "dueno_del_riesgo": a["dueno"],
        "clasificacion": a["clasificacion"],
        "expuesto": "Sí" if a["expuesto"] else "No",
        "amenaza": "Explotación remota de vulnerabilidad conocida",
        "vulnerabilidad": nvt,
        "cve": cve,
        "cvss": cvss,
        "probabilidad": p_auto,
        "impacto": i,
        "riesgo_inherente": v_auto,
        "nivel": nivel(v_auto),
        "probabilidad_ajustada": p_fin,
        "riesgo_ajustado": v_fin,
        "nivel_ajustado": nivel(v_fin),
        "justificacion_ajuste": just,
    })

filas.sort(key=lambda r: (-r["riesgo_ajustado"], -r["cvss"]))
for idx, r in enumerate(filas, 1):
    r["id_riesgo"] = f"R-{idx:03d}"

destino = OUT / "PT03_registro_riesgos.csv"
with open(destino, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
    w.writeheader()
    w.writerows(filas)

# ---------------------------------------------------------------------------
# Salida por consola (queda como evidencia en docs/evidencias/S03/salidas/)
# ---------------------------------------------------------------------------
print(f"Registro de riesgos generado: {destino}")
print(f"Riesgos registrados: {len(filas)}\n")

cab = f'{"ID":6} {"ACTIVO":20} {"DUENO":24} {"CVSS":5} {"P":2} {"I":2} {"VAL":4} {"NIVEL":8} VULNERABILIDAD'
print(cab)
print("-" * len(cab))
for r in filas:
    print(f'{r["id_riesgo"]:6} {r["activo"][:20]:20} {r["dueno_del_riesgo"][:24]:24} '
          f'{r["cvss"]:<5} {r["probabilidad_ajustada"]:<2} {r["impacto"]:<2} '
          f'{r["riesgo_ajustado"]:<4} {r["nivel_ajustado"]:8} {r["vulnerabilidad"][:52]}')

print("\nDistribución por nivel (tras el ajuste de auditoría):")
dist = {}
for r in filas:
    dist[r["nivel_ajustado"]] = dist.get(r["nivel_ajustado"], 0) + 1
for k in ("Crítico", "Alto", "Medio", "Bajo"):
    if k in dist:
        print(f"  {k:8} {dist[k]}")

print("\nEvidencia por fuente:")
fu = {}
for r in filas:
    fu[r["fuente_evidencia"]] = fu.get(r["fuente_evidencia"], 0) + 1
for k, v in sorted(fu.items()):
    print(f"  {k:20} {v}")

print("\nAjustes de auditoría aplicados:")
for r in filas:
    if r["justificacion_ajuste"]:
        print(f'  {r["id_riesgo"]}: {r["riesgo_inherente"]} ({r["nivel"]}) -> '
              f'{r["riesgo_ajustado"]} ({r["nivel_ajustado"]})')
