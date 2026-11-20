const { chromium, devices } = require('playwright');
const fs = require('fs');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const c = await b.newContext({ ...devices['iPhone 13 Pro'], locale: 'pt-BR' });
  const p = await c.newPage();
  try { await p.goto('https://jogargta.com/', { waitUntil: 'domcontentloaded', timeout: 45000 }); } catch (e) {}
  await p.waitForTimeout(6000);
  fs.writeFileSync(out + '/go', '');
  const cdp = await c.newCDPSession(p);
  const log = []; let n = 0;
  const grab = async (sec, label) => {
    const end = Date.now() + sec * 1000;
    while (Date.now() < end) {
      const st = await p.evaluate(() => { const f = document.querySelector('iframe[src*="player.kick"]'); const r = f ? f.getBoundingClientRect() : null; return { y: scrollY, r: r && [r.x, r.y, r.width, r.height] }; });
      const t = Date.now() / 1000;
      const r = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 90, clip: { x: 0, y: st.y, width: 390, height: 664, scale: 3 } });
      const name = `f${String(n++).padStart(5, '0')}.jpg`;
      fs.writeFileSync(`${out}/fr/${name}`, Buffer.from(r.data, 'base64'));
      log.push({ name, t, label, ...st });
    }
  };
  const go = async (y) => { await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(300); };
  await grab(11, 'top');
  await go(260); await grab(9, 'timer');
  await go(560); await grab(8, 'fila');
  try { await p.getByText('Fila do jogo').first().click({ timeout: 3000 }); } catch (e) {}
  await go(900); await grab(8, 'queue');
  fs.writeFileSync(out + '/log.json', JSON.stringify(log));
  await b.close();
})();
