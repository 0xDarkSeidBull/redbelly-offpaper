#!/bin/sh
# Rebuild every deliverable from source. Needs node 18+, python3 with numpy and Pillow, ffmpeg.
#   cd tools && npm install && cd .. && ./build.sh
set -e
cd "$(dirname "$0")"
D=deliverables
mkdir -p $D/01-identity-sheet $D/02-cover-art $D/03-thumbnails/examples $D/03-thumbnails/template $D/04-opening-sequence src/previews build
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 & SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1

echo "cover"
node tools/snap.mjs cover.html $D/02-cover-art/off-paper-cover-3000x3000.png
python3 -c "from PIL import Image; Image.open('$D/02-cover-art/off-paper-cover-3000x3000.png').convert('RGB').resize((1400,1400), Image.LANCZOS).save('$D/02-cover-art/off-paper-cover-1400x1400.jpg', quality=95)"

echo "thumbnails"
T="render=1"
node tools/snap.mjs thumbnail.html $D/03-thumbnails/examples/off-paper-ep32-thumbnail.png "$T&ep=32&title=Notes%20from%20the%20research%20frontline&guest=Vincent%20Gramoli&org=Redbelly%20Network&photo1=photos/vincent-gramoli.png&fx1=0.5&fy1=0.3&z1=1.6"
node tools/snap.mjs thumbnail.html $D/03-thumbnails/examples/off-paper-ep31-thumbnail.png "$T&ep=31&title=What%27s%20new%20at%20Tokeniser&guest=Matt%20Mills&org=Tokeniser&photo1=photos/matt-mills.jpg&fy1=0.4"
node tools/snap.mjs thumbnail.html $D/03-thumbnails/examples/off-paper-ep26-thumbnail.png "$T&ep=26&title=Redbelly%20and%20Tokeniser%20in%20conversation&guest=Alan%20Burt%20%26%20Matt%20Mills&org=Redbelly%20Network%20and%20Tokeniser&photo1=photos/alan-burt.png&fx1=0.6&z1=0.8&photo2=photos/matt-mills.jpg&fy2=0.38"
python3 tools/make_svg.py src/brand/tokeniser-logo-on-dark.png $D/03-thumbnails/template/off-paper-thumbnail-template.svg

echo "opening sequence"
node tools/render-video.mjs landscape build/opening-landscape-silent.mp4 60
node tools/render-video.mjs vertical build/opening-vertical-silent.mp4 60
python3 tools/audio.py build/opening-landscape-silent.events.json build/music-raw.wav
sh tools/master.sh build/music-raw.wav $D/04-opening-sequence/off-paper-opening-music.wav
for f in landscape:16x9 vertical:9x16; do
  n=${f%%:*}; r=${f##*:}
  ffmpeg -hide_banner -loglevel error -y -i build/opening-$n-silent.mp4 -i $D/04-opening-sequence/off-paper-opening-music.wav \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart $D/04-opening-sequence/off-paper-opening-$r.mp4
done

echo "identity sheet"
node tools/stills.mjs landscape build/landscape.png 2.2,3.5,5.6,8.4,9.6,12.0
node tools/stills.mjs vertical build/vertical.png 2.2,6.4,12.0
python3 tools/previews.py build $D src/previews
node tools/pdf.mjs $D/01-identity-sheet/off-paper-identity-sheet.pdf $D/01-identity-sheet/off-paper-identity-sheet.png

python3 check.py
