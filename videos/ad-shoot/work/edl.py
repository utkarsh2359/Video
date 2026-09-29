"""Build the ad's edit decision list from the per-take transcripts.

Picks one take per script line, removes every pause of MIN_GAP or longer
(detected with ffmpeg silencedetect), and maps each spoken word onto the
output timeline so captions can be timed one word at a time.

Writes edl.json: {"pieces": [...], "words": [...], "duration": s}
"""

import json
import re
import subprocess

NOISE_DB = -38
MIN_GAP = 0.25  # pauses at least this long are cut
PAD = 0.07  # breath kept either side of a cut
TAIL_MAX = 0.9  # cap on the last word's length when no silence is found

# (section, clip, first word start, last word start). Times come from the
# transcripts in tx/<clip>/transcript.json.
TAKES = [
    ("hook", "IMG_0846", 3.52, 10.64),  # D2C brand owners ... Now hear me out.
    ("problem", "IMG_0850", 1.20, 14.32),  # There is a bottleneck ... and spend more.
    ("problem", "IMG_0850", 31.28, 42.72),  # But on the other side ... stays the same.
    ("shark", "IMG_0857", 4.40, 17.36),  # And this is exactly what Shark Tank ... potential.
    ("proof", "IMG_0861", 5.92, 9.76),  # here is a brand ... competitors.
    ("proof", "IMG_0866", 4.56, 25.12),  # After a redesign ... conversion strategy.
    ("cta", "IMG_0872", 2.16, 5.60),  # Click the link below ... another level.
    ("guarantee", "IMG_0873", 239.50, 246.62),  # And if the new store ... until it does.
]

# Transcription fixes so captions match the script, keyed by (clip, word start).
# A value with spaces replaces one recognised word with several caption words
# spread across its time span; None drops the word.
FIXES = {
    ("IMG_0861", 5.92): "Here's",
    ("IMG_0861", 6.24): None,  # "is" folded into "Here's"
    ("IMG_0866", 5.28): "redesign,",
    ("IMG_0866", 9.60): "Add",
    ("IMG_0866", 9.92): "to cart",
    ("IMG_0866", 10.24): "to",
    ("IMG_0866", 17.84): "none",
    ("IMG_0866", 18.00): "of",
    ("IMG_0866", 18.16): None,
    ("IMG_0866", 22.48): "improving",
    ("IMG_0866", 23.60): "communication",
    ("IMG_0850", 35.12): "points,",
    ("IMG_0850", 41.68): None,  # "your conversion that stays" -> "your conversion stays"
    ("IMG_0850", 42.72): "same.",
}


def silences(clip):
    out = subprocess.run(
        ["ffmpeg", "-i", f"wav/{clip}.wav", "-af",
         f"silencedetect=noise={NOISE_DB}dB:d=0.12", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(starts, ends))


def build():
    pieces, words, t_out = [], [], 0.0
    for section, clip, first, last in TAKES:
        tx = json.load(open(f"tx/{clip}/transcript.json"))
        sil = silences(clip)
        ws = [w for w in tx if first - 0.01 <= w["start"] <= last + 0.01]
        start = max(0.0, ws[0]["start"] - PAD)
        # End where speech stops after the last word begins.
        after = [s for s, e in sil if s > ws[-1]["start"] + 0.1]
        end = min(after[0] if after else ws[-1]["end"], ws[-1]["start"] + TAIL_MAX) + PAD

        # Split the take at every pause >= MIN_GAP inside it.
        keep, cur = [], start
        for s, e in sil:
            if s > cur and e < end and e - s >= MIN_GAP:
                keep.append((cur, s + PAD))
                cur = e - PAD
        keep.append((cur, end))
        keep = [(a, b) for a, b in keep if b - a > 0.12]

        # A word belongs to the first piece that ends after it starts. Parakeet
        # often places a word's start inside the pause just before it, so clamp
        # it forward to the piece start instead of dropping it.
        placed = {i: [] for i in range(len(keep))}
        for w in ws:
            i = next((i for i, (a, b) in enumerate(keep) if w["start"] < b - 0.05), None)
            if i is not None:
                placed[i].append(w)
        for i, (a, b) in enumerate(keep):
            pieces.append({"section": section, "clip": clip, "in": round(a, 3),
                           "out": round(b, 3), "at": round(t_out, 3)})
            for w in placed[i]:
                fix = FIXES.get((clip, w["start"]), w["text"])
                if fix is None:
                    continue
                w0 = max(w["start"], a)
                w1 = max(min(w["end"], b), w0 + 0.08)
                parts = fix.split(" ")
                span = (w1 - w0) / len(parts)
                for k, p in enumerate(parts):
                    s0 = t_out + (w0 - a) + k * span
                    words.append({"text": p, "start": round(s0, 3),
                                  "end": round(s0 + span, 3), "section": section})
            t_out += b - a

    # Each caption word holds until the next one starts (no blank flicker).
    for w, nxt in zip(words, words[1:]):
        w["end"] = round(max(w["end"], nxt["start"]), 3)
    return {"pieces": pieces, "words": words, "duration": round(t_out, 3)}


if __name__ == "__main__":
    edl = build()
    json.dump(edl, open("edl.json", "w"), indent=1)
    print(f"{len(edl['pieces'])} pieces, {len(edl['words'])} words, {edl['duration']:.2f}s")
    for p in edl["pieces"]:
        print(f"{p['at']:6.2f}  {p['section']:9s} {p['clip']} {p['in']:7.2f}-{p['out']:7.2f}")
    print(" ".join(w["text"] for w in edl["words"]))
