const fs = require('fs');
const path = require('path');
const { connect, sleep } = require('../../lab7/auto/cdp');
const PDF = 'E:/ChatGPT/2026-11-11-13-35-39/a2-second-thought/docs/preview.pdf';
(async () => {
  const c = await connect('127.0.0.1:8770');
  await c.send('Emulation.setDeviceMetricsOverride', { width: 1000, height: 1300, deviceScaleFactor: 1.5, mobile: false });
  for (let p = 1; p <= 7; p++) {
    await c.send('Page.navigate', { url: 'about:blank' });
    await sleep(250);
    await c.send('Page.navigate', { url: 'file:///' + PDF + '#page=' + p + '&zoom=80' });
    await sleep(1600);
    const r = await c.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, '..', 'docs', 'page' + p + '.png'), Buffer.from(r.data, 'base64'));
    console.log('page', p);
  }
  c.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
