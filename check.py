"""Verify the Off Paper deliverables against the TASK-36 brief.

Run after ./build.sh:  python3 check.py
Needs python3 with Pillow, plus ffmpeg, ffprobe and pdffonts on the path.
Each check prints PASS or FAIL; the exit code is the number of failures.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import warnings
import wave

from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

ROOT = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ROOT, "deliverables")
PALETTE = {"343740", "A2FFC8", "DAFDE5", "C9DBF1", "323B70", "009C9C", "FF9A81"}
PALETTE_RGB = {tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in PALETTE}
SHOW_NAME = "Off Paper - Powered by Tokeniser"
SUPPLIED = {  # sha256 of the files downloaded from the brief's resource links
    "src/brand/tokeniser-logo-on-dark.png": "6952027cc97a7293e3f8b46874efc7d3532ea700e66e7c4142179d4e18c788dc",
    "src/brand/tokeniser-logo-on-mint.png": "483ed1e207e52bac194e3956c0f2801cf51b81bc1afd2229bdf9073411081e65",
    "src/brand/tokeniser-logo-slate-green-icon.png": "56d05ff1ba1ef6cccf22f4723a63957a6708af68fbed27edcdf67e1e577e7cd7",
}
SOURCES = ["src/brand.js", "src/cover.html", "src/thumbnail.html", "src/opening.html", "src/identity.html",
           "src/fonts.css", "tools/make_svg.py", "index.html",
           "deliverables/03-thumbnails/template/off-paper-thumbnail-template.svg"]

fails = 0


def check(ok, label, detail=""):
    global fails
    print(("PASS " if ok else "FAIL ") + label + (f"  ({detail})" if detail else ""))
    if not ok:
        fails += 1


def p(*a):
    return os.path.join(ROOT, *a)


def read(rel):
    path = p(rel)
    if rel.endswith(".svg"):
        # Skip embedded base64 images, check only the markup.
        return re.sub(r"base64,[A-Za-z0-9+/=]+", "base64,", open(path).read())
    return open(path, encoding="utf8").read()


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def frame_at(path, t):
    tmp = p("build", "_frame.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", path, "-frames:v", "1", tmp], check=True)
    return Image.open(tmp).convert("RGB")


print("Deliverable 1, identity sheet")
pdf = p("deliverables/01-identity-sheet/off-paper-identity-sheet.pdf")
check(os.path.exists(pdf), "identity sheet PDF exists")
fonts = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout.splitlines()[2:]
names = {l.split()[0].split("+")[-1] for l in fonts if l.strip()}
check(names and all(n.startswith("Montserrat") for n in names), "identity sheet PDF embeds only Montserrat", ", ".join(sorted(names)))
check(os.path.exists(p("deliverables/01-identity-sheet/off-paper-identity-sheet.png")), "identity sheet PNG exists")

print("Deliverable 2, cover art")
cov = Image.open(p("deliverables/02-cover-art/off-paper-cover-3000x3000.png"))
check(cov.size == (3000, 3000), "cover is square 3000 x 3000", str(cov.size))
small = Image.open(p("deliverables/02-cover-art/off-paper-cover-1400x1400.jpg"))
check(small.size == (1400, 1400), "cover 1400 x 1400 JPG for platforms with a size cap")
# Every solid pixel of the cover is a palette colour or an alpha blend of two palette colours.
px = cov.convert("RGB").resize((600, 600), Image.NEAREST).getdata()
counts = {}
for c in px:
    counts[c] = counts.get(c, 0) + 1
major = [c for c, n in counts.items() if n > 600 * 600 * 0.002]


def is_blend(c):
    for a in PALETTE_RGB:
        for b in PALETTE_RGB:
            for t in (0.3, 0.6, 0.7, 1.0):
                if all(abs(c[i] - (a[i] * t + b[i] * (1 - t))) <= 3 for i in range(3)):
                    return True
    return False


bad = [c for c in major if not is_blend(c)]
check(not bad, "cover uses only palette colours (direct or at the 70/60/30 percent rules)", f"{len(major)} main colours")

print("Deliverable 3, thumbnails")
for ep in ("ep32", "ep31", "ep26"):
    im = Image.open(p(f"deliverables/03-thumbnails/examples/off-paper-{ep}-thumbnail.png"))
    check(im.size == (1920, 1080), f"{ep} thumbnail 16:9 at 1920 x 1080")
svg = read("deliverables/03-thumbnails/template/off-paper-thumbnail-template.svg")
for slot in ("Episode number", "Title line 1", "Guest name", "Guest photo"):
    check(f'id="{slot}' in svg, f"SVG template has an editable '{slot}' layer")
th = read("src/thumbnail.html")
check("TITLE_MIN = 84" in th and "TITLE_LINES = 3" in th, "maker keeps titles 84 px or larger, at most 3 lines")
check(84 * 360 / 1920 >= 15.7, "smallest title is about 16 px on a 360 px wide phone thumbnail", f"{84 * 360 / 1920:.1f} px")

print("Deliverable 4, opening sequence")
for name, (w, h) in (("16x9", (1920, 1080)), ("9x16", (1080, 1920))):
    path = p(f"deliverables/04-opening-sequence/off-paper-opening-{name}.mp4")
    info = probe(path)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = [s for s in info["streams"] if s["codec_type"] == "audio"]
    num, den = map(int, v["r_frame_rate"].split("/"))
    dur = float(info["format"]["duration"])
    check((v["width"], v["height"]) == (w, h), f"{name} is {w} x {h}")
    check(num / den >= 24, f"{name} frame rate {num / den:.0f} fps")
    check(v["codec_name"] == "h264" and path.endswith(".mp4"), f"{name} H.264 MP4")
    check(len(a) == 1 and a[0]["codec_name"] == "aac", f"{name} has an AAC audio track")
    check(10 <= dur <= 20, f"{name} runs {dur:.1f} s, inside 10 to 20 s")
    end = frame_at(path, dur - 0.1)
    mean = [sum(ch) / len(ch) for ch in zip(*end.resize((64, 64)).getdata())]
    check(all(abs(m - s) < 3 for m, s in zip(mean, (0x34, 0x37, 0x40))), f"{name} ends on solid Slate", str([round(m) for m in mean]))
op = read("src/opening.html")
texts = re.findall(r"fillText\(([^,]+),", op)
check(texts and all(t.strip() in ("NAME_MAIN", "NAME_SUB") for t in texts), "opening draws no text but the show name", ", ".join(texts))
loud = subprocess.run(["ffmpeg", "-hide_banner", "-i", p("deliverables/04-opening-sequence/off-paper-opening-16x9.mp4"),
                       "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
lj = json.loads(loud[loud.rindex("{"):loud.rindex("}") + 1])
check(-17.5 <= float(lj["input_i"]) <= -14.5 and float(lj["input_tp"]) <= -1.0,
      "audio is balanced for podcast and YouTube", f"{lj['input_i']} LUFS, {lj['input_tp']} dBTP")
with wave.open(p("deliverables/04-opening-sequence/off-paper-opening-music.wav")) as wv:
    check(wv.getframerate() == 48000 and wv.getnchannels() == 2, "music master is 48 kHz stereo WAV")
audio_src = read("tools/audio.py")
check("import" in audio_src and not re.search(r"\.(wav|mp3|flac|ogg)['\"]\s*\)", audio_src.replace("out_path", "")),
      "music is synthesised in code, no sample files are loaded")

print("Deliverable 5 and 6, project files and licences")
for f in ("src/brand.js", "src/cover.html", "src/thumbnail.html", "src/opening.html", "src/identity.html",
          "tools/audio.py", "tools/render-video.mjs", "build.sh"):
    check(os.path.exists(p(f)), f"project file {f}")
check(os.path.exists(p("deliverables/06-licences/LICENCES.md")), "licence notes present")
check(os.path.exists(p("deliverables/06-licences/Montserrat-OFL.txt")), "Montserrat SIL Open Font License included")

print("Brand rules")
for rel, digest in SUPPLIED.items():
    check(hashlib.sha256(open(p(rel), "rb").read()).hexdigest() == digest, f"logo file unaltered: {os.path.basename(rel)}")
bj = read("src/brand.js")
check("const SHOW_NAME = 'Off Paper - Powered by Tokeniser';" in bj, "show name constant reads exactly as briefed")
check("NAME_MAIN = 'Off Paper'" in bj and "NAME_SUB = '- Powered by Tokeniser'" in bj, "stacked lines join to the exact show name")
check("DEVICE_ON_SOLID = 0.7" in bj and "DEVICE_ON_PHOTO = 0.6" in bj and "PHOTO_SLATE_OVERLAY = 0.3" in bj,
      "device opacity 70/60 and 30 percent Slate photo overlay")
for rel in SOURCES:
    s = read(rel)
    hexes = {h.upper() for h in re.findall(r"#([0-9A-Fa-f]{6})\b", s)}
    check(hexes <= PALETTE, f"{rel}: only palette hex colours", ", ".join(sorted(hexes - PALETTE)))
    rgbs = {tuple(map(int, m)) for m in re.findall(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", s)}
    check(rgbs <= PALETTE_RGB, f"{rel}: only palette rgb colours", str(sorted(rgbs - PALETTE_RGB)))
    fams = set(re.findall(r"font-family\s*[:=]\s*['\"]?([A-Za-z ]+)", s)) | set(re.findall(r"font:\s*\d+\s+[\d.]+\w+\s+([A-Za-z]+)", s))
    check(fams <= {"Montserrat", "var"}, f"{rel}: Montserrat only", ", ".join(sorted(fams)))
    s_rules = s.replace('Never "Off-Paper", "OffPaper", all capitals', "")  # the rule text itself
    for wrong in ("Off-Paper", "OffPaper", "OFF PAPER", "Off paper", "Off Paper –", "Off Paper —", "Off Paper:"):
        check(wrong not in s_rules, f"{rel}: show name not written as '{wrong}'")
    # Every "Off Paper" is the full name, the NAME_MAIN constant, or the first line of a
    # stacked lockup whose second line "- Powered by Tokeniser" follows within the same element.
    loose = [m.start() for m in re.finditer(r"Off Paper(?! - Powered by Tokeniser)", s)
             if "- Powered by Tokeniser" not in s[m.start():m.start() + 80]
             and not s[max(0, m.start() - 20):m.start()].endswith("NAME_MAIN = '")]
    check(not loose, f"{rel}: every 'Off Paper' is the full name or the stacked lockup", f"{len(loose)} loose")

print("No personal credit")
names_file = p(".credit-names")
names = [l.strip() for l in open(names_file) if l.strip()] if os.path.exists(names_file) else []
hits = []
for base in ("deliverables", "src", "tools", "index.html", "README.md", "check.py", "build.sh"):
    path = p(base)
    files = [path] if os.path.isfile(path) else [os.path.join(dp, f) for dp, _, fs in os.walk(path) if "node_modules" not in dp for f in fs]
    for f in files:
        if f.endswith((".png", ".jpg", ".mp4", ".wav", ".pdf", ".ttf")) or f.endswith("OFL.txt"):
            continue
        s = open(f, encoding="utf8", errors="ignore").read().lower()
        for n in names + ([] if f.endswith("check.py") else ["made by", "designed by", "created by"]):
            if n.lower() in s:
                hits.append(f"{os.path.relpath(f, ROOT)}: {n}")
check(not hits, "no names, handles or made by lines in the deliverable", "; ".join(hits[:5]))
for f in ("deliverables/02-cover-art/off-paper-cover-3000x3000.png",):
    meta = Image.open(p(f)).info
    check(not any(k.lower() in ("author", "artist", "copyright") for k in meta), f"no author metadata in {os.path.basename(f)}")

print()
print("All checks passed." if fails == 0 else f"{fails} check(s) failed.")
sys.exit(fails)
