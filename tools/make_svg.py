"""Write the editable thumbnail template as SVG for Figma, Penpot or Inkscape (all free).

Every slot is its own named layer: Episode number, Title line 1 to 3, Guest name,
Guest organisation, Guest photo. The geometry matches src/thumbnail.html.
usage: python3 make_svg.py logo.png out.svg [photo.jpg]
"""
import base64
import sys

logo_path, out = sys.argv[1], sys.argv[2]
photo = sys.argv[3] if len(sys.argv) > 3 else None
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()

W, H, M, PX, CUT = 1920, 1080, 96, 1100, 150
SLATE, MINT, LM, LB, BLUE = "#343740", "#A2FFC8", "#DAFDE5", "#C9DBF1", "#323B70"

# Supplied logo, cropped by viewBox only: 3259 x 539 of the 4167 x 1459 PNG.
lw = 230
lh = lw * 539 / 3259
logo = (f'<svg id="Tokeniser logo (do not edit)" x="{M}" y="{H - M - 50:.0f}" width="{lw}" height="{lh:.2f}" '
        f'viewBox="454 460 3259 539"><image width="4167" height="1459" href="data:image/png;base64,{b64(logo_path)}"/></svg>')

emblem = []
for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]):
    g, s = 5.6, (56 - 11.2) / 3
    emblem.append(f'<rect x="{M + cx * (s + g):.2f}" y="{84 + cy * (s + g):.2f}" width="{s:.2f}" height="{s:.2f}"/>')

tiles = []
for r in range(2):
    for k in range(6 - r * 2):
        x, y = PX - 150 + k * 50 + 8, H - 120 - r * 50
        on_photo = x >= PX
        tiles.append(f'<rect x="{x}" y="{y}" width="34" height="34" fill="{MINT if on_photo else LM}" '
                     f'fill-opacity="{0.6 if on_photo else 0.7}"/>')

panel = f"M{PX + CUT} 0H{W}V{H}H{PX}V{CUT}Z"
if photo:
    photo_el = (f'<image x="{PX}" y="0" width="{W - PX}" height="{H}" preserveAspectRatio="xMidYMid slice" '
                f'filter="url(#gray)" href="data:image/jpeg;base64,{b64(photo)}"/>')
else:
    photo_el = (f'<rect x="{PX}" y="0" width="{W - PX}" height="{H}" fill="{LB}"/>'
                f'<text x="{PX + (W - PX) / 2}" y="{H / 2}" text-anchor="middle" font-family="Montserrat" font-weight="700" '
                f'font-size="40" fill="{SLATE}">Drop guest photo here</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>Off Paper - Powered by Tokeniser, thumbnail template</title>
<defs>
  <clipPath id="panel"><path d="{panel}"/></clipPath>
  <filter id="gray"><feColorMatrix type="saturate" values="0"/></filter>
</defs>
<rect id="Background" width="{W}" height="{H}" fill="{SLATE}"/>
<g id="Guest photo" clip-path="url(#panel)">
  <g id="Photo (replace image, keep grayscale)">{photo_el}</g>
  <rect id="Slate overlay 30%" x="{PX}" y="0" width="{W - PX}" height="{H}" fill="{SLATE}" fill-opacity="0.3"/>
</g>
<g id="Tiles">{"".join(tiles)}</g>
<g id="Emblem" fill="{MINT}" fill-opacity="0.7">{"".join(emblem)}</g>
<text id="Show name" x="{M + 80}" y="128" font-family="Montserrat" font-size="34"><tspan font-weight="800" fill="{LM}">Off Paper </tspan><tspan font-weight="500" fill="{MINT}">- Powered by Tokeniser</tspan></text>
<g id="Episode number">
  <text x="{M}" y="349" font-family="Montserrat" font-weight="800" font-size="60" fill="{MINT}">EP 00</text>
  <rect x="{M + 200}" y="323" width="120" height="10" fill="{MINT}" fill-opacity="0.7"/>
</g>
<g id="Title (max 3 lines, 84 to 112 px)" font-family="Montserrat" font-weight="800" font-size="112" fill="{LM}">
  <text id="Title line 1" x="{M - 4}" y="493">Episode title</text>
  <text id="Title line 2" x="{M - 4}" y="614">goes here</text>
  <text id="Title line 3" x="{M - 4}" y="735"></text>
</g>
<text id="Guest name" x="{M}" y="821" font-family="Montserrat" font-weight="700" font-size="50" fill="{LM}">Guest Name</text>
<text id="Guest organisation" x="{M}" y="873" font-family="Montserrat" font-weight="500" font-size="36" fill="{LB}">Organisation</text>
{logo}
</svg>
'''
open(out, "w").write(svg)
