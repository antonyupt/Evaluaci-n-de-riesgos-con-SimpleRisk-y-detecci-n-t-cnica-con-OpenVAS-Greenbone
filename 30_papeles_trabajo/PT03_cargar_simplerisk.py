#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SI-084 · Semana 03
PT03 — Carga en SimpleRisk de los cinco riesgos de mayor valor, con su plan de
tratamiento y el control del Anexo A de la ISO/IEC 27001:2022 al que se mapean.

Genera el SQL que se aplica sobre la base de SimpleRisk. Se emite como archivo
para que la carga quede auditable: se puede leer, revisar y volver a ejecutar.

    python PT03_cargar_simplerisk.py  >  ../.tmp/cargar_riesgos.sql
"""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REG = BASE / "40_hallazgos" / "PT03_registro_riesgos.csv"

# Usuarios de SimpleRisk creados como dueños de riesgo (tabla `user`)
DUENO_A_USER = {
    "Gerencia de Finanzas": 2,
    "Gerencia Comercial": 3,
    "Gerencia de Operaciones": 4,
    "Jefatura de TI": 5,
}

# Plan de tratamiento por riesgo. La clave es un fragmento del nombre de la
# vulnerabilidad tal como aparece en el registro. Cada entrada declara:
#   estrategia  3=Mitigate 2=Accept 5=Transfer 4=Watch 1=Research
#   control     control_number del Anexo A ya cargado en framework_controls
#   p_res/i_res probabilidad e impacto residuales tras aplicar el control
TRATAMIENTO = [
    dict(match="Empty Password", estrategia=3, controles=["A.5.17", "A.8.5"],
         p_res=1,
         solucion="La instancia acepta autenticación sin contraseña o con la "
                  "credencial por defecto de la imagen.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.5.17 Authentication information; "
                    "A.8.5 Secure authentication.",
         recomendacion="Fijar contraseña robusta gestionada en bóveda, activar "
                       "password_encryption=scram-sha-256, restringir pg_hba.conf "
                       "por host y usuario, y retirar el privilegio de superusuario "
                       "de la cuenta de servicio de la aplicación."),
    dict(match="Credencial por defecto", estrategia=3, controles=["A.5.17", "A.8.5"],
         p_res=1,
         solucion="Prueba autenticada: la credencial postgres/postgres es válida "
                  "contra la base de datos ERP.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.5.17; A.8.5.",
         recomendacion="Rotar la credencial, prohibir credenciales por defecto en el "
                       "estándar de despliegue y verificarlo en el pipeline."),
    dict(match="TLS no forzado", estrategia=3, controles=["A.8.24", "A.8.22"],
         p_res=1,
         solucion="ssl=off. La autenticación y los datos de la base de datos ERP "
                  "viajan en claro por audit_net, compartida con activos expuestos.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.8.24 Use of cryptography; "
                    "A.8.22 Segregation of networks.",
         recomendacion="Activar ssl=on con hostssl obligatorio en pg_hba.conf, emitir "
                       "certificado desde la CA interna y sacar la base de datos del "
                       "segmento que comparte con los activos expuestos a Internet."),
    dict(match="superusuario", estrategia=3, controles=["A.8.5", "A.8.9"],
         p_res=1,
         solucion="La cuenta usada por la aplicación tiene rol de superusuario.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.8.5; A.8.9 Configuration management.",
         recomendacion="Crear una cuenta de servicio con privilegios mínimos sobre el "
                       "esquema de la aplicación y reservar el superusuario para "
                       "tareas administrativas con registro de uso."),
    dict(match="Default Logins", estrategia=3, controles=["A.5.17", "A.8.8"],
         p_res=1,
         solucion="El escáner confirma credenciales por defecto en el servicio.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.5.17; A.8.8 Management of "
                    "technical vulnerabilities.",
         recomendacion="Incorporar la verificación de credenciales por defecto al "
                       "ciclo de gestión de vulnerabilidades, con periodicidad "
                       "definida y responsable asignado."),
    dict(match="pg_hba", estrategia=3, controles=["A.8.9", "A.8.22"],
         p_res=1,
         solucion="pg_hba.conf acepta autenticación md5 desde cualquier host de la red.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.8.9; A.8.22.",
         recomendacion="Restringir las reglas host a las IP de los servicios que "
                       "legítimamente consumen la base de datos."),
    dict(match="md5", estrategia=3, controles=["A.5.17", "A.8.24"],
         p_res=1,
         solucion="Las contraseñas se almacenan con md5 en lugar de scram-sha-256.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.5.17; A.8.24.",
         recomendacion="Migrar a scram-sha-256 y forzar el cambio de todas las "
                       "credenciales existentes."),
    dict(match="Prometheus", estrategia=3, controles=["A.8.9"],
         p_res=1,
         solucion="El endpoint /metrics responde sin autenticación en el portal "
                  "de clientes.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.8.9.",
         recomendacion="Restringir /metrics a la red de observabilidad o exigir "
                       "autenticación."),
    dict(match="Configuration Files Listing", estrategia=3, controles=["A.8.9"],
         p_res=1,
         solucion="Archivos de configuración accesibles desde el servidor web.",
         requisitos="ISO/IEC 27001:2022 Anexo A — A.8.9.",
         recomendacion="Retirar los archivos del árbol público y deshabilitar el "
                       "listado de directorios."),
]

# Genérico para lo que no tenga entrada específica
GENERICO = dict(estrategia=3, controles=["A.8.8"], p_res=2,
                solucion="Vulnerabilidad detectada por el escáner en el activo.",
                requisitos="ISO/IEC 27001:2022 Anexo A — A.8.8 Management of "
                           "technical vulnerabilities.",
                recomendacion="Incorporar el hallazgo al ciclo de gestión de "
                              "vulnerabilidades con responsable y plazo.")


def esc(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")


def plan_para(vuln):
    for t in TRATAMIENTO:
        if t["match"].lower() in vuln.lower():
            return t
    return GENERICO


filas = list(csv.DictReader(open(REG, encoding="utf-8")))
top5 = filas[:5]

print("-- SI-084 · Semana 03 — carga de los 5 riesgos de mayor valor en SimpleRisk")
print("-- Generado por PT03_cargar_simplerisk.py a partir de PT03_registro_riesgos.csv")
print("SET NAMES utf8mb4;")
print("DELETE FROM mitigation_to_controls;")
print("DELETE FROM mitigations;")
print("DELETE FROM risk_scoring;")
print("DELETE FROM risks;")

for n, r in enumerate(top5, 1):
    rid = 1000 + n                      # SimpleRisk muestra el id como ID#
    owner = DUENO_A_USER.get(r["dueno_del_riesgo"], 1)
    p = int(r["probabilidad_ajustada"])
    i = int(r["impacto"])
    calc = round(p * i * 0.4, 1)        # normalización 0-10 de SimpleRisk
    t = plan_para(r["vulnerabilidad"])
    p_res = t["p_res"]
    calc_res = round(p_res * i * 0.4, 1)

    asunto = f'{r["id_riesgo"]} · {r["activo"]} · {r["vulnerabilidad"]}'[:250]
    evaluacion = (
        f'Activo: {r["activo"]} ({r["contenedor"]}, {r["host"]}). '
        f'Clasificacion: {r["clasificacion"]}. Expuesto a Internet: {r["expuesto"]}. '
        f'Amenaza: {r["amenaza"]}. '
        f'Vulnerabilidad: {r["vulnerabilidad"]}. '
        f'CVE: {r["cve"]}. CVSS v3.1: {r["cvss"]}. '
        f'Fuente de la evidencia: {r["fuente_evidencia"]}.'
    )
    notas = (
        f'Riesgo inherente {r["riesgo_inherente"]}/25 ({r["nivel"]}). '
        f'Riesgo tras ajuste de auditoria {r["riesgo_ajustado"]}/25 ({r["nivel_ajustado"]}). '
        f'Riesgo residual estimado {p_res * i}/25 tras aplicar el control. '
        f'Criterio de aceptacion del curso: se acepta con firma del dueno si el valor es <= 6/25. '
    )
    if r["justificacion_ajuste"]:
        notas += f'AJUSTE DE AUDITORIA (ISO/IEC 27005:2022): {r["justificacion_ajuste"]}'

    print(f"""
INSERT INTO risks (id,status,subject,reference_id,control_number,source,category,
                   owner,manager,assessment,notes,submission_date,mitigation_id,
                   mgmt_review,submitted_by)
VALUES ({rid},'Open','{esc(asunto)}','{esc(r["id_riesgo"])}','{esc(t["controles"][0])}',
        1,1,{owner},{owner},'{esc(evaluacion)}','{esc(notas)}',NOW(),0,0,1);
INSERT INTO risk_scoring (id,scoring_method,CLASSIC_likelihood,CLASSIC_impact,calculated_risk)
VALUES ({rid},1,{p},{i},{calc});
INSERT INTO mitigations (risk_id,submission_date,planning_strategy,mitigation_effort,
                         mitigation_cost,mitigation_owner,current_solution,
                         security_requirements,security_recommendations,submitted_by,
                         planning_date,mitigation_percent)
VALUES ({rid},NOW(),{t["estrategia"]},2,1,{DUENO_A_USER["Jefatura de TI"]},
        '{esc(t["solucion"])}',
        '{esc(t["requisitos"])} Riesgo residual objetivo: {p_res * i}/25 (score {calc_res}).',
        '{esc(t["recomendacion"])}',1,DATE_ADD(CURDATE(), INTERVAL 30 DAY),0);
UPDATE risks SET mitigation_id = LAST_INSERT_ID() WHERE id = {rid};
INSERT INTO mitigation_to_controls (mitigation_id,control_id)
  SELECT LAST_INSERT_ID(), id FROM framework_controls
   WHERE control_number IN ({",".join("'" + c + "'" for c in t["controles"])});""")

print("""
SELECT r.id AS 'ID#', r.reference_id AS 'ID auditoria',
       CONVERT(LEFT(r.subject,60) USING utf8) AS 'Riesgo',
       u.name AS 'Dueno del riesgo',
       rs.CLASSIC_likelihood AS P, rs.CLASSIC_impact AS I,
       rs.calculated_risk AS 'Score 0-10',
       ROUND(rs.CLASSIC_likelihood*rs.CLASSIC_impact) AS 'Valor 1-25',
       ps.name AS 'Tratamiento',
       GROUP_CONCAT(fc.control_number ORDER BY fc.control_number SEPARATOR ', ') AS 'Controles ISO'
  FROM risks r
  JOIN risk_scoring rs ON rs.id = r.id
  JOIN user u ON u.value = r.owner
  LEFT JOIN mitigations m ON m.risk_id = r.id
  LEFT JOIN planning_strategy ps ON ps.value = m.planning_strategy
  LEFT JOIN mitigation_to_controls mtc ON mtc.mitigation_id = m.id
  LEFT JOIN framework_controls fc ON fc.id = mtc.control_id
 GROUP BY r.id ORDER BY rs.calculated_risk DESC;""")
