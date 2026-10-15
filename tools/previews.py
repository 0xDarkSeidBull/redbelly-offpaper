"""Small JPG previews for the identity sheet and the showcase page.
usage: python3 previews.py build_dir deliverables_dir out_dir"""
import glob
import os
import sys

from PIL import Image

build, deliv, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(build, "*_[0-9].png")):
    im = Image.open(f).convert("RGB")
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(out, os.path.basename(f)[:-4] + ".jpg"), quality=90)
pairs = {"cover": "02-cover-art/off-paper-cover-3000x3000.png"}
for ep in ("ep32", "ep31", "ep26"):
    pairs[ep] = f"03-thumbnails/examples/off-paper-{ep}-thumbnail.png"
for name, rel in pairs.items():
    im = Image.open(os.path.join(deliv, rel)).convert("RGB")
    im.thumbnail((960, 960), Image.LANCZOS)
    im.save(os.path.join(out, name + ".jpg"), quality=90)
