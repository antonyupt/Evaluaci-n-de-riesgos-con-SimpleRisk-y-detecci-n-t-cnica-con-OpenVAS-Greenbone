import pandas as pd, json, re, glob

filas = []

# --- Lynis ---
for l in open("../20_evidencia/E04_config/lynis-report.dat"):
    if l.startswith("warning[]=") or l.startswith("suggestion[]="):
        tipo = "warning" if l.startswith("warning") else "suggestion"
        filas.append(dict(herramienta="Lynis", severidad="Alta" if tipo=="warning" else "Media",
                          hallazgo=l.split("=",1)[1].strip()[:160]))

# --- OpenSCAP (reglas fallidas) ---
import xml.etree.ElementTree as ET
try:
    ns = {'xccdf': 'http://checklists.nist.gov/xccdf/1.2'}
    tree = ET.parse("../20_evidencia/E04_config/oscap-resultados.xml")
    for rule_result in tree.iter('{http://checklists.nist.gov/xccdf/1.2}rule-result'):
        result = rule_result.find('{http://checklists.nist.gov/xccdf/1.2}result')
        if result is not None and result.text == 'fail':
            filas.append(dict(herramienta="OpenSCAP", severidad="Alta",
                              hallazgo=rule_result.get('idref')[:160]))
except Exception as e:
    print("Aviso OpenSCAP:", e)

# --- Docker Bench ---
for l in open("../20_evidencia/E04_config/docker-bench-clean.log"):
    if l.startswith("[WARN]"):
        filas.append(dict(herramienta="Docker Bench", severidad="Alta",
                          hallazgo=l.replace("[WARN]","").strip()[:160]))

# --- Trivy imágenes ---
for f in glob.glob("../20_evidencia/E04_config/trivy_*.json"):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    for res in d.get("Results", []) or []:
        for v in res.get("Vulnerabilities", []) or []:
            filas.append(dict(herramienta="Trivy", severidad=v["Severity"].capitalize(),
                              hallazgo=f'{v["VulnerabilityID"]} en {v["PkgName"]} {v.get("InstalledVersion","")}'))

m = pd.DataFrame(filas)

MAPEO = [
    (r"root|privileg|capab",              "A.8.2 Privileged access rights",        "DSS05.04"),
    (r"password|credential|secret|auth",  "A.5.17 Authentication information",     "DSS05.04"),
    (r"CVE-|vulnerab|outdated|version",   "A.8.8 Management of technical vulnerabilities", "DSS05.07"),
    (r"log|audit|journal",                "A.8.15 Logging",                        "DSS01.03"),
    (r"tls|ssl|cipher|encrypt|certificate","A.8.24 Use of cryptography",           "DSS05.03"),
    (r"firewall|port|network|expose",     "A.8.20 Networks security",              "DSS05.02"),
    (r"config|default|hardening|umask|pam|permission",  "A.8.9 Configuration management", "BAI10.02"),
    (r"backup|restore",                   "A.8.13 Information backup",             "DSS04.07"),
    (r"healthcheck|pids|cgroup",          "A.8.16 Monitoring activities",          "DSS01.03"),
]
def clasifica(t):
    for pat, iso, cobit in MAPEO:
        if re.search(pat, t, re.I):
            return pd.Series([iso, cobit])
    return pd.Series(["Sin clasificar", "Sin clasificar"])

m[["control_iso27001","objetivo_cobit"]] = m["hallazgo"].apply(clasifica)
m.to_csv("../40_hallazgos/PT04_matriz_control.csv", index=False)

print("Hallazgos por herramienta:\n", m.groupby(["herramienta","severidad"]).size().to_string())
print("\nHallazgos por control ISO:\n", m["control_iso27001"].value_counts().to_string())
print(f"\nSin clasificar: {(m.control_iso27001=='Sin clasificar').sum()} "
      f"({(m.control_iso27001=='Sin clasificar').mean():.0%}) — revisar manualmente")