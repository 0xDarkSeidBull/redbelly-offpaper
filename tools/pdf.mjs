// Identity sheet to PDF and PNG: node pdf.mjs out.pdf out.png
import { chromium } from 'playwright';
const [pdf, png] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1588, height: 1123 }, deviceScaleFactor: 2 });
p.on('pageerror', e => console.log('ERR', e.message));
await p.goto('http://127.0.0.1:8765/src/identity.html');
await p.waitForFunction(() => document.documentElement.dataset.ready === '1');
await p.waitForTimeout(300);
await p.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true });
await p.screenshot({ path: png, fullPage: true });
await b.close();
