# Booked-call video: Softwarelance pre-call brief

A vertical 1080x1920 video (~3 min) for people who have already booked a call.
It follows the Kallaway editing spec: a dark dot-grid background, a section title with an
italic serif accent, a motion-graphics stage in the top 70%, one caption word at a time,
a rounded card at the bottom, and hard cuts to full-screen punch cards on the key lines.
There's one accent colour (`#D0243A`).

There is no presenter footage for this script, so:

- the voiceover is AI-generated (Kokoro TTS, voice `am_michael`, 1.15x speed);
- the bottom card, where the face-cam would sit, is a **voice card** showing the brand,
  a waveform driven by the voiceover, and a progress bar with section ticks;
- the FULL inserts are full-screen punch cards instead of a full-screen face.

## Build

```bash
python3 work/vo.py            # work/script.txt -> assets/vo.wav + work/timing.json
python3 build.py              # timing.json -> index.html + compositions/*.html
npx hyperframes@0.8.91 check .
npx hyperframes@0.8.91 render . -q high -o renders/raw.mp4
ffmpeg -i renders/raw.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 256k renders/final.mp4
```

`vo.py` needs `pip install kokoro-onnx soundfile` and the Kokoro model that
`npx hyperframes tts` downloads to `~/.cache/hyperframes/tts` on first use.

## Editing

- **Script:** `work/script.txt`, one sentence per line. `## id` starts a section, and a line
  starting with `> ` becomes a full-screen punch card. `display|spoken_words` sets the
  pronunciation (for example `₹53.7|fifty-three_point_seven`), and `word@beat` names a
  beat that `build.py` syncs animation to.
- **Voice:** `python3 work/vo.py --voice am_adam --speed 1.1`. Other voices: `am_michael`,
  `am_adam`, `am_eric`, `am_liam`, `bm_george`, `bm_daniel`, `af_heart`, `hm_omega`.
- **Word timing:** each clause is synthesized separately. Within a clause, words are split
  by phoneme length and snapped to energy dips, so captions can be about ±0.1s off.
  Whisper would give exact timings, but its model host (huggingface.co) is blocked in
  cloud sessions.
- **Punch-card text** is in `PUNCH` in `build.py`, in the same order as the `>` lines.

## Using real footage later

If the presenter records this script, the `ad-shoot` project's pipeline
(`work/edl.py`, face card, jump-cut punch-ins) can replace the voice card and the
punch cards with the talking head.
