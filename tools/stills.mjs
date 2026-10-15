// Contact sheet of the opening: node stills.mjs landscape|vertical out.png t1,t2,...
import { chromium } from 'playwright';
import fs from 'fs';
const [fmt, out, ts] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage();
p.on('pageerror', e => console.log('ERR', e.message));
await p.goto(`http://127.0.0.1:8765/src/opening.html?render=1&format=${fmt}`);
await p.waitForFunction(() => document.documentElement.dataset.ready === '1');
const shots = [];
for (const t of ts.split(',').map(Number)) {
  shots.push(await p.evaluate(t => { frame(t); return document.getElementById('c').toDataURL('image/png'); }, t));
}
shots.forEach((d, i) => fs.writeFileSync(out.replace('.png', `_${i}.png`), Buffer.from(d.split(',')[1], 'base64')));
await b.close();
