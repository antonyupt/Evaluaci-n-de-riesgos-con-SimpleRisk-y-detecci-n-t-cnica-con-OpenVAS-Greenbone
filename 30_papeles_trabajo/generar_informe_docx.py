#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el informe EPIS del Taller 03 en Word (.docx) con las capturas."""
import csv
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parent
IMG = BASE / "docs" / "evidencias" / "S03"
REG = BASE / "40_hallazgos" / "PT03_registro_riesgos.csv"
LOGO_U = ROOT / "Logos" / "logo_universidad.png"
LOGO_E = ROOT / "Logos" / "logo_escuela_sistemas.jpeg"
OUT = ROOT / "SI084-S03-TALLER-Chata-Choque.docx"

GITHUB = "https://github.com/antonyupt/Evaluaci-n-de-riesgos-con-SimpleRisk-y-detecci-n-t-cnica-con-OpenVAS-Greenbone"

NAVY = RGBColor(0x16, 0x28, 0x5C)
rows = list(csv.DictReader(open(REG, encoding="utf-8")))

doc = Document()
# Estilo base
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(6)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.color.rgb = NAVY
    return p


def para(text="", bold=False, italic=False, align=None, size=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    if align:
        p.alignment = align
    return p


def cebra_tabla(headers, data, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, hh in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(hh)
        r.bold = True
        r.font.size = Pt(9)
    for row in data:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val))
            r.font.size = Pt(9)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    return t


def imagen(nombre, titulo, ancho=6.2):
    fp = IMG / nombre
    if fp.exists():
        doc.add_picture(str(fp), width=Inches(ancho))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = para(titulo, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=9)


# ===================== CARÁTULA =====================
tbl = doc.add_table(rows=1, cols=2)
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
c1, c2 = tbl.rows[0].cells
if LOGO_U.exists():
    c1.paragraphs[0].add_run().add_picture(str(LOGO_U), height=Inches(0.9))
    c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
if LOGO_E.exists():
    c2.paragraphs[0].add_run().add_picture(str(LOGO_E), height=Inches(0.9))
    c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

para()
para("UNIVERSIDAD PRIVADA DE TACNA", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=15)
para("FACULTAD DE INGENIERÍA", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=13)
para("ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
para()
para()
para("INFORME DE LABORATORIO N.º 03", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=16)
para("AUDITORÍA DE SISTEMAS · SI-084", align=WD_ALIGN_PARAGRAPH.CENTER, size=13)
para()
para("Evaluación de riesgos con SimpleRisk y detección técnica con OpenVAS/Greenbone",
     bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=13)
para()
para("Semana N.º 03 · Unidad I", align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
para()
para("Autor", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("Chata Choque, Brant Antony — Código bc2020067577", align=WD_ALIGN_PARAGRAPH.CENTER)
para()
para("Docente", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("Dr. Oscar Juan Jimenez Flores", align=WD_ALIGN_PARAGRAPH.CENTER)
para()
para("Repositorio del trabajo (GitHub):", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10)
para(GITHUB, align=WD_ALIGN_PARAGRAPH.CENTER, size=9)
para()
para("Tacna — Perú · 2026", align=WD_ALIGN_PARAGRAPH.CENTER, size=12)

doc.add_page_break()

# ===================== 1. INFORMACIÓN =====================
h("1. Información sobre el evento práctico", 1)

h("1.1 Título del evento práctico", 2)
para("Apreciación y tratamiento del riesgo de seguridad de la información sobre el entorno "
     "auditado si084-lab, alimentada por evidencia técnica de vulnerabilidades obtenida con "
     "reconocimiento nmap, escaneo no autenticado con nuclei, prueba autenticada sobre la base "
     "de datos y detección con Greenbone/OpenVAS, y registrada en SimpleRisk Community. El eje "
     "del trabajo es la conversión de un hallazgo técnico en un riesgo de negocio con activo, "
     "dueño, probabilidad e impacto trazables, y su cierre en un extracto de Declaración de "
     "Aplicabilidad (SoA) conforme a la NTP-ISO/IEC 27001:2022.")

h("1.2 Objetivos", 2)
para("Objetivo general.", bold=True)
para("Ejecutar un ciclo completo de apreciación y tratamiento del riesgo de seguridad de la "
     "información sobre el entorno auditado, sustentado en evidencia técnica verificable y con "
     "trazabilidad hasta los controles del Anexo A de la ISO/IEC 27001:2022.")
para("Objetivos específicos.", bold=True)
for o in [
    "Desplegar SimpleRisk Community y Greenbone Community Edition (OpenVAS) sobre Docker, en la red aislada audit_net.",
    "Ejecutar un escaneo autenticado y no autenticado de vulnerabilidades sobre el entorno si084-lab, dentro del alcance autorizado.",
    "Interpretar los resultados en términos de CVE, CVSS v3.1 y vector de ataque, distinguiendo la severidad técnica del riesgo de negocio.",
    "Convertir los hallazgos técnicos en riesgos de negocio con activo, amenaza, vulnerabilidad, probabilidad, impacto y dueño.",
    "Construir la matriz de riesgo inherente y residual y el plan de tratamiento.",
    "Elaborar un extracto de Declaración de Aplicabilidad (SoA), con al menos un control excluido con justificación.",
    "Sellar la evidencia con SHA-256 y versionarla en Git.",
]:
    doc.add_paragraph(o, style="List Bullet")

h("1.3 Tiempo de duración", 2)
para("100 minutos de laboratorio: 60 de taller guiado (Pasos A–E) y 40 de avance asistido.")

h("1.4 Resultados de aprendizaje", 2)
cebra_tabla(
    ["Código", "Resultado de aprendizaje", "Cómo se evidencia"],
    [["RA1", "Analiza e interpreta los conceptos y terminología de Auditoría de Sistemas",
      "Uso diferenciado de activo, amenaza, vulnerabilidad, riesgo inherente/residual, criterio de aceptación y dueño del riesgo"],
     ["RA2", "Evalúa la seguridad de la información en Auditoría de Sistemas",
      "Registro de 48 riesgos valorados, matriz inherente/residual, plan de tratamiento y SoA mapeado al Anexo A de la ISO/IEC 27001:2022"]],
    widths=[0.7, 2.6, 3.0])

h("1.5 Recursos", 2)
cebra_tabla(
    ["Recurso", "Versión", "Para qué se usó"],
    [["Docker Engine + Compose", "29.6.1 · Compose v5.2.0", "Motor de contenedores del entorno y de las herramientas"],
     ["Greenbone Community Containers", "GSA 28.3.0 · GVMD 26.37.1 · GMP 22.7", "Detección de vulnerabilidades con CVE y CVSS"],
     ["SimpleRisk Community", "simplerisk/simplerisk:latest", "Registro, evaluación, tratamiento y riesgo residual"],
     ["MariaDB", "11", "Base de datos de respaldo"],
     ["nmap", "7.98", "Reconocimiento de servicios y versiones"],
     ["nuclei", "3.11.1", "Escaneo no autenticado con severidad y CVE"],
     ["Python + pandas", "3.12.4 + 3.0.5", "Papel de trabajo de conversión técnico→riesgo"],
     ["Git", "2.55.0", "Versionado y cadena de custodia"],
     ["ISO/IEC 27001:2022 — Anexo A", "Edición 2022", "Marco de referencia del SoA"]],
    widths=[2.0, 2.2, 2.1])

h("1.6 Seguridad", 2)
for s in [
    "Alcance cerrado. El escaneo se ejecutó exclusivamente contra la red Docker audit_net (subred 172.20.0.0/16). No se dirigió tráfico hacia el campus ni hacia direcciones públicas. Escanear fuera de ese alcance constituye acceso no autorizado, tipificado en la Ley 30096 (art. 2), modificada por la Ley 30171.",
    "Verificación previa. Se ejecutó docker network inspect audit_net y se registró el rango exacto y las IP objetivo en objetivos.txt antes de lanzar cualquier prueba.",
    "Puertos aislados. Todos los servicios se publicaron solo en 127.0.0.1, nunca en 0.0.0.0. Las aplicaciones deliberadamente vulnerables (Juice Shop, DVWA) no se expusieron fuera del equipo.",
    "Credenciales de laboratorio. El escaneo autenticado usó únicamente credenciales del laboratorio; en ningún momento credenciales reales.",
    "Clasificación de la evidencia. Los reportes se tratan como Confidencial: no se publican en repositorios abiertos.",
]:
    doc.add_paragraph(s, style="List Number")

doc.add_page_break()

# ===================== 2. PROCEDIMIENTO =====================
h("2. Procedimiento o metodología", 1)

h("Paso A — Desplegar Greenbone e iniciar la sincronización", 2)
para("Se desplegó la pila de Greenbone Community Edition (16 contenedores) con Docker Compose y "
     "se creó el usuario administrador. La interfaz quedó disponible en http://127.0.0.1:9392. "
     "El feed NVT llegó a estado Current y los feeds SCAP, CERT y GVMD_DATA completaron la "
     "sincronización (más de 385 000 CVE importados; base de datos de 19 GB), tras lo cual se "
     "cargaron 186 134 pruebas de vulnerabilidad (VT) y las configuraciones de escaneo.")
para("Observación de campo: la URL del docker-compose que indica la documentación "
     "(…/docker-compose-22.4.yml) devuelve HTTP 404; la URL vigente es …/docker-compose.yml. "
     "Además, el nginx de Greenbone se remapeó del puerto 443 al 9443 por estar ocupado en el equipo.", italic=True)
imagen("01_greenbone_feed_status.png", "Figura 1. Estado de los feeds de Greenbone (NVT Current).")

h("Paso B — Desplegar SimpleRisk y fijar el criterio", 2)
para("Se desplegaron los servicios de SimpleRisk (acceso en http://127.0.0.1:8083) y, antes de "
     "evaluar ningún riesgo, se fijó el criterio: método Classic (Likelihood × Impact) "
     "normalizado a 0–10; escalas 1–5 con su definición operativa escrita; y criterio de "
     "aceptación en 6/25 (riesgo ≤ 6 aceptable con firma del dueño; > 6 exige tratamiento con "
     "plazo). Niveles: Bajo < 6, Medio 6–11, Alto 12–19, Crítico ≥ 20. Se crearon los cuatro "
     "dueños de riesgo por área.")
cebra_tabla(
    ["Probabilidad", "Definición operativa", "Impacto", "Definición operativa"],
    [["1 Muy baja", "< 1 vez cada 5 años", "1 Insignificante", "Sin efecto; se corrige en horas"],
     ["2 Baja", "1 vez cada 2–5 años", "2 Menor", "Interrupción < 4 h; sin efecto en clientes"],
     ["3 Media", "1 vez al año", "3 Moderado", "Interrupción 4–24 h; reclamos"],
     ["4 Alta", "Varias veces al año", "4 Mayor", "Interrupción > 24 h; pérdida económica"],
     ["5 Muy alta", "Mensual o más", "5 Catastrófico", "Continuidad comprometida; sanción"]],
    widths=[1.3, 1.9, 1.4, 1.9])
imagen("02_simplerisk_escalas_y_criterio.png", "Figura 2. Escalas 1–25 y criterio de aceptación en SimpleRisk.")
imagen("03_simplerisk_formula_classic.png", "Figura 3. Fórmula Classic (Likelihood × Impact) normalizada.")
imagen("04_simplerisk_duenos_de_riesgo.png", "Figura 4. Dueños de riesgo por área.")

h("Paso C — Escaneo de vulnerabilidades", 2)
para("El alcance se registró en objetivos.txt antes de escanear:")
cebra_tabla(
    ["Contenedor", "IP", "Servicio (nmap 7.98)", "Activo de negocio"],
    [["si084_db", "172.20.0.4", "PostgreSQL 13.23 / 5432", "Base de datos ERP · Restringida"],
     ["si084_juiceshop", "172.20.0.3", "OWASP Juice Shop / 3000", "Portal de clientes · Confidencial · expuesto"],
     ["si084_dvwa", "172.20.0.2", "Apache 2.4.25 / 80", "App legada interna · Interna"],
     ["si084_portal", "172.20.0.5", "nginx 1.18.0 / 80", "Portal corporativo · Pública · expuesto"]],
    widths=[1.5, 1.2, 1.9, 2.4])
para("Se ejecutaron tres pruebas complementarias contra esos objetivos:", bold=True)
para("• Reconocimiento con nmap (-sV -sC -p-): identificó Apache 2.4.25, nginx 1.18.0, "
     "PostgreSQL y Juice Shop.")
para("• Escaneo no autenticado con nuclei: 60 hallazgos (1 crítico, 5 altos, 2 medios).")
para("• Escaneo de vulnerabilidades con Greenbone/OpenVAS: la tarea Full and fast recorrió los "
     "4 hosts y produjo 78 hallazgos, con severidad máxima 10.0 (Critical).")
para("• Prueba autenticada sobre si084_db, que el escáner no autenticado no alcanza:", bold=True)
cebra_tabla(
    ["Prueba", "Resultado real obtenido"],
    [["Credencial por defecto postgres/postgres", "AUTENTICACIÓN EXITOSA"],
     ["Versión", "PostgreSQL 13.23"],
     ["ssl", "off — canal EN CLARO SIN TLS"],
     ["password_encryption", "md5 (débil, no scram-sha-256)"],
     ["Algoritmo real de la cuenta", "md5; la cuenta es superusuario"],
     ["pg_hba.conf", "host all all all md5 — acepta md5 desde cualquier host"]],
    widths=[2.6, 3.6])
imagen("06_greenbone_tarea_escaneo.png", "Figura 5. Tarea de escaneo Greenbone en estado Done, severidad 10.0 (Critical).")

h("Paso D — Convertir hallazgos técnicos en riesgos de negocio", 2)
para("El papel de trabajo PT03_tecnico_a_riesgo.py consumió las tres fuentes de evidencia "
     "(Greenbone, nuclei y prueba autenticada) y aplicó el contexto de negocio declarado antes "
     "de mirar los resultados: la probabilidad la alimenta la severidad técnica más la "
     "exposición del activo; el impacto lo determina el valor del activo, no la severidad. "
     "El registro resultante contiene 48 riesgos. Se muestran los de mayor valor:")

top = rows[:14]
data = []
for r in top:
    data.append([r["id_riesgo"], r["activo"], r["dueno_del_riesgo"].replace("Gerencia de ", "G. ").replace("Gerencia ", "G. "),
                 r["vulnerabilidad"][:34], r["cvss"], r["probabilidad_ajustada"], r["impacto"],
                 r["riesgo_ajustado"], r["nivel_ajustado"]])
cebra_tabla(["ID", "Activo", "Dueño", "Vulnerabilidad", "CVSS", "P", "I", "Val", "Nivel"], data,
            widths=[0.5, 1.3, 1.0, 1.9, 0.4, 0.3, 0.3, 0.4, 0.7])
para("Distribución de los 48 riesgos: Crítico 3 · Alto 5 · Medio 34 · Bajo 6.", bold=True)

h("Discusión: los dos casos contrastantes", 3)
para("Caso 1 — CVSS alto, riesgo de negocio bajo (R-043).", bold=True)
para("Greenbone detectó en el portal corporativo (nginx 1.18.0) la vulnerabilidad «Nginx "
     "Multiple Vulnerabilities (Oct 2022)» con CVSS 7.8. Sin embargo, el riesgo de negocio es 4 "
     "(Bajo): el activo es de clasificación Pública, sin datos personales ni financieros. La "
     "probabilidad es alta (activo expuesto), pero el impacto es 1 (Insignificante), porque su "
     "compromiso no interrumpe operaciones ni genera incumplimiento. Reportarlo como «crítico» "
     "desviaría presupuesto que debe ir a la base de datos.")
para("Caso 2 — CVSS medio, riesgo de negocio crítico (R-003).", bold=True)
para("La prueba autenticada confirmó ssl=off en la base de datos ERP (CVE-2021-23214, CVSS 5.9, "
     "Media). El cálculo automático da 10 (Medio, P=2×I=5). Se ajustó a 20 (Crítico, P=4×I=5): "
     "si084_juiceshop está expuesto y comparte audit_net con si084_db; comprometer el portal "
     "coloca al atacante en la adyacencia de red que la vulnerabilidad requiere, y capturar en "
     "claro las credenciales del ERP —información Restringida sujeta a la Ley 29733— es trivial. "
     "El ajuste quedó registrado en la columna justificacion_ajuste del registro, conforme a "
     "ISO/IEC 27005:2022.")
para("Regla derivada: el CVSS mide la explotabilidad técnica en abstracto; el riesgo mide la "
     "consecuencia para esta organización. Un registro ordenado por CVSS es un reporte de "
     "escáner con otro nombre.", italic=True)

h("Paso E — Tratamiento, riesgo residual y extracto de SoA", 2)
para("Se cargaron en SimpleRisk los cinco riesgos de mayor valor, cada uno con su decisión de "
     "tratamiento, su plan y su control del Anexo A. La aceptación del riesgo residual la firma "
     "el dueño del riesgo (Gerencia de Finanzas), nunca TI.")
cebra_tabla(
    ["ID", "Riesgo", "Inh.", "Decisión", "Control ISO 27001:2022", "Resid.", "Responsable"],
    [["R-001", "Credencial por defecto en el ERP", "20", "Mitigar", "A.5.17 · A.8.5", "5", "Jefatura de TI"],
     ["R-002", "Credencial por defecto (autenticado)", "20", "Mitigar", "A.5.17 · A.8.5", "5", "Jefatura de TI"],
     ["R-003", "Datos del ERP en claro (sin TLS)", "20", "Mitigar", "A.8.24 · A.8.22", "5", "Jefatura de TI"],
     ["R-004", "Default logins en PostgreSQL", "15", "Mitigar", "A.5.17 · A.8.8", "5", "Jefatura de TI"],
     ["R-005", "Enumeración de base por defecto", "15", "Mitigar", "A.8.8", "5", "Jefatura de TI"]],
    widths=[0.5, 1.9, 0.4, 0.7, 1.5, 0.5, 1.0])
imagen("05_simplerisk_riesgos_cargados.png", "Figura 6. Los cinco riesgos cargados en SimpleRisk con su valor y nivel.")
imagen("08_simplerisk_mitigacion_control_iso.png", "Figura 7. Plan de mitigación de R-003 con el control ISO 27001 mapeado.")

para("Extracto de la Declaración de Aplicabilidad (SoA):", bold=True)
cebra_tabla(
    ["Control", "Título (Anexo A)", "¿Aplica?", "Estado", "Riesgos"],
    [["A.5.17", "Authentication information", "Sí", "No implementado", "R-001, R-002"],
     ["A.8.5", "Secure authentication", "Sí", "No implementado", "R-004, R-006"],
     ["A.8.8", "Management of technical vulnerabilities", "Sí", "No implementado", "R-004, R-005"],
     ["A.8.9", "Configuration management", "Sí", "Parcial", "R-007, R-046"],
     ["A.8.22", "Segregation of networks", "Sí", "No implementado", "R-003"],
     ["A.8.24", "Use of cryptography", "Sí", "No implementado", "R-003"],
     ["A.7.4", "Physical security monitoring", "No (excluido)", "N/A", "—"]],
    widths=[0.8, 2.4, 1.0, 1.3, 1.0])
para("El control A.7.4 se excluye con justificación: el entorno auditado está íntegramente "
     "virtualizado en contenedores sobre infraestructura del proveedor de nube; la seguridad "
     "física del centro de datos no está bajo control de la organización y se gestiona por "
     "contrato mediante A.5.19 y A.5.21.")

para("Sellado de la evidencia: se calcularon los hashes SHA-256 de los 19 archivos de evidencia "
     "(SHA256SUMS_E03.txt) y se verificaron con sha256sum -c (todos OK). El repositorio se "
     "versionó en Git con la etiqueta taller-03.")

doc.add_page_break()

# ===================== 3. RESULTADOS =====================
h("3. Resultados", 1)
para("Toda la evidencia está versionada en el repositorio del trabajo. La URL de referencia es:")
para(GITHUB, bold=True)
para("Etiqueta de entrega: " + GITHUB + "/tree/taller-03")
para()
cebra_tabla(
    ["#", "Resultado esperado", "¿Se logró?", "Evidencia"],
    [["1", "Greenbone/OpenVAS operativo con feeds sincronizados", "Sí",
      "GSA 28.3.0, NVT Current; Figura 1; escaneo Full and fast ejecutado (Figura 5)"],
     ["2", "SimpleRisk con escalas 1–5 con definición operativa y criterio de aceptación", "Sí",
      "Figuras 2 y 3; criterio ≤ 6/25 y apetito de riesgo configurados"],
     ["3", "Reporte de escaneo (CSV y XML) con la lista de objetivos autorizados", "Sí",
      "reporte_greenbone.csv (78 hallazgos) y .xml en E03_scan/; objetivos.txt; nmap; nuclei; prueba autenticada"],
     ["4", "Registro con ≥ 10 riesgos, cada uno con activo, dueño, CVE, P, I y nivel", "Sí — 48 riesgos",
      "PT03_registro_riesgos.csv"],
     ["5", "Dos casos contrastantes documentados", "Sí",
      "R-043 (CVSS 7.8 → riesgo 4, Bajo) y R-003 (CVSS 5.9 → riesgo 20, Crítico), Paso D"],
     ["6", "Cinco riesgos en SimpleRisk con plan y control ISO", "Sí",
      "Figuras 6 y 7"],
     ["7", "SoA con ≥ 5 controles, uno excluido con justificación", "Sí — 7 controles, A.7.4 excluido",
      "PT03_soa_extracto.md"],
     ["8", "Hashes en la cadena de custodia y commit en Git", "Sí",
      "SHA256SUMS_E03.txt (19 archivos OK); git log"]],
    widths=[0.3, 2.3, 1.1, 2.5])

h("3.1 Síntesis cuantitativa", 2)
cebra_tabla(
    ["Indicador", "Valor"],
    [["Hallazgos técnicos procesados (Greenbone + nuclei + autenticado)", "78 + 60 + 6"],
     ["Riesgos de negocio registrados", "48"],
     ["Riesgos Críticos tras el ajuste de auditoría", "3"],
     ["Riesgos cargados y tratados en SimpleRisk", "5"],
     ["Controles del Anexo A en el SoA", "6 incluidos + 1 excluido"],
     ["Archivos sellados con SHA-256", "19"]],
    widths=[4.2, 2.0])

# ===================== 4. CONCLUSIONES =====================
h("4. Conclusiones", 1)
for c in [
    "La severidad CVSS y el riesgo de negocio son escalas distintas. La corrida lo probó con dos casos del mismo conjunto de datos: R-043 (nginx, CVSS 7.8) resultó de riesgo Bajo por estar en un activo público sin datos, mientras que R-003 (TLS, CVSS 5.9) resultó Crítico por exponer en claro las credenciales del ERP. Ordenar por CVSS habría enterrado el hallazgo que más compromete a la organización.",
    "Sin criterio de aceptación fijado antes de evaluar, la matriz no es comparable. El criterio se cargó en SimpleRisk antes de registrar el primer riesgo, lo que permitió afirmar sin discusión qué residuales no pueden aceptarse. Fijarlo después habría permitido justificar cualquier número a posteriori.",
    "La Declaración de Aplicabilidad vuelve auditable el análisis. Cada control incluido se rastrea a riesgos concretos, y la exclusión de A.7.4 se apoya en un hecho verificable —el entorno es virtualizado— con controles compensatorios nombrados. Esa trazabilidad bidireccional es lo que exige la cláusula 6.1.3 de la ISO/IEC 27001:2022.",
    "La evidencia sin cadena de custodia no sostiene un hallazgo. El sellado SHA-256 (19 archivos verificados) y el versionado en Git permiten demostrar qué archivo se analizó, cuándo y bajo qué alcance.",
    "El alcance autorizado es un control del propio proceso de auditoría. Registrar objetivos.txt antes de escanear y limitarlo a audit_net es lo que separa una prueba de auditoría de una conducta tipificada por la Ley 30096.",
]:
    doc.add_paragraph(c, style="List Number")

# ===================== 5. CUESTIONARIO =====================
h("5. Cuestionario", 1)
qa = [
    ("¿Por qué un CVE con CVSS 9.8 no es por sí solo un riesgo alto?",
     "Porque el CVSS mide explotabilidad técnica en abstracto; sus métricas de impacto describen el efecto sobre el sistema, no sobre el negocio. El riesgo (ISO/IEC 27005) combina probabilidad y consecuencia para la organización, lo que exige conocer el activo, su clasificación y su exposición. En la corrida, R-043 (nginx CVSS 7.8) resultó Bajo por estar en un activo público sin datos."),
    ("¿Diferencia entre riesgo inherente y residual, y el error más frecuente?",
     "El inherente ignora los controles; el residual los considera tras verificar que operan. El error frecuente es dar por bueno un control documentado nunca probado, lo que convierte el residual en ficción."),
    ("¿Quién firma la aceptación del riesgo residual y por qué no TI?",
     "El dueño del riesgo, quien responde por el proceso de negocio, porque TI administra el activo pero no asume la consecuencia. Un riesgo aceptado sin su firma es un riesgo ignorado."),
    ("¿Qué aporta el SoA que no aporta el registro de riesgos?",
     "El registro dice qué puede pasar y cuánto importa; el SoA dice qué controles se aplican, cuáles no y por qué, de forma rastreable en ambos sentidos. Permite al auditor exigir la implementación de un control o su justificación de exclusión."),
    ("¿Consecuencia legal de escanear fuera de la red autorizada?",
     "Acceso no autorizado a sistema informático, tipificado en el art. 2 de la Ley 30096, modificada por la Ley 30171. Por eso el alcance se documenta antes en objetivos.txt."),
    ("¿Por qué no escanear con los feeds de Greenbone sincronizando?",
     "Porque la base de pruebas define qué reconoce el escáner; con feeds incompletos, la ausencia de un hallazgo no significa que no exista, sino que no se buscó. Greenbone bloquea el lanzamiento con «Scans are not available during this time» mientras sincroniza."),
    ("¿Qué papel cumple el hash SHA-256?",
     "Establece la cadena de custodia digital: fija el contenido de cada archivo, detectable con sha256sum -c. Combinado con el commit de Git, prueba qué se analizó, cuándo y bajo qué alcance."),
    ("¿Por qué la guía exige la URL de GitHub y no una captura?",
     "Una captura no verifica autoría, fecha ni contenido; un commit etiquetado sí. Las capturas documentan estados de interfaz, pero se citan por su URL en el repositorio."),
]
for i, (q, a) in enumerate(qa, 1):
    para(f"{i}. {q}", bold=True)
    para(a)

# ===================== 6. REFERENCIAS =====================
h("6. Referencias bibliográficas", 1)
for ref in [
    "Alexander, A. G. (2007). Diseño de un sistema de gestión de seguridad de información: óptica ISO 27001. Alfaomega.",
    "Congreso de la República del Perú. (2011). Ley N.° 29733, Ley de Protección de Datos Personales. El Peruano.",
    "Congreso de la República del Perú. (2013). Ley N.° 30096, Ley de Delitos Informáticos (mod. Ley N.° 30171, 2014). El Peruano.",
    "FIRST. (2019). Common Vulnerability Scoring System v3.1: Specification Document. https://www.first.org/cvss/v3-1/specification-document",
    "Greenbone AG. (2024). Greenbone Community Documentation. https://greenbone.github.io/docs/",
    "ISO/IEC. (2022). ISO/IEC 27001:2022 — Information security management systems — Requirements. https://www.iso.org/standard/27001",
    "ISO/IEC. (2022). ISO/IEC 27002:2022 — Information security controls. https://www.iso.org/standard/75652.html",
    "ISO/IEC. (2022). ISO/IEC 27005:2022 — Guidance on managing information security risks. https://www.iso.org/standard/80585.html",
    "ISO. (2018). ISO 31000:2018 — Risk management — Guidelines. https://www.iso.org/standard/65694.html",
    "Presidencia del Consejo de Ministros. (2016). R.M. N.° 004-2016-PCM. https://www.gob.pe/institucion/pcm/normas-legales/292578-004-2016-pcm",
    "Secretaría de Gobierno y Transformación Digital. (2023). R.S.G.T.D. N.° 003-2023-PCM/SGTD.",
    "SimpleRisk. (2024). SimpleRisk Documentation. https://www.simplerisk.com/documentation",
]:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    for r in p.runs:
        r.font.size = Pt(10)

# ===================== 7. ANEXOS =====================
h("7. Anexos", 1)
cebra_tabla(
    ["Anexo", "Título", "Ubicación en el repositorio"],
    [["A", "Evidencia cruda del escaneo (Greenbone CSV/XML, nmap, nuclei, prueba autenticada, verificación web)", "20_evidencia/E03_scan/"],
     ["B", "Registro completo de 48 riesgos con ajuste de auditoría", "40_hallazgos/PT03_registro_riesgos.csv"],
     ["C", "Extracto de la Declaración de Aplicabilidad", "30_papeles_trabajo/PT03_soa_extracto.md"],
     ["D", "Cadena de custodia y su verificación", "20_evidencia/SHA256SUMS_E03.txt"],
     ["E", "Capturas numeradas 01–08", "docs/evidencias/S03/"],
     ["F", "Papeles de trabajo y scripts", "30_papeles_trabajo/"]],
    widths=[0.6, 3.4, 2.2])
para()
para("Escuela Profesional de Ingeniería de Sistemas · Universidad Privada de Tacna · Tacna, Perú",
     align=WD_ALIGN_PARAGRAPH.CENTER, size=9, italic=True)

doc.save(str(OUT))
print("DOCX generado:", OUT)
print("Paragrafos:", len(doc.paragraphs))
