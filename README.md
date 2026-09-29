# Claude + Video Editing

Prompt-driven video editing with Claude. The core feature is generating **motion graphics**:
kinetic type, stat count-ups, charts, logo stings, lower-thirds, and animated headlines.

Built on [HyperFrames](https://hyperframes.heygen.com) (HTML + GSAP → video), with
**Whisper** for word-level transcripts and **ffmpeg / ffprobe** for encoding and inspection.

## Requirements

- Node.js ≥ 22
- ffmpeg and ffprobe on `PATH`
- Chrome/Chromium (HyperFrames downloads one if needed; check with `npx hyperframes doctor`)

## Layout

```
videos/
  claude-video-editing-intro/   # starter motion graphic (6s title sting)
    index.html                  # host composition
    compositions/title.html     # the animated scene
    assets/vendor/gsap.min.js
```

Each motion graphic is a self-contained HyperFrames project under `videos/`.

## Try the starter

```bash
cd videos/claude-video-editing-intro
npx hyperframes@0.8.91 check .                         # lint, runtime, layout, contrast
npx hyperframes@0.8.91 preview                         # live Studio in the browser
npx hyperframes@0.8.91 render . -q high -o renders/video.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate renders/video.mp4
```

## New motion graphic

```bash
npx hyperframes@0.8.91 init videos/<name> --non-interactive --example=blank --skill=motion-graphics
```

Or just ask Claude, e.g. *"make an 8s kinetic-type sting that says 'Ship it'"*.

## Transcripts (Whisper)

```bash
npx hyperframes transcribe input.mp4 -m small.en          # writes transcript.json
npx hyperframes transcribe input.mp4 --to srt -o captions.srt
```
