// Render the opening frame by frame into a silent video:
// node render-video.mjs landscape|vertical out.mp4 [fps]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
const [fmt, out, fpsArg = '60'] = process.argv.slice(2);
const fps = +fpsArg;
const b = await chromium.launch();
const p = await b.newPage();
p.on('pageerror', e => console.log('ERR', e.message));
await p.goto(`http://127.0.0.1:8765/src/opening.html?render=1&format=${fmt}`);
await p.waitForFunction(() => document.documentElement.dataset.ready === '1');
const ev = await p.evaluate(() => EVENTS());
fs.writeFileSync(out.replace(/\.mp4$/, '.events.json'), JSON.stringify(ev, null, 2));
const n = Math.round(ev.duration * fps);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709',
  '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = 0; i < n; i++) {
  const d = await p.evaluate(t => { frame(t); return document.getElementById('c').toDataURL('image/png'); }, i / fps);
  const buf = Buffer.from(d.split(',')[1], 'base64');
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 120 === 0) console.log(fmt, i, '/', n);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await b.close();
