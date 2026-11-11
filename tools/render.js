const fs = require('fs');
const path = require('path');
const { connect, sleep } = require('../../lab7/auto/cdp');

const ROOT = path.join(__dirname, '..');
const files = [
  ['docs/system-diagram.svg', 1020, 760],
  ['docs/storyboard-1.svg', 1020, 500],
  ['docs/storyboard-2.svg', 1020, 500],
  ['docs/storyboard-3.svg', 1020, 500]
];

(async () => {
  const c = await connect('127.0.0.1:8770');
  for (const [rel, w, h] of files) {
    await c.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 2, mobile: false });
    await c.navigate('file:///' + path.join(ROOT, rel).replace(/\\/g, '/'));
    await sleep(700);
    const r = await c.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    const out = path.join(ROOT, rel.replace('.svg', '.png'));
    fs.writeFileSync(out, Buffer.from(r.data, 'base64'));
    console.log('rendered', rel, '->', path.basename(out));
  }
  await c.send('Emulation.clearDeviceMetricsOverride');
  await c.navigate('http://127.0.0.1:8770/');
  c.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
