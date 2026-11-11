const fs = require('fs');
const path = require('path');
const { connect, sleep } = require('../../lab7/auto/cdp');

const OUT = path.join(__dirname, '..', 'docs', 'screenshots');

async function shot(c, name) {
  const r = await c.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, 'base64'));
  console.log('shot', name);
}

(async () => {
  const c = await connect('127.0.0.1:8770');
  await c.send('Page.enable');
  await c.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 2, mobile: false });
  await sleep(800);

  await c.navigate('http://127.0.0.1:8770/');
  await sleep(800);
  await c.evaluate(`localStorage.clear(); location.reload();`);
  await sleep(1600);

  const health = await c.evaluate(`({contract:!document.getElementById('view-contract').hidden, title:document.title})`);
  console.log('boot', JSON.stringify(health));
  await shot(c, '01-contract.png');

  // start
  await c.clickSel('#start-btn');
  await sleep(900);
  await shot(c, '02-problem.png');

  // think for a while before answering (keeps the recorded durations plausible)
  await sleep(38000);
  // wrong intuitive answer on problem 1
  await c.evaluate(`document.getElementById('answer').focus()`);
  await c.insert('0.10');
  await sleep(400);
  await c.clickSel('#answer-form button[type=submit]');
  await sleep(900);
  const fb = await c.evaluate(`document.getElementById('feedback').textContent.trim().slice(0,120)`);
  console.log('feedback:', fb);
  await shot(c, '03-feedback-lure.png');

  // hint ladder
  await c.clickSel('#stuck-btn');
  await sleep(700);
  const h = await c.evaluate(`({lvl:document.getElementById('hint-level').textContent, why:document.getElementById('hint-why').textContent})`);
  console.log('hint', JSON.stringify(h));
  await shot(c, '04-hint.png');

  // correct answer
  await c.evaluate(`(()=>{const a=document.getElementById('answer');a.value='';a.focus();return 1;})()`);
  await c.insert('0.05');
  await sleep(300);
  await c.clickSel('#answer-form button[type=submit]');
  await sleep(900);
  const refl = await c.evaluate(`!document.getElementById('reflect').hidden`);
  console.log('reflection open:', refl);
  await c.evaluate(`document.getElementById('reflect-input').focus()`);
  await c.insert('I subtracted first and got 0.10. Writing b + (b+1) = 1.10 was the step that fixed it.');
  await sleep(500);
  await shot(c, '05-reflection.png');

  await c.clickSel('#reflect-save');
  await sleep(700);

  // problem 2: solve unaided
  await sleep(26000);
  await c.evaluate(`document.getElementById('answer').focus()`);
  await c.insert('5');
  await sleep(300);
  await c.clickSel('#answer-form button[type=submit]');
  await sleep(700);
  await c.clickSel('#reflect-skip');
  await sleep(700);

  // problem 3: wrong twice then hint 3
  await sleep(44000);
  await c.evaluate(`document.getElementById('answer').focus()`);
  await c.insert('24');
  await sleep(300);
  await c.clickSel('#answer-form button[type=submit]');
  await sleep(700);
  await c.clickSel('#stuck-btn');
  await sleep(500);
  await c.clickSel('#deeper-btn');
  await sleep(600);
  const h3 = await c.evaluate(`document.getElementById('hint-level').textContent`);
  console.log('deep hint', h3);
  await c.evaluate(`(()=>{const a=document.getElementById('answer');a.value='';a.focus();return 1;})()`);
  await c.insert('47');
  await sleep(300);
  await c.clickSel('#answer-form button[type=submit]');
  await sleep(800);
  await c.clickSel('#reflect-save');
  await sleep(1000);

  const summary = await c.evaluate(`({
    visible: !document.getElementById('view-summary').hidden,
    label: document.getElementById('profile-label').textContent,
    metrics: [...document.querySelectorAll('.metric')].map(m=>m.textContent)
  })`);
  console.log('summary', JSON.stringify(summary, null, 1));
  await shot(c, '06-summary.png');

  // about dialog
  await c.evaluate(`document.getElementById('about').showModal()`);
  await sleep(600);
  await shot(c, '07-about.png');
  await c.evaluate(`document.getElementById('about').close()`);

  c.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
