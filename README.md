# SI-084 · Auditoría de Sistemas · Entorno auditable `si084-lab`

Repositorio de trabajo del encargo de auditoría. Contiene el entorno auditado,
la evidencia levantada, los papeles de trabajo y los hallazgos de cada semana.

**Autor:** Chata Choque, Brant Antony — código `bc2020067577`
**Docente:** Dr. Oscar Juan Jimenez Flores
**Universidad Privada de Tacna** · Facultad de Ingeniería · Escuela Profesional de Ingeniería de Sistemas

---

## Alcance autorizado

> Todo escaneo de este repositorio se ejecuta **exclusivamente** contra la red
> Docker `audit_net`. El alcance se documenta en
> [`20_evidencia/E03_scan/objetivos.txt`](20_evidencia/E03_scan/objetivos.txt)
> **antes** de lanzar cualquier prueba.
>
> Escanear infraestructura fuera de ese alcance constituye acceso no autorizado
> a sistema informático, tipificado en el artículo 2 de la **Ley 30096**,
> modificada por la Ley 30171.

## Estructura

| Ruta | Contenido |
|---|---|
| `entorno/` | `docker-compose.yml` del entorno auditado y de las herramientas |
| `entorno/greenbone/` | Pila de Greenbone Community Edition |
| `20_evidencia/E03_scan/` | Evidencia cruda del escaneo de la Semana 03 |
| `20_evidencia/SHA256SUMS_E03.txt` | Cadena de custodia digital |
| `30_papeles_trabajo/` | Papeles de trabajo del auditor |
| `40_hallazgos/` | Registro de riesgos resultante |
| `docs/evidencias/S03/` | Capturas numeradas y salidas de consola |

## Activos del entorno y su contexto de negocio

El contexto se declara **antes** de evaluar. Sin él, la severidad CVSS no puede
convertirse en riesgo.

| Contenedor | Activo de negocio | Dueño del riesgo | Clasificación | Expuesto | Criticidad |
|---|---|---|---|---|---|
| `si084_db` | Base de datos ERP | Gerencia de Finanzas | Restringida | No | 5 |
| `si084_juiceshop` | Portal de clientes | Gerencia Comercial | Confidencial | Sí | 4 |
| `si084_portal` | Portal corporativo | Gerencia Comercial | Pública | Sí | 2 |
| `si084_dvwa` | App legada interna | Gerencia de Operaciones | Interna | No | 3 |

## Cómo se levanta el entorno

```bash
cd entorno
docker compose up -d
```

Interfaces (publicadas solo en `127.0.0.1`, nunca en `0.0.0.0`):

| Servicio | URL |
|---|---|
| SimpleRisk | http://127.0.0.1:8083 |
| Greenbone / OpenVAS | http://127.0.0.1:9392 |
| Portal de clientes (Juice Shop) | http://127.0.0.1:3000 |
| App legada (DVWA) | http://127.0.0.1:8081 |
| Portal corporativo (nginx) | http://127.0.0.1:8082 |

> Los contenedores `si084_juiceshop` y `si084_dvwa` son aplicaciones
> **deliberadamente vulnerables**. Son el objeto de auditoría del curso y no
> deben exponerse fuera de este equipo.

## Papeles de trabajo

| Archivo | Qué hace |
|---|---|
| [`PT03_tecnico_a_riesgo.py`](30_papeles_trabajo/PT03_tecnico_a_riesgo.py) | Convierte la evidencia técnica en registro de riesgos de negocio |
| [`PT03_soa_extracto.md`](30_papeles_trabajo/PT03_soa_extracto.md) | Extracto de la Declaración de Aplicabilidad |
| [`gmp.sh`](30_papeles_trabajo/gmp.sh) | Envoltorio para hablar GMP con Greenbone |
| [`capturar_evidencia.js`](30_papeles_trabajo/capturar_evidencia.js) | Captura automatizada de las pantallas exigidas |
| [`sellar_evidencia.sh`](30_papeles_trabajo/sellar_evidencia.sh) | Sella la evidencia con SHA-256 y verifica la cadena |

## Verificar la cadena de custodia

```bash
sha256sum -c 20_evidencia/SHA256SUMS_E03.txt
```

## Limpiar el entorno

```bash
cd entorno && docker compose down -v
docker compose -p greenbone-community-edition -f greenbone/docker-compose.yml down -v
docker network rm audit_net
```
