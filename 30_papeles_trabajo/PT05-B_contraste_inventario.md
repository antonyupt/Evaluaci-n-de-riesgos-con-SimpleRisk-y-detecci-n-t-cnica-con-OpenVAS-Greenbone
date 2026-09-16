# Papel de trabajo PT05-B — Contraste de inventario declarado vs. real

**Fecha del escaneo:** 16 de septiembre de 2026
**Herramienta:** Nmap 7.98, `-sV -sC -p- --open` contra la subred `si084-lab_audit_net`
**Fuente:** `20_evidencia/E05_infra/nmap_servicios.nmap`

| Servicio hallado por Nmap | Puerto | Versión | ¿Figura en el inventario declarado? | ¿Tiene dueño identificado? | ¿Está en el alcance del SGSI? | Observación |
|---|---|---|---|---|---|---|
| si084_db (PostgreSQL) | 5432/tcp | PostgreSQL DB 9.6.0 o superior | Sí | Sí (base del portal/ERP) | Sí | Coincide con `alcance_E05.md` |
| si084_portal (Apache) | 80/tcp (mapeado externo a 8082) | Apache httpd 2.4.68 (Debian) | Sí | Sí | Sí | Redirige internamente a `si084_portal:8082` |
| **si084_wpdb (MariaDB)** | *(puerto detectado por el script `-sC`, confirmar en `nmap_servicios.nmap`)* | MariaDB Server, certificado TLS autofirmado (válido hasta 2036-09-13) | **No** | **No identificado** | **No declarado explícitamente en `alcance_E05.md`** | **Servicio no inventariado — ver hallazgo H-001** |

**Puertos TLS (443, 8443):** cerrados en los tres hosts escaneados. Ningún servicio del entorno expone HTTPS; todo el tráfico observado viaja en claro.

**Conclusión del contraste:** el `alcance_E05.md` declaró explícitamente `si084_juiceshop` y `si084_portal`, pero no mencionó la base de datos de soporte del portal (`si084_wpdb`), que sin embargo está en la misma red auditada y respondió al escaneo. Esto reproduce en miniatura el hallazgo clásico de auditoría: el inventario de activos declarado y la superficie real expuesta no coinciden.