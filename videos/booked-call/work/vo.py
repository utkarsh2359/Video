"""Voiceover + word timings from work/script.txt.

Kokoro TTS (the model `npx hyperframes tts` caches) speaks the script one
clause at a time, so every clause boundary is known exactly. Inside a clause,
word boundaries are placed by phoneme length and then snapped to the nearest
energy dip. Pauses between clauses are ours, kept tight (no dead air).

    python3 work/vo.py [--voice am_michael] [--speed 1.15]

Writes assets/vo.wav and work/timing.json.
"""

import argparse
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from kokoro_onnx.tokenizer import Tokenizer

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "hyperframes" / "tts"
SR = 24000
GAP = {",": 0.09, ";": 0.12, ":": 0.14, ".": 0.24, "?": 0.26, "!": 0.24}
SECTION_GAP = 0.34
LEAD_IN = 0.15


def parse(path):
    """-> list of sections {id, lines: [{full, tokens: [{text, spoken, beat}]}]}"""
    sections = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or (line.startswith("#") and not line.startswith("## ")):
            continue
        if line.startswith("## "):
            sections.append({"id": line[3:].strip(), "lines": []})
            continue
        full = line.startswith("> ")
        if full:
            line = line[2:]
        toks = []
        for tok in line.split():
            beat = None
            if "@" in tok:
                tok, beat = tok.split("@", 1)
            text, _, spoken = tok.partition("|")
            toks.append({"text": text, "spoken": (spoken or text).replace("_", " "), "beat": beat})
        sections[-1]["lines"].append({"full": full, "tokens": toks})
    return sections


def rms_frames(audio, hop=0.005, win=0.02):
    h, w = int(SR * hop), int(SR * win)
    n = max(1, (len(audio) - w) // h + 1)
    return np.array([np.sqrt(np.mean(audio[i * h:i * h + w] ** 2) + 1e-12) for i in range(n)]), hop


def word_bounds(audio, weights):
    """Boundaries (seconds, len = words + 1) inside one synthesized clause."""
    dur = len(audio) / SR
    cum = np.concatenate([[0], np.cumsum(weights)]) / sum(weights)
    bounds = list(cum * dur)
    env, hop = rms_frames(audio)
    for i in range(1, len(bounds) - 1):
        t = bounds[i]
        lo = max(int((t - 0.07) / hop), 0)
        hi = min(int((t + 0.07) / hop) + 1, len(env))
        if hi > lo:
            bounds[i] = (lo + int(np.argmin(env[lo:hi]))) * hop + 0.01
    for i in range(1, len(bounds)):  # keep monotonic, min 60 ms per word
        bounds[i] = max(bounds[i], bounds[i - 1] + 0.06)
    bounds[-1] = max(bounds[-1], dur)
    return bounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=1.15)
    args = ap.parse_args()

    model = Kokoro(str(CACHE / "models" / "kokoro-v1.0.onnx"), str(CACHE / "voices" / "voices-v1.0.bin"))
    tok = Tokenizer()
    sections = parse(ROOT / "work" / "script.txt")

    out = [np.zeros(int(SR * LEAD_IN), dtype=np.float32)]
    t = LEAD_IN
    words, sec_times, full = [], [], []
    for si, sec in enumerate(sections):
        if si:
            out.append(np.zeros(int(SR * SECTION_GAP), dtype=np.float32))
            t += SECTION_GAP
        sec_start = t
        for line in sec["lines"]:
            line_start = t
            # split the line into clauses at punctuation
            clauses, cur = [], []
            for tk in line["tokens"]:
                cur.append(tk)
                if re.search(r'[,.?!:;]["”]?$', tk["spoken"]):
                    clauses.append(cur)
                    cur = []
            if cur:
                clauses.append(cur)
            for ci, cl in enumerate(clauses):
                text = " ".join(tk["spoken"] for tk in cl)
                audio, sr = model.create(text, voice=args.voice, speed=args.speed, lang="en-us")
                assert sr == SR
                audio = np.asarray(audio, dtype=np.float32)
                weights = []
                for tk in cl:
                    ph = tok.phonemize(re.sub(r'["”“]', "", tk["spoken"]), "en-us")
                    weights.append(len(re.sub(r"[ˈˌ\s]", "", ph)) + 1.5)
                b = word_bounds(audio, weights)
                for tk, a, z in zip(cl, b, b[1:]):
                    words.append({"text": tk["text"], "start": round(t + a, 3), "end": round(t + z, 3),
                                  "section": sec["id"], "beat": tk["beat"]})
                out.append(audio)
                t += len(audio) / SR
                last = cl[-1]["spoken"].rstrip('"”')
                gap = GAP.get(last[-1], 0.06) if last else 0.06
                if ci == len(clauses) - 1 and line is sec["lines"][-1]:
                    gap = 0  # section gap follows
                out.append(np.zeros(int(SR * gap), dtype=np.float32))
                t += gap
            if line["full"]:
                full.append([round(line_start, 3), round(t, 3)])
        sec_times.append({"id": sec["id"], "start": round(sec_start, 3), "end": round(t, 3)})

    tail = 0.6
    out.append(np.zeros(int(SR * tail), dtype=np.float32))
    audio = np.concatenate(out)
    peak = np.max(np.abs(audio))
    audio = audio / peak * 0.89
    sf.write(ROOT / "assets" / "vo.wav", audio, SR)
    duration = round(len(audio) / SR, 3)

    # section boundaries meet in the middle of the gap; last section runs to the end
    for a, b in zip(sec_times, sec_times[1:]):
        mid = round((a["end"] + b["start"]) / 2, 3)
        a["end"], b["start"] = mid, mid
    sec_times[0]["start"] = 0
    sec_times[-1]["end"] = duration

    # loudness envelope for the waveform card (25 values/s)
    env, hop = rms_frames(audio, hop=0.04, win=0.04)
    env = np.clip(env / np.percentile(env, 98), 0, 1)

    beats = {}
    for w in words:
        if w["beat"]:
            beats.setdefault(w["section"], {})[w["beat"]] = w["start"]
    (ROOT / "work" / "timing.json").write_text(json.dumps({
        "voice": args.voice, "speed": args.speed, "duration": duration,
        "sections": sec_times, "full": full, "beats": beats,
        "words": [{k: w[k] for k in ("text", "start", "end", "section")} for w in words],
        "envelope": [round(float(x), 2) for x in env],
    }, indent=1))
    print(f"{duration:.2f}s, {len(words)} words, {len(full)} full inserts")
    for s in sec_times:
        print(f"  {s['id']:8s} {s['start']:7.2f} - {s['end']:7.2f}")


if __name__ == "__main__":
    main()
