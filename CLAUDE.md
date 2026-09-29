# Claude + Video Editing

Claude generates and edits video from prompts. The core feature is **motion graphics**:
short, design-led, unnarrated pieces (kinetic type, stat count-ups, charts, logo stings,
lower-thirds, maps, animated headlines) rendered to MP4 or a transparent overlay.

## Toolchain

| Tool | Role |
| --- | --- |
| [HyperFrames](https://hyperframes.heygen.com) (`hyperframes@0.8.91`) | HTML + GSAP compositions → preview, check, render |
| Whisper (whisper.cpp via `npx hyperframes transcribe`) | Word-level transcripts for captions and beat-synced overlays |
| ffmpeg | Encoding, trimming, audio extraction, format conversion |
| ffprobe | Verifying inputs and renders (duration, resolution, fps, codecs) |

The SessionStart hook (`.claude/hooks/session-start.sh`) installs ffmpeg/ffprobe and the
HyperFrames skills in web sessions.

## Workflow

- **Start at the `/hyperframes` skill** for any video request. It routes short motion
  graphics to `/motion-graphics`; longer, narrated, or footage-based work goes elsewhere.
- Each piece is its own HyperFrames project under `videos/<kebab-name>/`, scaffolded with:
  ```bash
  npx hyperframes@0.8.91 init videos/<name> --non-interactive --example=blank --skill=motion-graphics
  ```
  Never run `hyperframes init` in the repo root. Run commands inside the project as
  `(cd videos/<name> && ...)`.
- The root `index.html` is a thin host; scenes live in `compositions/*.html` sub-compositions
  (everything inside `<template>`), each registering a paused GSAP timeline on
  `window.__timelines["<composition-id>"]`.
- Loop: `npx hyperframes check .` → `npx hyperframes snapshot . --at <times>` (look at
  `snapshots/contact-sheet.jpg`) → `npx hyperframes render . -q high -o renders/video.mp4`
  → verify with `ffprobe`.

## Conventions

- **Vendor scripts locally.** Load GSAP from `assets/vendor/gsap.min.js`, not a CDN. The
  render browser can't always reach CDNs, and local copies keep renders reproducible.
- **Fonts:** reference Google Fonts families by `font-family` only; the HyperFrames
  compiler fetches and injects deterministic `@font-face` rules. Don't add `<link>` tags.
- Keep colors in CSS custom properties on `#root`; no scattered inline hex values.
- Deterministic only: no `Date.now()`, `Math.random()`, or network fetches in compositions.
- `renders/` and `snapshots/` are gitignored; regenerate them.

## Known environment limits (cloud sessions)

- Whisper model downloads come from `huggingface.co` (whisper.cpp) or
  `openaipublic.azureedge.net` (openai-whisper). If the network policy blocks them,
  `transcribe` fails with HTTP 403. Allow those hosts in the environment's network settings.
- `npx hyperframes tts` needs `pip install kokoro-onnx soundfile`.
