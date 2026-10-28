# Off Paper - Powered by Tokeniser

Visual identity, cover art, thumbnail template and opening sequence for the relaunch of Redbelly Insights as **Off Paper - Powered by Tokeniser**.

The idea behind everything: real world paperwork becoming tokens on chain. A page outline with ledger lines (the paper) breaks into square tiles (the tokens), and the tiles lock into a grid (the chain). It is shown with shapes, motion and sound only.

Open `index.html` to see everything on one page.

## Deliverables

| # | Brief item | File |
|---|---|---|
| 1 | Identity sheet | `deliverables/01-identity-sheet/off-paper-identity-sheet.pdf` (2 pages A3), plus a PNG |
| 2 | Cover art, square | `deliverables/02-cover-art/off-paper-cover-3000x3000.png`, plus a 1400 x 1400 JPG |
| 3 | Editable thumbnail template | `src/thumbnail.html` (browser maker, free) and `deliverables/03-thumbnails/template/off-paper-thumbnail-template.svg` (Figma, Penpot or Inkscape, all free) |
| 3 | Three finished thumbnails, 1920 x 1080 | `deliverables/03-thumbnails/examples/` (EP 32, EP 31, EP 26) |
| 4 | Opening sequence with audio | `deliverables/04-opening-sequence/off-paper-opening-16x9.mp4` (1920 x 1080) and `off-paper-opening-9x16.mp4` (1080 x 1920). Both are H.264 at 60 fps with AAC 48 kHz stereo, 15.0 s long. The music master is a separate WAV. |
| 5 | Project files | `src/` (every visual), `tools/` (renderers and music), `build.sh`, `check.py` |
| 6 | Licence proof | `deliverables/06-licences/LICENCES.md` and the Montserrat OFL |

## Making a new thumbnail (no design skills needed)

1. Open `src/thumbnail.html` in any browser. On the hosted site it is the "Make a thumbnail" button. It is free and needs no account or install.
2. Type the episode number, title, guest name and organisation, then choose the guest photo. For a second guest, add a second photo and join the names with "&".
3. Use the sliders to frame the face. The phone preview shows the thumbnail at real feed size. If the title would need more than three lines, a warning appears: shorten the title.
4. Click "Download PNG". You get a 1920 x 1080 file named after the episode.

Colours, fonts, logo, layout and the photo treatment (grayscale with a 30 percent Slate overlay) are locked, so every episode matches.

**In Figma instead:** drag `off-paper-thumbnail-template.svg` onto a Figma canvas. Each slot is a named layer: "Episode number", "Title line 1" to "Title line 3", "Guest name", "Guest organisation" and "Guest photo". To change the photo, select the image inside "Guest photo", choose Fill, then Choose image, and keep the grayscale and the overlay layer. Montserrat is built into Figma. Penpot and Inkscape open the same file.

## Identity in short

- **Colours:** Tokeniser palette only. Slate is the base, Light Mint is for the name and titles, Mint for accents and tiles, Light Blue for secondary text and the photo backdrop, Blue for light in motion. Teal is for light backgrounds. Orange is left out of show art.
- **Type:** Montserrat only. ExtraBold for the name and titles, SemiBold for the sub line, Bold for guest names, Medium for organisations.
- **Show name:** always "Off Paper - Powered by Tokeniser". The stacked version puts "Off Paper" over "- Powered by Tokeniser". The text comes from one constant in `src/brand.js`.
- **Logo:** the three supplied PNG files, unaltered and only scaled evenly. On dark backgrounds use `tokeniser-logo-on-dark.png`; on light, `tokeniser-logo-slate-green-icon.png`.
- **Graphic devices:** cut sheet, ledger lines, token tiles and the emblem (3 x 3 tiles with the top right tile missing). They sit at 70 percent opacity on solid colour and 60 percent on photos. Photos carry a 30 percent Slate overlay.

## Opening sequence timing

| Time | Picture | Sound |
|---|---|---|
| 0.0 to 2.5 s | A page outline draws in, then its ledger lines | D minor pad fades in |
| 2.7 to 4.1 s | A Mint scan passes down the page and turns each line into tiles | A fine tick per line, and an arpeggio starts |
| 4.1 to 7.0 s | The tiles leave the page and lock into an 8 x 8 ledger, row by row | A low pulse, and a click per locked row |
| 7.0 to 8.8 s | Links draw between the tiles, and a wave turns them Mint (verified) | A soft bell run |
| 8.9 to 10.0 s | The grid folds into the emblem; the corner tiles fall away | A riser |
| 10.0 to 11.7 s | The show name and the Tokeniser logo appear | Resolves to D major, with a low hit |
| 11.7 to 14.0 s | Clean hold | Pad holds |
| 14.0 to 15.0 s | Fade to solid Slate, so an episode can cut straight in | Fades to silence |

There is no voice and there are no words. The only text drawn is the show name, and the Tokeniser logo is the supplied image. The audio is mastered to -16 LUFS integrated with a true peak of -1.5 dBTP.

## Rebuilding

Requirements: Node 18 or newer, Python 3 with numpy and Pillow, FFmpeg, and poppler-utils for `pdffonts`.

```
cd tools && npm install && cd ..
./build.sh
```

`build.sh` starts a local web server, renders the cover, the thumbnails, the SVG template, both videos frame by frame (60 fps), the music, the identity sheet PDF and the previews, and then runs `check.py`. A full build takes about four minutes.

To change the opening, edit `src/opening.html`. Open it in a browser to watch it play live, or add `?format=vertical` for the 9:16 layout and `?t=9.5` to freeze one moment. The music follows the timings the renderer writes, so it stays in sync.

## Verification

`python3 check.py` runs 148 checks against the brief:

- file formats and sizes: cover 3000 x 3000, thumbnails 1920 x 1080, videos at 1920 x 1080 and 1080 x 1920, 60 fps, with an audio track, 10 to 20 seconds long
- both videos end on solid Slate
- loudness falls between -17.5 and -14.5 LUFS
- the logo files match the supplied downloads by SHA-256
- every colour in every source file is from the Tokeniser palette
- the cover's pixels are palette colours or the allowed opacity blends
- Montserrat is the only typeface, and the only font embedded in the PDF
- the show name is never spelled another way
- the opening draws no text but the show name
- the thumbnail template has all of its slots
- the 70, 60 and 30 percent opacity rules hold
- no personal credit (names, handles or signature lines) appears anywhere in the deliverable

## Hosting

The repository is a static site. Serve the folder with any web server, such as Caddy or nginx, and open `index.html`. No build step is needed to view it.

Do not let the server hand out `.git` or the ignored files. A clone's `.git` folder holds local logs that name the machine and user that ran git there. With Caddy, block them before `file_server`:

```
@hidden path /.git /.git/* /.gitignore /.credit-names
respond @hidden 404
```
