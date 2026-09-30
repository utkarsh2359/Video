# Ad shoot: D2C store redesign ad

Vertical 9:16 talking-head ad (~30s) selling a D2C store redesign / CRO service with a
refund-or-work-free guarantee. Footage review and cut list: [footage-review.md](footage-review.md).

## Getting the footage

The six selected clips are "Copy of IMG_08xx.MOV" files in the "Ad shoot" Drive folder,
shared as "Anyone with the link". Drive's connector caps downloads at 10 MB and the network
policy blocks drive.google.com, so download through the Drive API (www.googleapis.com is
reachable) with the `GDRIVE_API_KEY` environment variable:

```bash
mkdir -p footage
curl -sSL -o footage/IMG_0846.MOV \
  "https://www.googleapis.com/drive/v3/files/<copy_id>?alt=media&key=$GDRIVE_API_KEY"
```

Copy IDs are in the `cut` array of footage-review.md. Keep raw footage out of git (`footage/` is ignored).

## Edit plan

1. Download the 6 copies. Verify each with ffprobe (expect 1080x1920 HEVC .MOV, check rotation metadata).
2. Trim the ranges with ffmpeg (±0.5s pad), tighten on silence, remove pauses as jump cuts.
3. Transcribe (Whisper) for word-level captions; correct against the script.
4. Build a HyperFrames composition (1080x1920):
   - Hook (0846): "₹5L → ₹20L/month" text hit in the first second.
   - Proof (0866): stat graphics on the spoken words: 2% → 3.5% conversion,
     5% → 15% add-to-cart → checkout, +75% revenue count-up.
   - Guarantee (0873): "Refund or we work free" badge.
   - CTA (0872): end card with brand + "Link below".
   - Punch-in zooms on jump cuts; word-by-word captions in the lower safe zone.
5. Loudness-normalise to about -14 LUFS, render, verify with ffprobe.

Still needed from the client: script, reference screenshots, brand name/logo.

## Build (current)

```bash
(cd work && python3 edl.py)      # takes -> edl.json (needs footage/ + tx/)
python3 build.py                 # edl.json -> index.html + compositions/
npx hyperframes@0.8.91 check .
npx hyperframes@0.8.91 render . -q high -o renders/raw.mp4
ffmpeg -i renders/raw.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 256k renders/final.mp4
```

### Case-study screenshots (placeholders until provided)

The proof section shows labelled placeholder PDPs until these files exist. Drop in
full-page mobile screenshots (about 1170px wide, any height) and re-run `build.py`:

| File | Used for |
|---|---|
| `assets/cases/kalyntika-before.png` | "Here's a brand that already had a good website" (browser mockup) |
| `assets/cases/fitfeast-before.png`, `fitfeast-after.png` | Conversion rate 2% → 3.5% (phone, wipe before → after) |
| `assets/cases/toddlersart-before.png`, `toddlersart-after.png` | Add to cart → checkout 5% → 15% |

The sales chart is rebuilt from `assets/cases/dashboard-*-ref.png` (values in `build.py`,
`SALES_SEP` / `SALES_AUG`).
