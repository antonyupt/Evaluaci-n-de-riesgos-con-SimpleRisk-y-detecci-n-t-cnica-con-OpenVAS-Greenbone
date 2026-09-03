# PT03 · Extracto de la Declaración de Aplicabilidad (SoA)

**SI-084 · Auditoría de Sistemas · Semana 03**
**Marco:** ISO/IEC 27001:2022 — Anexo A
**Alcance:** entorno auditado `si084-lab` (red `audit_net`)
**Enfoque de identificación:** basado en activos (ISO/IEC 27005:2022)

> La Declaración de Aplicabilidad es el punto donde el análisis de riesgos se
> vuelve auditable. Cada control incluido o excluido se rastrea hasta un riesgo
> concreto del registro `40_hallazgos/PT03_registro_riesgos.csv`.

## Extracto

| Control | Título (Anexo A) | ¿Aplica? | Justificación | Estado | Riesgos que trata |
|---|---|---|---|---|---|
| **A.5.17** | Authentication information | Sí | La prueba autenticada confirmó credencial por defecto válida (`postgres/postgres`) y almacenamiento de contraseñas con `md5` en la base de datos ERP | No implementado | R-001, R-002, R-009 |
| **A.8.5** | Secure authentication | Sí | La cuenta de servicio de la aplicación opera como superusuario; `pg_hba.conf` acepta `md5` desde cualquier host de la red | No implementado | R-004, R-006, R-008 |
| **A.8.8** | Management of technical vulnerabilities | Sí | El escaneo evidenció vulnerabilidades explotables con referencia pública y no existe proceso de gestión de parches documentado | No implementado | R-004, R-005 |
| **A.8.9** | Configuration management | Sí | Configuraciones por defecto en producción: listado de directorios activo en el portal, `/metrics` de Prometheus sin autenticación, servicios con parámetros de fábrica | Parcial | R-007, R-010 |
| **A.8.22** | Segregation of networks | Sí | La base de datos ERP (información Restringida) comparte el segmento `audit_net` con activos expuestos a Internet, habilitando movimiento lateral | No implementado | R-003 |
| **A.8.24** | Use of cryptography | Sí | La prueba autenticada confirmó `ssl=off`: la autenticación y los datos de la base de datos ERP viajan en claro por la red | No implementado | R-003, R-009 |
| **A.8.28** | Secure coding | Sí | El entorno incluye aplicaciones con inyección y controles de entrada ausentes; no existe estándar de codificación segura ni revisión previa al despliegue | No implementado | (portal de clientes / app legada) |
| **A.7.4** | Physical security monitoring | **No** | **Excluido con justificación:** el entorno auditado está íntegramente virtualizado en contenedores sobre infraestructura del proveedor de nube. La seguridad física del centro de datos no está bajo control de la organización y se gestiona por vía contractual mediante **A.5.19** y **A.5.21** (seguridad en las relaciones con proveedores), verificados contra la certificación vigente del proveedor | **N/A** | — |

## Nota de método

- Los controles **incluidos** se declaran *No implementado* o *Parcial* porque el
  taller levanta la línea base: ninguno se da por operativo sin haberlo probado.
- El control **A.7.4 se excluye** apoyándose en un hecho verificable —la
  naturaleza virtualizada del entorno—, no en conveniencia, y nombra los
  controles compensatorios. Esta es la exclusión que un auditor de certificación
  revisa primero.
- La trazabilidad es bidireccional: desde cada control se llega a los riesgos que
  trata, y desde cada riesgo del registro se llega al control que lo mitiga.
