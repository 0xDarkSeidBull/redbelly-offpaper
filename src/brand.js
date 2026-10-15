// Off Paper - Powered by Tokeniser: shared identity code.
// Every visual (cover, thumbnails, opening sequence, identity sheet) draws from this file,
// so colours, type and graphic devices stay identical across the show.

const SHOW_NAME = 'Off Paper - Powered by Tokeniser';
const NAME_MAIN = 'Off Paper';
const NAME_SUB = '- Powered by Tokeniser';

// Tokeniser palette, nothing else is used.
const P = {
  slate: '#343740', mint: '#A2FFC8', lightMint: '#DAFDE5',
  lightBlue: '#C9DBF1', blue: '#323B70', teal: '#009C9C', orange: '#FF9A81',
};

// Tokeniser rules for graphic devices and photos.
const DEVICE_ON_SOLID = 0.7;
const DEVICE_ON_PHOTO = 0.6;
const PHOTO_SLATE_OVERLAY = 0.3;

const FONT = 'Montserrat';

function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}

function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = {
  inOut: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  out: t => 1 - Math.pow(1 - t, 3),
  outQuint: t => 1 - Math.pow(1 - t, 5),
  in: t => t * t * t,
};
const seg = (t, a, b) => clamp((t - a) / (b - a));

async function loadFonts() {
  const weights = [400, 500, 600, 700, 800];
  await Promise.all(weights.map(w => document.fonts.load(`${w} 40px ${FONT}`, 'Off Paper - Powered by Tokeniser 0123456789')));
  await document.fonts.ready;
}

function loadImage(src) {
  return new Promise((res, rej) => {
    const im = new Image();
    im.onload = () => res(im);
    im.onerror = rej;
    im.src = src;
  });
}

// Device 1, the cut sheet: a page outline with its top right corner cut at 45 degrees.
function sheetPath(ctx, x, y, w, h, cut) {
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + w - cut, y);
  ctx.lineTo(x + w, y + cut);
  ctx.lineTo(x + w, y + h);
  ctx.lineTo(x, y + h);
  ctx.closePath();
}

// Device 2, ledger lines: rows of rounded bars that read as a printed page, never as words.
function ledgerRows(count, seed, minLen = 0.45) {
  const r = rng(seed);
  const rows = [];
  for (let i = 0; i < count; i++) rows.push(i === 0 ? 0.62 : minLen + (1 - minLen) * r());
  return rows;
}

function drawLedgerLines(ctx, x, y, w, rows, gap, thick, color, alpha) {
  ctx.save();
  ctx.fillStyle = rgba(color, alpha);
  rows.forEach((len, i) => {
    roundRect(ctx, x, y + i * gap, w * len, thick, thick / 2);
    ctx.fill();
  });
  ctx.restore();
}

// Device 3, token tiles: square tiles on a strict grid. The emblem is a 3x3 tile grid
// with the top right tile missing, the same corner the sheet is cut at.
const EMBLEM_CELLS = [[0, 0], [1, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]];

function drawEmblem(ctx, x, y, size, color, alpha) {
  const g = size * 0.1;
  const s = (size - 2 * g) / 3;
  ctx.save();
  ctx.fillStyle = rgba(color, alpha);
  for (const [cx, cy] of EMBLEM_CELLS) {
    ctx.fillRect(x + cx * (s + g), y + cy * (s + g), s, s);
  }
  ctx.restore();
}

function drawTileField(ctx, x, y, cols, rows, cell, gap, color, alpha, keep) {
  ctx.save();
  ctx.fillStyle = rgba(color, alpha);
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    if (keep && !keep(c, r)) continue;
    ctx.fillRect(x + c * (cell + gap), y + r * (cell + gap), cell, cell);
  }
  ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function font(weight, px) { return `${weight} ${px}px ${FONT}`; }

// Show name lockup. Stacked: NAME_MAIN over NAME_SUB.
// Inline: one line. Both read exactly as the show name.
function drawName(ctx, x, y, size, opts = {}) {
  const { align = 'left', main = P.lightMint, sub = P.mint, layout = 'stack', subScale = 0.3 } = opts;
  ctx.save();
  ctx.textBaseline = 'alphabetic';
  if (layout === 'inline') {
    ctx.font = font(800, size);
    const wMain = ctx.measureText(NAME_MAIN + ' ').width;
    ctx.font = font(500, size);
    const wSub = ctx.measureText(NAME_SUB).width;
    let x0 = align === 'center' ? x - (wMain + wSub) / 2 : align === 'right' ? x - wMain - wSub : x;
    ctx.textAlign = 'left';
    ctx.font = font(800, size); ctx.fillStyle = main; ctx.fillText(NAME_MAIN + ' ', x0, y);
    ctx.font = font(500, size); ctx.fillStyle = sub; ctx.fillText(NAME_SUB, x0 + wMain, y);
    ctx.restore();
    return { width: wMain + wSub, height: size };
  }
  ctx.textAlign = align;
  ctx.font = font(800, size);
  ctx.fillStyle = main;
  ctx.fillText(NAME_MAIN, x, y);
  const w1 = ctx.measureText(NAME_MAIN).width;
  const subPx = size * subScale;
  ctx.font = font(600, subPx);
  ctx.fillStyle = sub;
  ctx.fillText(NAME_SUB, x, y + subPx * 1.75);
  const w2 = ctx.measureText(NAME_SUB).width;
  ctx.restore();
  return { width: Math.max(w1, w2), height: size + subPx * 1.75 };
}

// The supplied logo is only ever scaled uniformly; never recoloured or redrawn.
// Crop boxes trim the transparent padding of the supplied PNGs.
const LOGO_BOX = {
  dark: { src: 'brand/tokeniser-logo-on-dark.png', crop: [454, 460, 3259, 539] },
  light: { src: 'brand/tokeniser-logo-slate-green-icon.png', crop: [400, 78, 3495, 580] },
};

function drawLogo(ctx, img, kind, x, y, width, alpha = 1) {
  const [sx, sy, sw, sh] = LOGO_BOX[kind].crop;
  const h = width * sh / sw;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.drawImage(img, sx, sy, sw, sh, x, y, width, h);
  ctx.restore();
  return h;
}

// Photos: grayscale, then a 30 percent Slate overlay, as the Tokeniser photo rule asks.
function drawPhoto(ctx, img, x, y, w, h, focus = [0.5, 0.35], zoom = 1) {
  // Cover fit, then zoom. Zoom under 1 is for cut-out photos: the image sits on the
  // Light Blue backdrop, anchored to the bottom edge.
  const k = Math.max(w / img.width, h / img.height) * zoom;
  const dw = img.width * k, dh = img.height * k;
  let ox = w / 2 - focus[0] * dw, oy = h / 2 - focus[1] * dh;
  ox = dw >= w ? clamp(ox, w - dw, 0) : (w - dw) * focus[0];
  oy = dh >= h ? clamp(oy, h - dh, 0) : h - dh;
  ctx.save();
  ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  ctx.fillStyle = P.lightBlue; ctx.fillRect(x, y, w, h);
  ctx.filter = 'grayscale(1) contrast(1.05)';
  ctx.drawImage(img, x + ox, y + oy, dw, dh);
  ctx.filter = 'none';
  ctx.fillStyle = rgba(P.slate, PHOTO_SLATE_OVERLAY);
  ctx.fillRect(x, y, w, h);
  ctx.restore();
}

if (typeof window !== 'undefined') {
  Object.assign(window, {
    SHOW_NAME, NAME_MAIN, NAME_SUB, P, DEVICE_ON_SOLID, DEVICE_ON_PHOTO, PHOTO_SLATE_OVERLAY, FONT,
    rgba, rng, clamp, lerp, ease, seg, loadFonts, loadImage, sheetPath, ledgerRows, drawLedgerLines,
    EMBLEM_CELLS, drawEmblem, drawTileField, roundRect, font, drawName, LOGO_BOX, drawLogo, drawPhoto,
  });
}
