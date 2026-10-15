// Render a page's canvas to PNG: node snap.mjs page.html out.png [query]
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const [page, out, query = ''] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1200, height: 1200 } });
p.on('console', m => console.log('page:', m.text()));
p.on('pageerror', e => console.log('ERR', e.message));
await p.goto('http://127.0.0.1:8765/src/' + page + (query ? '?' + query : ''));
await p.waitForFunction(() => document.documentElement.dataset.ready === '1', null, { timeout: 60000 });
const data = await p.evaluate(() => document.getElementById('c').toDataURL('image/png'));
fs.writeFileSync(out, Buffer.from(data.split(',')[1], 'base64'));
await b.close();
