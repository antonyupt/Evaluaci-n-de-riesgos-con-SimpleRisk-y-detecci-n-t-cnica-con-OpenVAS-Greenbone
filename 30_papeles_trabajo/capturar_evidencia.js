/**
 * SI-084 · Semana 03 — Captura automatizada de la evidencia en pantalla.
 *
 * Genera los PNG que exigen los resultados 1, 2 y 6 de la guía del taller.
 * Se ejecuta dentro de un contenedor conectado a audit_net y a la red de
 * Greenbone, de modo que alcanza ambas interfaces por nombre de servicio.
 *
 *   node capturar_evidencia.js <destino>
 */
const puppeteer = require('puppeteer');

const OUT = process.argv[2] || '/out';
const SR = 'http://si084_simplerisk';
const GB = 'http://nginx:9392';
const SR_USER = 'admin', SR_PASS = 'SI084_lab_2026!';
const GB_USER = 'admin', GB_PASS = 'SI084_lab_2026';

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function shot(page, file, note) {
  await sleep(1500);
  await page.screenshot({ path: `${OUT}/${file}`, fullPage: true });
  console.log(`  [ok] ${file}  — ${note}`);
}

async function type(page, sel, value) {
  await page.waitForSelector(sel, { timeout: 30000 });
  await page.click(sel, { clickCount: 3 });
  await page.type(sel, value, { delay: 25 });
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000 });

  // ---------------- SimpleRisk ----------------
  try {
    console.log('SimpleRisk:');
    await page.goto(`${SR}/index.php`, { waitUntil: 'networkidle2', timeout: 60000 });
    await type(page, 'input[name="user"]', SR_USER);
    await type(page, 'input[name="pass"]', SR_PASS);
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {}),
      page.click('button[type="submit"], input[type="submit"]'),
    ]);
    await sleep(3000);

    await page.goto(`${SR}/admin/risk_configuration.php`, { waitUntil: 'networkidle2' });
    await shot(page, '02_simplerisk_escalas_y_criterio.png',
      'Risk Levels 1-25 y criterio de aceptacion (resultado 2)');

    // Pestaña de la fórmula clásica + matriz de calor
    const tabs = await page.$$('button[role="tab"], .nav-link');
    for (const t of tabs) {
      const txt = (await page.evaluate(e => e.textContent, t) || '').trim();
      if (/Classic Risk Formula/i.test(txt)) { await t.click(); break; }
    }
    await shot(page, '03_simplerisk_formula_classic.png',
      'Likelihood x Impact normalizado 0-10 (resultado 2)');

    await page.goto(`${SR}/admin/user_management.php`, { waitUntil: 'networkidle2' })
      .catch(() => {});
    await shot(page, '04_simplerisk_duenos_de_riesgo.png',
      'Dueños de riesgo por area (resultado 2)');

    await page.goto(`${SR}/management/index.php`, { waitUntil: 'networkidle2' }).catch(() => {});
    await shot(page, '05_simplerisk_riesgos_cargados.png',
      'Riesgos cargados con su valor y nivel (resultado 6)');
  } catch (e) {
    console.log('  [!] SimpleRisk:', e.message);
  }

  // ---------------- Greenbone ----------------
  try {
    console.log('Greenbone:');
    // La SPA de GSA monta el formulario en la raiz; /login no lo sirve directamente.
    await page.goto(`${GB}/`, { waitUntil: 'networkidle2', timeout: 60000 });
    await page.waitForSelector('input[name="username"]', { timeout: 45000 });
    await type(page, 'input[name="username"]', GB_USER);
    await type(page, 'input[name="password"]', GB_PASS);
    await page.keyboard.press('Enter');
    await sleep(9000);

    await page.goto(`${GB}/feedstatus`, { waitUntil: 'networkidle2' });
    await shot(page, '01_greenbone_feed_status.png',
      'Estado de los feeds NVT/SCAP/CERT (resultado 1)');

    await page.goto(`${GB}/tasks`, { waitUntil: 'networkidle2' });
    await shot(page, '06_greenbone_tarea_escaneo.png',
      'Tarea de escaneo y su estado (resultado 3)');

    await page.goto(`${GB}/reports`, { waitUntil: 'networkidle2' });
    await shot(page, '07_greenbone_reportes.png',
      'Reportes disponibles para descarga (resultado 3)');
  } catch (e) {
    console.log('  [!] Greenbone:', e.message);
  }

  await browser.close();
  console.log('Capturas completas.');
})();
