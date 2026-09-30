"""Generate the booked-call video's HyperFrames compositions from work/timing.json.

Kallaway layout (see the style spec): dark dot-grid background, a section title
and a motion-graphics stage in the top 70%, one caption word at a time, and a
rounded card at the bottom. There is no presenter footage for this script, so
the bottom card is a "voice card" (brand + live waveform of the voiceover), and
the FULL inserts are full-screen punch cards instead of a full-screen face.
Stage beats are keyed to spoken words (`word@beat` in work/script.txt).

    python3 work/vo.py      # script -> assets/vo.wav + work/timing.json
    python3 build.py        # timing -> index.html + compositions/
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
TM = json.loads((ROOT / "work" / "timing.json").read_text())
D = TM["duration"]
W, H = 1080, 1920
FULL = [tuple(r) for r in TM["full"]]
SEC = {s["id"]: (s["start"], s["end"]) for s in TM["sections"]}
BEATS = TM["beats"]

PALETTE = """
  --bg: #0b0b0c;
  --card: #1a1a1c;
  --card2: #232326;
  --card-edge: rgba(255, 255, 255, 0.1);
  --ink: #ffffff;
  --muted: #a0a0a6;
  --dim: #3a3a3e;
  --accent: #d0243a;
  --glow: rgba(255, 59, 78, 0.5);
  --dot: rgba(255, 255, 255, 0.07);
"""

FONTS = """
@font-face { font-family: "Instrument Serif"; font-style: italic; font-weight: 400;
  src: url("assets/fonts/InstrumentSerif-Italic.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+2000-206F, U+2191, U+2193, U+2212; }
@font-face { font-family: "Instrument Serif"; font-style: italic; font-weight: 400;
  src: url("assets/fonts/InstrumentSerif-Italic-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+20A0-20C0, U+2113; }
"""

SHARED_CSS = """
.title { position: absolute; top: 150px; left: 50px; right: 50px; text-align: center;
  font-family: Inter, sans-serif; color: var(--ink); line-height: 1.1;
  text-shadow: 0 0 20px rgba(255,255,255,0.25); }
.title .l1, .title .l2 { display: block; font-size: 58px; font-weight: 800; letter-spacing: -0.02em; }
.title .l2 { margin-top: 4px; }
.tw { display: inline-block; }
.serif { font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400;
  font-size: 1.24em; letter-spacing: 0; }
.red { color: var(--accent); }
.ul { position: relative; display: inline-block; }
.ul::after { content: ""; position: absolute; left: 2%; right: 2%; bottom: 0; height: 5px;
  background: var(--accent); border-radius: 3px; transform: scaleX(var(--u, 0));
  transform-origin: left center; }
.hl { display: inline-block; background: var(--accent); color: #fff; padding: 0 16px 6px;
  border-radius: 12px; text-shadow: none; }
.stage { position: absolute; left: 0; top: 330px; width: 1080px; height: 850px; }
.cam { position: absolute; inset: 0; transform-origin: 50% 50%; }
.grp { position: absolute; inset: 0; }
.row { position: absolute; left: 0; right: 0; display: flex; justify-content: center;
  align-items: center; gap: 22px; }
.card { position: absolute; background: var(--card); border: 1px solid var(--card-edge);
  border-radius: 24px; box-shadow: 0 24px 60px rgba(0,0,0,0.55); color: var(--ink);
  font-family: Inter, sans-serif; }
.row > .card, .row > .chip { position: relative; }
.chip { position: absolute; display: inline-flex; align-items: center; gap: 14px;
  padding: 16px 28px; border-radius: 999px; background: var(--card);
  border: 1px solid var(--card-edge); color: var(--ink); font-family: Inter, sans-serif;
  font-weight: 800; font-size: 34px; letter-spacing: -0.01em; white-space: nowrap;
  box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.chip.redc { background: var(--accent); border-color: transparent; }
.chip svg { width: 38px; height: 38px; }
.label { font-family: Inter, sans-serif; font-weight: 700; font-size: 28px; color: var(--muted);
  letter-spacing: 0.08em; text-transform: uppercase; }
.big { font-family: Inter, sans-serif; font-weight: 900; color: var(--ink);
  letter-spacing: -0.04em; line-height: 1; }
.glow { filter: drop-shadow(0 0 28px var(--glow)); }
.tglow { text-shadow: 0 0 40px var(--glow); }
.muted { color: var(--muted); }
.stat { padding: 34px 40px; }
.stat .label { display: block; }
.stat .big { display: block; margin-top: 16px; }
.stat .sub { display: block; font-family: Inter, sans-serif; font-weight: 700; font-size: 30px;
  color: var(--muted); margin-top: 14px; }
.bar { position: absolute; bottom: 0; border-radius: 16px 16px 6px 6px; transform-origin: 50% 100%; }
.strike { position: absolute; left: -4%; top: 52%; height: 6px; width: 108%;
  background: var(--accent); border-radius: 3px; transform-origin: left center; transform: scaleX(0); }
.phone { position: absolute; width: 360px; height: 720px; border-radius: 52px; background: #000;
  border: 10px solid #2a2a2e; box-shadow: 0 30px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.08); }
.phone .scr { position: absolute; inset: 0; border-radius: 42px; overflow: hidden; background: #f4f2ee; }
.phone .notch { position: absolute; top: 12px; left: 50%; width: 100px; height: 28px; margin-left: -50px;
  border-radius: 20px; background: #000; z-index: 3; }
.pdp { position: absolute; inset: 0; padding: 58px 20px 20px; font-family: Inter, sans-serif; color: #1c1c1e; }
.pdp .nav { font-weight: 800; font-size: 20px; letter-spacing: 0.04em; margin-bottom: 14px; }
.pdp .img { height: 290px; border-radius: 14px; background: linear-gradient(135deg, #e6d9cf, #c7ad9b); }
.pdp .ln { height: 15px; border-radius: 8px; background: #d9d5ce; margin-top: 13px; }
.pdp .price { font-weight: 900; font-size: 30px; margin-top: 14px; }
.pdp .btn { margin-top: 16px; height: 56px; border-radius: 12px; background: #1c1c1e; color: #fff;
  font-weight: 800; font-size: 21px; display: flex; align-items: center; justify-content: center; }
.bubble { position: absolute; padding: 16px 24px; border-radius: 22px; background: #fff; color: #111;
  font-family: Inter, sans-serif; font-weight: 800; font-size: 28px; white-space: nowrap;
  box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.bubble.q::before { content: "?"; display: inline-flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; margin-right: 12px; border-radius: 50%; background: var(--accent);
  color: #fff; font-size: 24px; vertical-align: 2px; }
.icon { stroke: #fff; stroke-width: 6; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.icon .r { stroke: var(--accent); }
.pp { position: absolute; color: #ffffff; }
.num { display: inline-flex; align-items: center; justify-content: center; width: 72px; height: 72px;
  border-radius: 20px; background: var(--accent); color: #fff; font-family: Inter, sans-serif;
  font-weight: 900; font-size: 40px; flex: none; }
"""

# Simple line icons (viewBox 0 0 64 64).
ICONS = {
    "house": '<path d="M10 30 L32 12 L54 30"/><path d="M16 26 V52 H48 V26"/><path class="r" d="M27 52 V38 H37 V52"/>',
    "search": '<circle cx="28" cy="28" r="16"/><path class="r" d="M40 40 L54 54"/>',
    "phone": '<rect x="18" y="6" width="28" height="52" rx="6"/><path class="r" d="M28 50 H36"/>',
    "cursor": '<path d="M16 10 L48 34 L34 36 L42 52 L36 55 L28 39 L18 48 Z"/>',
    "cal": '<rect x="8" y="12" width="48" height="44" rx="8"/><path d="M8 26 H56 M20 6 V16 M44 6 V16"/><path class="r" d="M22 40 L29 47 L43 34"/>',
    "check": '<path class="r" d="M12 34 L26 48 L52 18"/>',
    "cross": '<path class="r" d="M16 16 L48 48 M48 16 L16 48"/>',
    "cart": '<path d="M6 10 H14 L20 42 H50 L56 20 H17"/><circle cx="24" cy="52" r="4"/><circle class="r" cx="46" cy="52" r="4"/>',
    "card": '<rect x="6" y="14" width="52" height="36" rx="6"/><path class="r" d="M6 26 H58"/><path d="M14 40 H26"/>',
    "page": '<rect x="12" y="6" width="40" height="52" rx="6"/><path d="M20 18 H44 M20 28 H44"/><path class="r" d="M20 40 H34"/>',
    "eye": '<path d="M4 32 C16 12 48 12 60 32 C48 52 16 52 4 32 Z"/><circle class="r" cx="32" cy="32" r="8"/>',
    "pct": '<circle cx="18" cy="18" r="7"/><circle class="r" cx="46" cy="46" r="7"/><path d="M50 12 L14 52"/>',
    "bag": '<path d="M12 22 H52 L48 56 H16 Z"/><path class="r" d="M24 22 V16 A8 8 0 0 1 40 16 V22"/>',
    "blocks": '<rect x="8" y="34" width="22" height="22" rx="3"/><rect x="34" y="34" width="22" height="22" rx="3"/><rect class="r" x="21" y="8" width="22" height="22" rx="3"/>',
    "tv": '<rect x="6" y="14" width="52" height="34" rx="6"/><path d="M22 56 H42"/><path class="r" d="M26 24 L40 31 L26 38 Z"/>',
    "up": '<path class="r" d="M8 50 L26 32 L36 42 L56 18"/><path class="r" d="M42 18 H56 V32"/>',
    "down": '<path class="r" d="M8 16 L26 34 L36 24 L56 48"/><path class="r" d="M42 48 H56 V34"/>',
    "bolt": '<path class="r" d="M36 4 L14 36 H30 L26 60 L50 26 H34 Z"/>',
    "people": '<circle cx="22" cy="20" r="9"/><path d="M6 54 C6 40 38 40 38 54"/><circle class="r" cx="44" cy="22" r="7"/><path class="r" d="M40 38 C52 38 58 44 58 54"/>',
}


def icon(name, size=64, cls=""):
    return (f'<svg class="icon {cls}" width="{size}" height="{size}" viewBox="0 0 64 64">'
            f'{ICONS[name]}</svg>')


PERSON = ('<svg width="56" height="64" viewBox="0 0 56 64"><circle cx="28" cy="18" r="12" fill="currentColor"/>'
          '<path d="M4 62 C4 38 52 38 52 62 Z" fill="currentColor"/></svg>')


def esc(s):
    return html.escape(s, quote=False)


def T(at):
    return at if isinstance(at, str) else f"{at:.3f}"


def L(g):
    return f"L({g:.3f})"


# ---------------------------------------------------------------------------
# GSAP snippet helpers. `at` is a JS expression or local seconds.

def enter(sel, at, dur=0.3, extra=""):
    return (f'tl.fromTo("{sel}", {{autoAlpha: 0, scale: 0.9, filter: "blur(10px)"}},'
            f' {{autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: {dur}, ease: "power3.out"{extra}}}, {T(at)});')


def enter_up(sel, at, dur=0.3, extra=""):
    return (f'tl.fromTo("{sel}", {{autoAlpha: 0, y: 30, filter: "blur(10px)"}},'
            f' {{autoAlpha: 1, y: 0, filter: "blur(0px)", duration: {dur}, ease: "power3.out"{extra}}}, {T(at)});')


def pop(sel, at, dur=0.25, extra=""):
    return (f'tl.fromTo("{sel}", {{autoAlpha: 0, scale: 0.6}},'
            f' {{autoAlpha: 1, scale: 1, duration: {dur}, ease: "back.out(2)"{extra}}}, {T(at)});')


def leave(sel, at, dur=0.2):
    return (f'tl.to("{sel}", {{autoAlpha: 0, filter: "blur(10px)", scale: 0.96,'
            f' duration: {dur}, ease: "power2.in"}}, {T(at)});')


def count(sel, at, dur, frm, to, fmt):
    """Seek-safe count-up: tween a proxy and write the formatted value."""
    return (f'(() => {{ const el = document.querySelector("{sel}"); const p = {{v: {frm}}};'
            f' tl.fromTo(p, {{v: {frm}}}, {{v: {to}, duration: {dur}, ease: "power2.out", immediateRender: false,'
            f' onUpdate: () => {{ el.textContent = {fmt}; }} }}, {T(at)}); }})();')


def draw(sel, at, dur=0.6, ease="power2.inOut"):
    return (f'tl.fromTo("{sel}", {{strokeDashoffset: 1}}, {{strokeDashoffset: 0, duration: {dur},'
            f' ease: "{ease}"}}, {T(at)});')


def grow(sel, at, dur=0.5, frm=0, to=1, extra=""):
    return (f'tl.fromTo("{sel}", {{scaleY: {frm}}}, {{scaleY: {to}, duration: {dur}, ease: "power3.out"{extra}}},'
            f' {T(at)});')


def growx(sel, at, dur=0.5, frm=0, to=1, extra=""):
    return (f'tl.fromTo("{sel}", {{scaleX: {frm}}}, {{scaleX: {to}, duration: {dur}, ease: "power3.out"{extra}}},'
            f' {T(at)});')


RUPEE_L = '"₹" + p.v.toFixed(1) + "L"'
INR = '"₹" + Math.round(p.v).toLocaleString("en-IN")'
PCT1 = 'p.v.toFixed(1) + "%"'
PCT0 = 'Math.round(p.v) + "%"'
INT = 'Math.round(p.v).toString()'


# ---------------------------------------------------------------------------
# Titles. `l2` marks the serif accent as *phrase*; style: ul | hl | red.

def title_html(tid, l1, l2, style="ul"):
    def words(s):
        out, acc = [], None
        for part in s.split(" "):
            if acc is not None:
                acc.append(part)
                if part.endswith("*"):
                    out.append(accent(" ".join(acc)))
                    acc = None
            elif part.startswith("*") and part.endswith("*") and len(part) > 1:
                out.append(accent(part))
            elif part.startswith("*"):
                acc = [part]
            else:
                out.append(f'<span class="tw">{esc(part)}</span>')
        return " ".join(out)

    def accent(p):
        p = esc(p.strip("*"))
        cls = {"ul": "serif ul", "hl": "serif hl", "red": "serif red"}[style]
        return f'<span class="tw"><span class="{cls}">{p}</span></span>'

    return (f'<div class="title" id="{tid}"><span class="l1">{words(l1)}</span>'
            f'<span class="l2">{words(l2)}</span></div>')


def title_js(tid, at, out=None, ul=False):
    js = [f'tl.fromTo("#{tid} .tw", {{autoAlpha: 0, y: 10, filter: "blur(12px)"}},'
          f' {{autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.27, ease: "power2.out", stagger: 0.066}}, {T(at)});']
    if ul:
        js.append(f'tl.fromTo("#{tid} .ul", {{"--u": 0}}, {{"--u": 1, duration: 0.5, ease: "power2.inOut"}}, {T(at)} + 0.45);')
    if out is not None:
        js.append(f'tl.to("#{tid}", {{autoAlpha: 0, filter: "blur(10px)", duration: 0.18, ease: "power2.in"}}, {T(out)} - 0.18);')
    return js


class Section:
    """Collects body HTML and GSAP lines for one stage composition."""

    def __init__(self, sid):
        self.sid = sid
        self.start, self.end = SEC[sid]
        self.b = BEATS.get(sid, {})
        self.body, self.js = [], []
        self.titles = []

    def t(self, beat, off=0.0):
        """Beat name -> local-time JS expression."""
        return L(self.b[beat] + off)

    def g(self, beat, off=0.0):
        return self.b[beat] + off

    def title(self, at_g, l1, l2, style="ul"):
        self.titles.append((at_g, l1, l2, style))

    def group(self, gid, t_in, t_out, inner):
        """A scene group: blurs in at t_in (global), blurs out before t_out."""
        self.body.append(f'<div class="grp" id="{gid}">{inner}</div>')
        self.js.append(f'tl.set("#{gid}", {{autoAlpha: 0}}, 0);')
        self.js.append(enter(f"#{gid}", L(t_in), 0.3))
        if t_out is not None and t_out < self.end - 0.05:
            self.js.append(leave(f"#{gid}", L(t_out - 0.2), 0.2))

    def add(self, *lines):
        self.js.extend(lines)

    def html(self):
        titles = []
        for i, (at, l1, l2, style) in enumerate(self.titles):
            tid = f"{self.sid}-t{i}"
            nxt = self.titles[i + 1][0] if i + 1 < len(self.titles) else None
            titles.append(title_html(tid, l1, l2, style))
            self.js[:0] = title_js(tid, L(max(at, self.start)), L(nxt) if nxt else None, style == "ul")
        return "\n".join(titles), "\n".join(self.body)


def full_ranges(a, b):
    return [(x, y) for x, y in FULL if a - 0.01 <= x < b]


# ---------------------------------------------------------------------------
# Sections

def s_hook():
    S = Section("hook")
    S.title(0, "Same Traffic.", "*More Orders.*", "ul")
    people = "".join(f'<div class="pp" id="hk-p{i}" style="left:{(i % 8) * 92}px; top:{(i // 8) * 96}px">{PERSON}</div>'
                     for i in range(32))
    S.group("hk-g1", S.start, None, f"""
      <div class="row" style="top:10px">
        <div class="chip" id="hk-meta">{icon("tv")} Ads</div>
        <div class="card" id="hk-spend" style="padding:18px 34px">
          <span class="label" style="font-size:22px">Ad spend / month</span><br>
          <span class="big" id="hk-spend-v" style="font-size:64px">₹0</span></div>
      </div>
      <svg width="1080" height="120" style="position:absolute; left:0; top:150px">
        <path id="hk-flow" d="M540 0 V110" stroke="#d0243a" stroke-width="6" stroke-dasharray="1"
          stroke-dashoffset="1" pathLength="1" fill="none"/></svg>
      <div id="hk-crowd" style="position:absolute; left:{(1080 - 7 * 92 - 56) // 2}px; top:290px; width:{7 * 92 + 56}px; height:380px">{people}</div>
      <div class="row" style="top:710px">
        <div class="chip" id="hk-visit">{icon("people")} Visitors</div>
        <div class="chip redc" id="hk-orders">{icon("bag")} Orders: <span id="hk-orders-v">1</span></div>
      </div>""")
    buyers1 = [11]
    buyers2 = [3, 11, 17, 22, 28, 30]
    S.add(
        pop("#hk-meta", 0.05), pop("#hk-spend", 0.2),
        count("#hk-spend-v", S.t("b_lakhs"), 1.2, 0, 480000, INR),
        'tl.fromTo("#hk-spend", {boxShadow: "0 0 0 rgba(208,36,58,0)"}, {boxShadow: "0 0 50px rgba(208,36,58,0.6)", duration: 0.3, yoyo: true, repeat: 1}, ' + S.t("b_ads") + ');',
        draw("#hk-flow", S.t("b_people", -0.2), 0.35),
        'tl.fromTo("#hk-crowd .pp", {autoAlpha: 0, y: -60, scale: 0.6}, {autoAlpha: 0.22, y: 0, scale: 1, duration: 0.3, ease: "power3.out", stagger: {each: 0.04, from: "random"}}, 0.4);',
        'tl.to("#hk-crowd .pp", {autoAlpha: 1, duration: 0.2, stagger: {each: 0.02, from: "center"}}, ' + S.t("b_people") + ');',
        enter("#hk-visit", S.t("b_store")),
        f'tl.to("#hk-p{buyers1[0]}", {{color: "#d0243a", scale: 1.2, duration: 0.2}}, {S.t("b_store", 0.2)});',
        pop("#hk-orders", S.t("b_store", 0.25)),
        'tl.to("#hk-crowd .pp", {opacity: 0.35, duration: 0.3}, ' + S.t("b_more") + ');',
        f'tl.to("{", ".join(f"#hk-p{i}" for i in buyers2)}", {{color: "#d0243a", opacity: 1, scale: 1.2, duration: 0.22, stagger: 0.09}}, {S.t("b_bought")});',
        count("#hk-orders-v", S.t("b_bought"), 0.55, 1, 6, INT),
        'tl.fromTo("#hk-orders", {scale: 1}, {scale: 1.12, duration: 0.18, yoyo: true, repeat: 1}, ' + S.t("b_bought", 0.5) + ');',
    )
    return S


SALES_SEP = [237, 218, 228, 262, 228, 300, 258, 358, 325, 316, 305, 280, 335, 308, 222,
             220, 175, 165, 172, 182, 190, 175, 240, 265, 198, 248, 332, 348, 258]
SALES_AUG = [172, 62, 55, 165, 162, 188, 193, 225, 232, 172, 200, 150, 160, 240, 272, 125,
             85, 82, 92, 125, 180, 193, 215, 223, 160, 198, 175, 155, 225, 255, 225]


def sales_path(values, w=840, h=300, days=31, top=400):
    pts = [(i * w / (days - 1), h - v / top * h) for i, v in enumerate(values)]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cx = (x0 + x1) / 2
        d += f" C{cx:.1f} {y0:.1f}, {cx:.1f} {y1:.1f}, {x1:.1f} {y1:.1f}"
    return d


def s_case():
    S = Section("case")
    S.title(S.start, "One D2C Brand. 30 Days.", "₹53.7L → *₹73.7L*", "hl")
    b = S.g
    # g1: brand + 30-day ring
    S.group("cs-g1", S.start, b("b_from"), f"""
      <div class="row" style="top:40px">
        <div class="chip" id="cs-d2c">{icon("bag")} D2C Brand</div>
        <div class="chip redc" id="cs-cro">CRO Redesign</div>
      </div>
      <svg id="cs-ring" width="440" height="440" viewBox="0 0 440 440" style="position:absolute; left:320px; top:220px">
        <circle cx="220" cy="220" r="190" stroke="#2a2a2e" stroke-width="26" fill="none"/>
        <circle id="cs-ring-arc" cx="220" cy="220" r="190" stroke="#d0243a" stroke-width="26" fill="none"
          stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"
          transform="rotate(-90 220 220)" class="glow"/>
      </svg>
      <div style="position:absolute; left:320px; top:220px; width:440px; height:440px; display:flex;
          flex-direction:column; align-items:center; justify-content:center">
        <span class="big" id="cs-days" style="font-size:170px">0</span>
        <span class="label">days</span></div>""")
    S.add(pop("#cs-d2c", S.t("b_brand")), pop("#cs-cro", S.t("b_redesign", -0.35)),
          draw("#cs-ring-arc", S.t("b_days", -0.5), 1.0, "power2.out"),
          count("#cs-days", S.t("b_days", -0.5), 1.0, 0, 30, INT))
    # g2: monthly sales + chart
    grid = "".join(f'<line x1="0" x2="840" y1="{y}" y2="{y}" stroke="#2a2a2e" stroke-width="2"/>' for y in (0, 75, 150, 225, 300))
    S.group("cs-g2", b("b_from"), b("b_day1"), f"""
      <div class="card" style="left:60px; top:20px; width:960px; height:790px">
        <div style="position:absolute; left:50px; top:40px"><span class="label">Monthly sales</span></div>
        <div class="big" id="cs-total" style="position:absolute; left:50px; top:92px; font-size:120px">₹53.7L</div>
        <div class="chip redc" id="cs-plus" style="position:absolute; right:50px; top:106px; font-size:44px">+₹20L</div>
        <div style="position:absolute; left:50px; top:250px; font-family:Inter; font-weight:700; font-size:26px; color:var(--muted)">
          <span style="color:#fff">━</span> Month before &nbsp;&nbsp; <span style="color:#d0243a">━</span> After redesign</div>
        <svg width="840" height="320" viewBox="0 -10 840 320" style="position:absolute; left:60px; top:330px; overflow:visible">
          {grid}
          <path id="cs-aug" d="{sales_path(SALES_AUG)}" stroke="#8a8a90" stroke-width="5" fill="none" pathLength="1"
            stroke-dasharray="1" stroke-dashoffset="1"/>
          <path id="cs-sep" d="{sales_path(SALES_SEP)}" stroke="#d0243a" stroke-width="7" fill="none" pathLength="1"
            stroke-dasharray="1" stroke-dashoffset="1" class="glow"/>
        </svg>
        <div style="position:absolute; left:60px; right:60px; top:680px; display:flex; justify-content:space-between;
          font-family:Inter; font-weight:700; font-size:24px; color:var(--muted)"><span>Day 1</span><span>Day 15</span><span>Day 30</span></div>
      </div>""")
    S.add(draw("#cs-aug", S.t("b_from"), 0.9), draw("#cs-sep", S.t("b_to", -0.1), 1.0),
          count("#cs-total", S.t("b_to"), 1.0, 53.7, 73.7, RUPEE_L),
          'tl.to("#cs-total", {color: "#ff3b4e", duration: 0.2}, ' + S.t("b_to", 1.0) + ');',
          pop("#cs-plus", S.t("b_to", 1.0), 0.3))
    # g3: per day bars
    S.group("cs-g3", b("b_day1"), b("b_best"), f"""
      <div class="row" style="top:20px"><span class="label" style="font-size:34px">Sales per day</span></div>
      <div style="position:absolute; left:180px; top:110px; width:720px; height:560px">
        <div class="bar" id="cs-bar1" style="left:40px; width:260px; height:{560 * 1.7 / 2.6:.0f}px; background:#3a3a3e"></div>
        <div class="bar glow" id="cs-bar2" style="left:420px; width:260px; height:{560 * 2.5 / 2.6:.0f}px; background:var(--accent)"></div>
        <div class="big" id="cs-v1" style="position:absolute; left:40px; width:260px; text-align:center; bottom:{560 * 1.7 / 2.6 + 20:.0f}px; font-size:76px">₹1.7L</div>
        <div class="big" id="cs-v2" style="position:absolute; left:420px; width:260px; text-align:center; bottom:{560 * 2.5 / 2.6 + 20:.0f}px; font-size:76px">₹1.7L</div>
      </div>
      <div style="position:absolute; left:180px; top:690px; width:720px; display:flex; font-family:Inter; font-weight:800;
        font-size:30px; color:var(--muted); text-transform:uppercase; letter-spacing:0.06em">
        <span style="margin-left:40px; width:260px; text-align:center">Before</span>
        <span style="margin-left:120px; width:260px; text-align:center; color:#fff">After</span></div>""")
    S.add(grow("#cs-bar1", S.t("b_day1"), 0.5), enter("#cs-v1", S.t("b_day1", 0.2)),
          grow("#cs-bar2", S.t("b_day2"), 0.7, 1.7 / 2.5), enter("#cs-v2", S.t("b_day2")),
          count("#cs-v2", S.t("b_day2"), 0.7, 1.7, 2.5, RUPEE_L))
    # g4: daily bars, best day
    n = len(SALES_SEP)
    best = SALES_SEP.index(max(SALES_SEP))
    bw, gap = 24, 6
    left0 = (1080 - n * (bw + gap)) // 2
    bars = "".join(f'<div class="bar dbar" id="cs-d{i}" style="left:{i * (bw + gap)}px; width:{bw}px; height:{v / 400 * 520:.0f}px;'
                   f' background:{"#d0243a" if i == best else "#4a4a50"}; border-radius:6px"></div>' for i, v in enumerate(SALES_SEP))
    S.group("cs-g4", b("b_best"), b("b_household"), f"""
      <div class="row" style="top:10px"><span class="label" style="font-size:34px">Every day, after the redesign</span></div>
      <div style="position:absolute; left:{left0}px; top:160px; width:{n * (bw + gap)}px; height:560px">
        <div style="position:absolute; left:0; right:0; bottom:{350 / 400 * 520:.0f}px; border-top:4px dashed rgba(208,36,58,0.8)"></div>
        {bars}</div>
      <div class="chip redc" id="cs-bestchip" style="left:{left0 + best * (bw + gap) - 170}px; top:95px; font-size:36px">Best day ₹3.5L+</div>""")
    S.add('tl.fromTo("#cs-g4 .dbar", {scaleY: 0}, {scaleY: 1, duration: 0.4, ease: "power3.out", stagger: 0.025}, ' + S.t("b_best") + ');',
          pop("#cs-bestchip", S.t("b_35")),
          f'tl.fromTo("#cs-d{best}", {{filter: "brightness(1)"}}, {{filter: "brightness(1.6)", duration: 0.25, yoyo: true, repeat: 1}}, {S.t("b_35")});')
    # g5: household + jump
    S.group("cs-g5", b("b_household"), b("b_aov"), f"""
      <div class="row" style="top:60px"><div class="chip" id="cs-house">{icon("house")} Regular household brand</div></div>
      <div class="row" style="top:230px">
        <svg width="220" height="220" viewBox="0 0 64 64" class="icon glow" id="cs-up">{ICONS["up"]}</svg>
        <span class="big tglow" id="cs-jump" style="font-size:230px">+37%</span></div>
      <div class="row" style="top:560px"><span class="label" style="font-size:34px">Month-on-month sales</span></div>""")
    S.add(pop("#cs-house", S.t("b_household")),
          enter("#cs-up", S.t("b_jump", -0.2)), count("#cs-jump", S.t("b_jump", -0.2), 0.8, 0, 37, '"+" + Math.round(p.v) + "%"'))
    # g6: AOV
    S.group("cs-g6", b("b_aov"), None, f"""
      <div class="card stat" id="cs-aovcard" style="left:140px; top:60px; width:800px; height:600px; text-align:center">
        <span class="label" style="font-size:32px">Average order value</span>
        <div style="margin-top:70px"><span class="big muted" id="cs-aovold" style="font-size:96px; position:relative">₹1,559<span class="strike" id="cs-aovstrike"></span></span></div>
        <div style="margin-top:40px"><span class="big tglow" id="cs-aovnew" style="font-size:170px; color:#ff3b4e">₹1,559</span></div>
      </div>
      <div class="row" style="top:700px"><div class="chip redc" id="cs-aovpct">+11% per order</div></div>""")
    S.add(enter("#cs-aovold", S.t("b_aov1")), enter("#cs-aovnew", S.t("b_aov2", -0.3)),
          count("#cs-aovnew", S.t("b_aov2", -0.3), 0.8, 1559, 1731, INR),
          growx("#cs-aovstrike", S.t("b_aov2", 0.2), 0.3), pop("#cs-aovpct", S.t("b_aov2", 0.5)))
    return S


def s_problem():
    S = Section("problem")
    b = S.g
    S.title(S.start, "When They Came To Us,", "Sales Were *Dropping*", "red")
    S.title(b("b_audit"), "Most Product Pages", "Don’t *Answer Questions*", "ul")
    down = "M0 40 C120 30, 200 90, 320 120 S 560 200, 700 300"
    S.group("pb-g1", S.start, b("b_ads"), f"""
      <div class="row" style="top:30px"><span class="label" style="font-size:34px">The month before</span></div>
      <svg width="700" height="320" style="position:absolute; left:190px; top:140px; overflow:visible">
        <path id="pb-line" d="{down}" stroke="#d0243a" stroke-width="10" fill="none" pathLength="1"
          stroke-dasharray="1" stroke-dashoffset="1" class="glow" stroke-linecap="round"/></svg>
      <div class="row" style="top:470px">
        <svg width="150" height="150" viewBox="0 0 64 64" class="icon" id="pb-dn">{ICONS["down"]}</svg>
        <span class="big red tglow" id="pb-7" style="font-size:200px">−7%</span></div>
      <div class="row" style="top:700px"><span class="label" style="font-size:32px">Sales</span></div>""")
    S.add(draw("#pb-line", S.t("b_drop", -0.2), 0.8), enter("#pb-dn", S.t("b_7")), pop("#pb-7", S.t("b_7")))
    items = [("Ads running", "check", "b_ads"), ("People visiting", "check", "b_visit"), ("People buying", "cross", None)]
    rows = "".join(f'<div class="card" id="pb-i{i}" style="left:140px; top:{60 + i * 220}px; width:800px; height:180px;'
                   f' display:flex; align-items:center; gap:34px; padding:0 50px">{icon(ic, 96)}'
                   f'<span class="big" style="font-size:64px; letter-spacing:-0.02em">{t}</span></div>'
                   for i, (t, ic, _) in enumerate(items))
    f_end = full_ranges(S.start, S.end)[0][1]
    S.group("pb-g2", b("b_ads"), b("b_audit"), rows)
    S.add(enter("#pb-i0", S.t("b_ads")), enter("#pb-i1", S.t("b_visit")), enter("#pb-i2", L(f_end - 0.3)),
          'tl.fromTo("#pb-i2", {borderColor: "rgba(255,255,255,0.1)"}, {borderColor: "rgba(208,36,58,1)", duration: 0.3}, ' + L(f_end) + ');')
    S.group("pb-g3", b("b_audit"), None, f"""
      <div class="chip" id="pb-audit" style="left:60px; top:0">{icon("search")} In most store audits</div>
      <div class="phone" id="pb-phone" style="left:360px; top:90px">
        <div class="scr"><div class="pdp"><div class="nav">YOURSTORE</div><div class="img"></div>
          <div class="ln" style="width:80%"></div><div class="ln" style="width:55%"></div>
          <div class="price">₹1,499</div><div class="btn">Add to cart</div>
          <div class="ln" style="width:90%"></div><div class="ln" style="width:65%"></div></div></div>
        <div class="notch"></div></div>
      <div class="bubble q" id="pb-q0" style="left:30px; top:180px">Will it suit me?</div>
      <div class="bubble q" id="pb-q1" style="left:640px; top:300px">When will it arrive?</div>
      <div class="bubble q" id="pb-q2" style="left:50px; top:470px">Is COD available?</div>
      <div class="bubble q" id="pb-q3" style="left:620px; top:600px">Is it worth ₹1,499?</div>
      <div class="bubble" id="pb-think" style="left:300px; top:380px; background:var(--accent); color:#fff; font-size:40px;
        padding:22px 34px">“I’ll think about it…”</div>""")
    S.add(pop("#pb-audit", S.t("b_audit", -0.1)), enter_up("#pb-phone", S.t("b_pdp", -0.1), 0.4),
          *[pop(f"#pb-q{i}", S.t("b_q", -0.55 + i * 0.22)) for i in range(4)],
          'tl.to("#pb-phone, #pb-q0, #pb-q1, #pb-q2, #pb-q3", {opacity: 0.25, duration: 0.3}, ' + S.t("b_leave") + ');',
          pop("#pb-think", S.t("b_leave", 0.25), 0.3),
          'tl.to("#pb-phone", {x: 700, rotation: 8, duration: 0.8, ease: "power2.in"}, ' + S.t("b_leave", 0.8) + ');')
    return S


def s_about():
    S = Section("about")
    b = S.g
    S.title(S.start, "At Softwarelance, We Fix", "What Happens *After The Click*", "ul")
    S.group("ab-g1", S.start, b("b_cust"), f"""
      <div class="row" style="top:10px"><div class="card" id="ab-logo" style="padding:22px 44px; font-size:60px; font-weight:900;
        letter-spacing:-0.03em">software<span class="red">lance</span></div></div>
      <div class="card stat" id="ab-s1" style="left:60px; top:230px; width:460px; height:360px">
        <span class="label">D2C brands</span><span class="big" id="ab-32" style="font-size:112px">0+</span>
        <span class="sub">worked with</span></div>
      <div class="card stat" id="ab-s2" style="left:560px; top:230px; width:460px; height:360px; border-color:rgba(208,36,58,0.7)">
        <span class="label">Revenue added</span><span class="big tglow" id="ab-46" style="font-size:112px; color:#ff3b4e">₹0Cr</span>
        <span class="sub">and counting</span></div>
      <div class="row" style="top:650px"><div class="chip" id="ab-click">{icon("cursor")} Ad click</div>
        <span class="big muted" style="font-size:60px">→</span>
        <div class="chip redc" id="ab-after">Everything after it</div></div>""")
    S.add(enter("#ab-logo", S.t("b_sl", -0.1)),
          enter("#ab-s1", S.t("b_32", -0.1)), count("#ab-32", S.t("b_32", -0.1), 0.8, 0, 32, 'Math.round(p.v) + "+"'),
          enter("#ab-s2", S.t("b_46", -0.1)), count("#ab-46", S.t("b_46", -0.1), 0.9, 0, 46, '"₹" + Math.round(p.v) + "Cr+"'))
    fr = full_ranges(S.start, S.end)[0]
    S.add(pop("#ab-click", L(fr[1])), pop("#ab-after", L(fr[1] + 0.25)))
    steps = [("page", "Product page", "b_pdp", 100, 100), ("cart", "Cart", "b_cart", 34, 58),
             ("card", "Checkout", "b_checkout", 14, 34), ("bag", "Orders", "b_orders", 5, 14)]
    rows = []
    for i, (ic, name, _, before, after) in enumerate(steps):
        y = 150 + i * 150
        rows.append(f'<div id="ab-st{i}" style="position:absolute; left:340px; top:{y}px; width:690px; height:120px">'
                    f'<div style="position:absolute; left:0; top:4px; display:flex; align-items:center; gap:16px">{icon(ic, 52)}'
                    f'<span class="big" style="font-size:40px; letter-spacing:-0.02em">{name}</span></div>'
                    f'<div style="position:absolute; left:0; top:72px; width:600px; height:34px; border-radius:17px; background:#232326">'
                    f'<div class="fbar" id="ab-bar{i}" style="position:absolute; left:0; top:0; height:34px; width:{after * 6}px;'
                    f' border-radius:17px; background:var(--accent); transform-origin:0 50%; transform:scaleX({before / after:.3f})"></div></div>'
                    f'<span class="big" id="ab-v{i}" style="position:absolute; left:620px; top:62px; font-size:40px">{before}%</span>'
                    f'<svg id="ab-ok{i}" width="52" height="52" viewBox="0 0 64 64" class="icon" style="position:absolute; left:440px; top:0">{ICONS["check"]}</svg>'
                    f'</div>')
    S.group("ab-g2", b("b_cust"), None, f"""
      <div class="phone" id="ab-phone" style="left:40px; top:120px; width:270px; height:540px; border-radius:40px">
        <div class="scr" style="border-radius:30px"><div class="pdp" style="padding:44px 14px 14px"><div class="nav" style="font-size:15px">YOURSTORE</div>
          <div class="img" style="height:200px"></div><div class="ln"></div><div class="ln" style="width:60%"></div>
          <div class="price" style="font-size:22px">₹1,499</div><div class="btn" style="height:42px; font-size:16px">Add to cart</div></div>
          <div id="ab-scan" style="position:absolute; left:0; right:0; top:0; height:6px; background:var(--accent);
            box-shadow:0 0 20px var(--glow)"></div></div><div class="notch" style="width:80px; margin-left:-40px"></div></div>
      <div class="chip" id="ab-cust" style="left:40px; top:30px; font-size:30px">{icon("eye")} Like your customer</div>
      {"".join(rows)}
      <div class="chip redc" id="ab-drop" style="left:600px; top:30px; font-size:30px">Drop-offs</div>
      <div class="row" style="top:760px"><div class="chip" id="ab-smooth">{icon("bolt")} Smoother flow, more orders</div></div>""")
    S.add(pop("#ab-cust", S.t("b_cust")), enter_up("#ab-phone", S.t("b_cust"), 0.4),
          'tl.fromTo("#ab-scan", {y: 0}, {y: 520, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: 1}, ' + S.t("b_phone") + ');',
          'tl.fromTo("#ab-g2 [id^=ab-st]", {autoAlpha: 0, x: 40}, {autoAlpha: 1, x: 0, duration: 0.3, ease: "power3.out", stagger: 0.12}, ' + S.t("b_drop", -0.4) + ');',
          pop("#ab-drop", S.t("b_drop")),
          'tl.set("#ab-g2 [id^=ab-ok]", {autoAlpha: 0}, 0);')
    for i, (_, _, beat, before, after) in enumerate(steps):
        at = S.t("b_redesign") if i == 0 else S.t(beat)
        S.add(pop(f"#ab-ok{i}", at))
        if i:
            S.add(growx(f"#ab-bar{i}", S.t("b_fix", i * 0.15), 0.7, before / after, 1),
                  count(f"#ab-v{i}", S.t("b_fix", i * 0.15), 0.7, before, after, PCT0))
    S.add(pop("#ab-smooth", S.t("b_smooth")),
          'tl.fromTo("#ab-v3", {color: "#ffffff"}, {color: "#ff3b4e", duration: 0.2}, ' + S.t("b_orders") + ');',
          'tl.fromTo("#ab-st3", {scale: 1}, {scale: 1.06, duration: 0.2, yoyo: true, repeat: 1, transformOrigin: "0% 50%"}, ' + S.t("b_orders") + ');')
    return S


def s_proof():
    S = Section("proof")
    b = S.g
    S.title(S.start, "It’s Not Just", "*One Brand*", "ul")
    S.title(b("b_kids"), "Kids’ Toys Brand:", "Conversion *2% → 3.5%*", "hl")
    S.group("pf-g1", b("b_one"), b("b_kids"), f"""
      <div class="card" id="pf-ff" style="left:120px; top:40px; width:840px; height:560px; text-align:center">
        <div style="margin-top:60px"><span class="big" style="font-size:120px; letter-spacing:-0.05em">FitFeast</span></div>
        <div style="margin-top:34px; display:flex; justify-content:center"><div class="chip" id="pf-shark" style="position:relative">{icon("tv")} As seen on Shark Tank India</div></div>
        <div style="margin-top:44px"><span class="big tglow" id="pf-2cr" style="font-size:110px; color:#ff3b4e">₹2Cr+</span>
          <span class="label" style="font-size:30px">&nbsp;/ month</span></div>
      </div>
      <div class="row" style="top:650px"><div class="chip redc" id="pf-trust">{icon("check")} Trusts us with their product pages</div></div>""")
    S.add(enter("#pf-ff", S.t("b_ff", -0.1)), pop("#pf-shark", S.t("b_shark")), enter("#pf-2cr", S.t("b_2cr")),
          count("#pf-2cr", S.t("b_2cr"), 0.6, 0, 2, '"₹" + Math.round(p.v) + "Cr+"'),
          pop("#pf-trust", S.t("b_trust")))
    S.group("pf-g2", b("b_kids"), b("b_atc"), f"""
      <div class="row" style="top:30px"><div class="chip" id="pf-kid">{icon("blocks")} Kids’ toys brand</div></div>
      <div class="card stat" id="pf-stuck" style="left:190px; top:170px; width:700px; height:400px; text-align:center">
        <span class="label">Conversion rate</span><span class="big" style="font-size:180px">2%</span>
        <svg width="560" height="60" style="margin-top:10px"><path id="pf-flat" d="M0 30 H560" stroke="#8a8a90" stroke-width="6"
          stroke-dasharray="14 12" fill="none"/></svg></div>
      <div class="row" style="top:620px"><div class="chip" id="pf-r1">{icon("page")} Product page rebuilt</div>
        <div class="chip" id="pf-r2">{icon("cart")} Cart rebuilt</div></div>""")
    S.add(pop("#pf-kid", S.t("b_kids")), enter("#pf-stuck", S.t("b_2", -0.2)),
          pop("#pf-r1", S.t("b_rebuilt")), pop("#pf-r2", S.t("b_rebuilt", 0.35)))

    def pair(pid, label, x, frm, to, maxv, fmt):
        h = 440
        return (f'<div style="position:absolute; left:{x}px; top:60px; width:440px; height:{h + 180}px">'
                f'<div class="label" style="text-align:center">{label}</div>'
                f'<div style="position:absolute; left:40px; top:120px; width:360px; height:{h}px">'
                f'<div class="bar" id="{pid}-a" style="left:0; width:150px; height:{frm / maxv * h:.0f}px; background:#4a4a50"></div>'
                f'<div class="bar glow" id="{pid}-b" style="left:210px; width:150px; height:{to / maxv * h:.0f}px; background:var(--accent)"></div>'
                f'<div class="big" style="position:absolute; left:0; width:150px; text-align:center; bottom:{frm / maxv * h + 14:.0f}px; font-size:52px">{fmt(frm)}</div>'
                f'<div class="big" id="{pid}-v" style="position:absolute; left:180px; width:210px; text-align:center; bottom:{to / maxv * h + 14:.0f}px; font-size:64px">{fmt(frm)}</div>'
                f'</div></div>')
    S.group("pf-g3", b("b_atc"), None, f"""
      {pair("pf-atc", "Add to cart", 80, 5, 15, 16, lambda v: f"{v:g}%")}
      {pair("pf-cr", "Conversion", 560, 2, 3.5, 4, lambda v: f"{v:g}%")}
      <div style="position:absolute; left:620px; right:30px; top:{180 + 440 - 1.8 / 4 * 440:.0f}px; border-top:4px dashed #ffffff;"
        id="pf-avg"><span class="label" style="position:absolute; right:0; top:-34px; font-size:20px; color:#fff">Avg</span></div>
      <div class="row" style="top:720px"><div class="chip redc" id="pf-double">≈ 2× the Indian average of 1.8%</div></div>""")
    S.add(grow("#pf-atc-a", S.t("b_5"), 0.4), grow("#pf-atc-b", S.t("b_15"), 0.6, 5 / 15), enter("#pf-atc-v", S.t("b_15")),
          count("#pf-atc-v", S.t("b_15"), 0.6, 5, 15, PCT0),
          'tl.fromTo("#pf-cr-a, #pf-cr-b, #pf-cr-v", {autoAlpha: 0}, {autoAlpha: 1, duration: 0.01}, ' + S.t("b_cr") + ');',
          'tl.set("#pf-cr-a, #pf-cr-b, #pf-cr-v", {autoAlpha: 0}, 0);',
          grow("#pf-cr-a", S.t("b_cr2"), 0.4), grow("#pf-cr-b", S.t("b_cr35"), 0.6, 2 / 3.5),
          count("#pf-cr-v", S.t("b_cr35"), 0.6, 2, 3.5, PCT1),
          growx("#pf-avg", S.t("b_double", -0.3), 0.5, 0, 1, ', transformOrigin: "0% 50%"'),
          pop("#pf-double", S.t("b_double", 0.2)))
    return S


def s_promise():
    S = Section("promise")
    b = S.g
    S.title(S.start, "The Average Indian Store", "Converts At *1.8%*", "hl")
    dots = "".join(f'<div class="dot" id="pm-d{i}" style="left:{(i % 10) * 64}px; top:{(i // 10) * 56}px"></div>' for i in range(100))
    S.group("pm-g1", b("b_exact", -0.1), None, f"""
      <div class="row" style="top:0"><div class="chip" id="pm-note" style="font-size:28px; color:var(--muted)">Results vary by brand</div></div>
      <div id="pm-grid" style="position:absolute; left:{(1080 - 9 * 64 - 36) // 2}px; top:110px; width:612px; height:560px">{dots}</div>
      <div class="row" style="top:710px"><span class="big" style="font-size:44px; letter-spacing:-0.02em">
        <span class="red">1.8</span> of every <span id="pm-100">100</span> visitors buy</span></div>
      <div class="chip redc" id="pm-room" style="left:310px; top:320px; font-size:52px; padding:22px 40px">{icon("up")} Room to grow</div>""")
    S.body.insert(0, '<style>#promise-root .dot { position: absolute; width: 36px; height: 36px; border-radius: 50%; background: #3a3a3e; }</style>')
    S.add(pop("#pm-note", S.t("b_exact")),
          'tl.fromTo("#pm-grid .dot", {autoAlpha: 0, scale: 0}, {autoAlpha: 1, scale: 1, duration: 0.2, stagger: {each: 0.006, grid: [10, 10], from: "start"}}, ' + S.t("b_avg", -0.3) + ');',
          'tl.to("#pm-d44, #pm-d45", {background: "#d0243a", boxShadow: "0 0 24px rgba(255,59,78,0.8)", scale: 1.25, duration: 0.25}, ' + S.t("b_18") + ');',
          'tl.to("#pm-d45", {clipPath: "inset(0 20% 0 0)", duration: 0.2}, ' + S.t("b_18") + ');',
          'tl.to("#pm-grid .dot:not(#pm-d44):not(#pm-d45)", {background: "#ffffff", opacity: 0.8, duration: 0.3, stagger: {each: 0.004, from: "center", grid: [10, 10]}}, ' + S.t("b_room", -0.3) + ');',
          pop("#pm-room", S.t("b_room"), 0.3))
    return S


def s_call():
    S = Section("call")
    b = S.g
    S.title(S.start, "Doing ₹5L+ A Month?", "You’re In The *Right Place*", "ul")
    S.title(b("b_booked"), "Before Our Call,", "Here’s *What Happens*", "red")
    S.group("cl-g1", S.start, b("b_booked"), f"""
      <div class="card stat" id="cl-rev" style="left:190px; top:40px; width:700px; height:330px; text-align:center">
        <span class="label">Your monthly sales</span><span class="big" id="cl-5l" style="font-size:150px">₹0L+</span></div>
      <div class="row" style="top:450px"><div class="chip" id="cl-traffic">{icon("people")} Same traffic</div>
        <span class="big muted" style="font-size:60px">→</span>
        <div class="chip redc" id="cl-sales">{icon("up")} More sales</div></div>""")
    S.add(enter("#cl-rev", S.t("b_5l", -0.2)), count("#cl-5l", S.t("b_5l", -0.2), 0.6, 0, 5, '"₹" + Math.round(p.v) + "L+"'),
          'tl.fromTo("#cl-rev", {borderColor: "rgba(255,255,255,0.1)"}, {borderColor: "rgba(208,36,58,1)", duration: 0.3}, ' + S.t("b_more") + ');',
          pop("#cl-traffic", S.t("b_traffic")), pop("#cl-sales", S.t("b_traffic", 0.4)))
    steps = [("cal", "Call booked", "You’re all set", "b_booked"),
             ("search", "We audit your store", "On a phone, like your customer", "b_store"),
             ("down", "Where you’re losing sales", "Shown on the call", "b_losing"),
             ("bolt", "How we’d fix it", "Product page, cart, checkout", "b_fix")]
    rows = "".join(f'<div class="card" id="cl-s{i}" style="left:90px; top:{20 + i * 175}px; width:900px; height:150px;'
                   f' display:flex; align-items:center; gap:30px; padding:0 36px">'
                   f'<span class="num">{i + 1 if i else "✓"}</span>{icon(ic, 72)}'
                   f'<div><div class="big" style="font-size:44px; letter-spacing:-0.02em">{t}</div>'
                   f'<div class="label" style="font-size:22px; margin-top:10px; text-transform:none; letter-spacing:0">{sub}</div></div></div>'
                   for i, (ic, t, sub, _) in enumerate(steps))
    S.group("cl-g2", b("b_booked"), b("b_work"), rows)
    for i, (_, _, _, beat) in enumerate(steps):
        S.add(enter(f"#cl-s{i}", S.t(beat, -0.15)))
    S.add('tl.fromTo("#cl-s0 .num", {scale: 1}, {scale: 1.2, duration: 0.15, yoyo: true, repeat: 1}, ' + S.t("b_booked", 0.2) + ');')
    S.group("cl-g3", b("b_work"), None, f"""
      <div class="row" style="top:40px"><div class="chip" id="cl-w1">{icon("page")} Product pages</div></div>
      <div class="row" style="top:150px"><div class="chip" id="cl-w2">{icon("cart")} Carts</div>
        <div class="chip" id="cl-w3">{icon("card")} Checkouts</div></div>
      <svg width="700" height="380" style="position:absolute; left:190px; top:300px; overflow:visible">
        <path id="cl-grow" d="M0 360 C180 340, 300 280, 420 190 S 620 30, 700 10" stroke="#d0243a" stroke-width="12"
          fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" class="glow" stroke-linecap="round"/></svg>
      <div class="chip redc" id="cl-conf" style="left:560px; top:250px">Confident growth</div>""")
    S.add(pop("#cl-w1", S.t("b_work", -0.1)), pop("#cl-w2", S.t("b_work", 0.3)), pop("#cl-w3", S.t("b_work", 0.6)),
          draw("#cl-grow", S.t("b_conf", -0.3), 1.0), pop("#cl-conf", S.t("b_conf", 0.5)))
    return S


def s_prep():
    S = Section("prep")
    b = S.g
    S.title(S.start, "Before The Call, Keep", "These *3 Numbers* Ready", "hl")
    cards = [("eye", "Sessions", "b_sess"), ("pct", "Conversion rate", "b_cr"), ("bag", "Avg. order value", "b_aov")]
    rows = "".join(f'<div class="card" id="pr-c{i}" style="left:90px; top:{150 + i * 170}px; width:900px; height:140px;'
                   f' display:flex; align-items:center; gap:30px; padding:0 36px">'
                   f'<span class="num">{i + 1}</span>{icon(ic, 72)}'
                   f'<span class="big" style="font-size:52px; letter-spacing:-0.02em">{t}</span>'
                   f'<span class="big muted" style="font-size:52px; margin-left:auto">—</span></div>'
                   for i, (ic, t, _) in enumerate(cards))
    S.group("pr-g1", S.start, b("b_see"), f"""
      <div class="row" style="top:10px"><div class="chip" id="pr-shop">{icon("bag")} Shopify</div>
        <div class="chip redc" id="pr-30">Last 30 days</div></div>
      {rows}
      <div class="row" style="top:690px"><div class="chip" id="pr-grow">{icon("up")} We’ll show you how to grow</div></div>""")
    S.add(pop("#pr-shop", S.t("b_shopify")), pop("#pr-30", S.t("b_30", -0.2)),
          *[enter(f"#pr-c{i}", S.t(beat, -0.1)) for i, (_, _, beat) in enumerate(cards)],
          pop("#pr-grow", S.t("b_grow", -0.2)))
    S.group("pr-g2", b("b_see"), None, f"""
      <div class="row" style="top:170px">
        <svg width="260" height="260" viewBox="0 0 64 64" class="icon glow" id="pr-cal">{ICONS["cal"]}</svg></div>
      <div class="row" style="top:470px"><span class="big" id="pr-see" style="font-size:96px">See you on the call.</span></div>""")
    S.add(pop("#pr-cal", S.t("b_see"), 0.35), enter_up("#pr-see", S.t("b_see", 0.1)))
    return S


BUILDERS = [s_hook, s_case, s_problem, s_about, s_proof, s_promise, s_call, s_prep]


def stage_file(S):
    titles, body = S.html()
    sid = S.sid
    script = "\n        ".join(S.js)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>
        #{sid}-root {{ position: absolute; inset: 0; {PALETTE} }}
        #{sid}-root * {{ box-sizing: border-box; margin: 0; }}
        {FONTS}
        {SHARED_CSS}
      </style>
      <div id="{sid}-root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
        {titles}
        <div class="stage"><div class="cam" id="{sid}-cam">
        {body}
        </div></div>
        <div id="{sid}-sweep" style="position:absolute; left:0; top:0; width:420px; height:1250px; pointer-events:none;
             background: linear-gradient(90deg, transparent, rgba(208,36,58,0.5), rgba(255,255,255,0.3), transparent);
             transform: skewX(-18deg); opacity: 0"></div>
      </div>
      <script>
        (() => {{
        const L = (g) => g - {S.start:.3f};
        const tl = gsap.timeline({{ paused: true }});
        tl.fromTo("#{sid}-sweep", {{x: -700, opacity: 1}}, {{x: 1400, opacity: 1, duration: 0.45, ease: "power2.inOut"}}, 0);
        tl.set("#{sid}-sweep", {{opacity: 0}}, 0.46);
        tl.fromTo("#{sid}-cam", {{scale: 1}}, {{scale: 1.03, duration: {S.end - S.start:.3f}, ease: "none"}}, 0);
        {script}
        {hide_js(S.start, S.end, f"#{sid}-root", "L")}
        window.__timelines = window.__timelines || {{}};
        window.__timelines["{sid}"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""


# ---------------------------------------------------------------------------
# FULL inserts: full-screen punch cards. Text per insert, in order of FULL.

PUNCH = [
    ("Let Me", "Show You"),
    ("+₹20 Lakh", "In One Month"),
    ("Not", "Buying"),
    ("After", "The Click"),
    ("Their Whole", "Website"),
    ("Imagine", "30 Days"),
    ("You’re In The", "Right Place"),
    ("Beyond Your", "Wildest Dreams"),
]


def full_file():
    assert len(PUNCH) == len(FULL), (len(PUNCH), len(FULL))
    cards, js = [], []
    for i, ((a, b), (l1, l2)) in enumerate(zip(FULL, PUNCH)):
        l2h = f'<span class="serif red">{esc(l2)}</span>'
        cards.append(f'<div class="pc" id="pc{i}"><div class="pin" id="pc{i}-in">'
                     f'<div class="p1"><span class="pw">{esc(l1)}</span></div>'
                     f'<div class="p2"><span class="pw">{l2h}</span></div></div></div>')
        js += [f'tl.set("#pc{i}", {{autoAlpha: 1}}, {a:.3f});',
               f'tl.set("#pc{i}", {{autoAlpha: 0}}, {b:.3f});',
               f'tl.fromTo("#pc{i} .pw", {{autoAlpha: 0, y: 24, filter: "blur(14px)"}}, {{autoAlpha: 1, y: 0, filter: "blur(0px)",'
               f' duration: 0.25, ease: "power3.out", stagger: 0.12}}, {a:.3f});',
               # jump-cut feel: hard punch-in halfway through longer inserts
               ]
        if b - a > 2.5:
            m = (a + b) / 2
            js.append(f'tl.fromTo("#pc{i}-in", {{scale: 1}}, {{scale: 1.03, duration: {m - a:.3f}, ease: "none"}}, {a:.3f});'
                      f' tl.fromTo("#pc{i}-in", {{scale: 1.13}}, {{scale: 1.16, duration: {b - m - 0.01:.3f}, ease: "none", immediateRender: false}}, {m + 0.01:.3f});')
        else:
            js.append(f'tl.fromTo("#pc{i}-in", {{scale: 1}}, {{scale: 1.04, duration: {b - a:.3f}, ease: "none"}}, {a:.3f});')
        if i == 1:
            js.append(count("#pc1 .p1 .pw", a, 0.9, 0, 20, '"+₹" + Math.round(p.v) + " Lakh"'))
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>
        #full-root {{ position: absolute; inset: 0; pointer-events: none; {PALETTE} }}
        {FONTS}
        #full-root .pc {{ position: absolute; inset: 0; visibility: hidden; opacity: 0;
          background: radial-gradient(ellipse at 50% 40%, rgba(208, 36, 58, 0.34), transparent 60%),
            radial-gradient(circle, var(--dot) 1.2px, transparent 1.6px) 0 0 / 24px 24px, #0b0b0c; }}
        #full-root .pin {{ position: absolute; left: 0; right: 0; top: 480px; text-align: center; transform-origin: 50% 40%; }}
        #full-root .pw {{ display: inline-block; }}
        #full-root .p1 {{ font-family: Inter, sans-serif; font-weight: 900; font-size: 128px; letter-spacing: -0.045em;
          color: #fff; line-height: 1.15; text-shadow: 0 0 40px rgba(255,255,255,0.18); }}
        #full-root .p2 {{ font-family: "Instrument Serif", serif; font-style: italic; font-size: 160px; line-height: 1.1; margin-top: 18px;
          color: var(--accent); text-shadow: 0 0 60px rgba(255, 59, 78, 0.55); }}
        #full-root .serif {{ font-family: "Instrument Serif", serif; }}
        #full-root .red {{ color: #ff3b4e; }}
      </style>
      <div id="full-root" data-composition-id="full" data-width="{W}" data-height="{H}">
        {chr(10).join("        " + c for c in cards).strip()}
      </div>
      <script>
        (() => {{
        const tl = gsap.timeline({{ paused: true }});
        {chr(10).join("        " + j for j in js).strip()}
        window.__timelines = window.__timelines || {{}};
        window.__timelines["full"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""


def hide_js(a, b, sel, local):
    """Hide a layer while a FULL insert covers it (hard cut both ways)."""
    out = []
    for x, y in full_ranges(a, b):
        tx = f"L({x:.3f})" if local else f"{x:.3f}"
        ty = f"L({y:.3f})" if local else f"{y:.3f}"
        out.append(f'tl.set("{sel} > *", {{opacity: 0}}, {tx}); tl.set("{sel} > *", {{opacity: 1}}, {ty});')
    return " ".join(out)


def in_full(t):
    return any(a - 1e-3 <= t < b - 1e-3 for a, b in FULL)


def captions_file():
    spans, js = [], []
    words = TM["words"]
    for i, w in enumerate(words):
        y = 1160 if in_full(w["start"]) else 1240
        nxt = words[i + 1]["start"] if i + 1 < len(words) else D
        # hold through short pauses; clear on sentence gaps longer than 0.35s
        end = nxt if nxt - w["end"] < 0.35 else w["end"] + 0.15
        spans.append(f'<div class="cw" id="cw{i}" style="top:{y - 45}px">{esc(w["text"])}</div>')
        js.append(f'tl.set("#cw{i}", {{autoAlpha: 1}}, {w["start"]:.3f});'
                  f' tl.fromTo("#cw{i}", {{scale: 0.95}}, {{scale: 1, duration: 0.08, ease: "power1.out"}}, {w["start"]:.3f});'
                  f' tl.set("#cw{i}", {{autoAlpha: 0}}, {min(end, D):.3f});')
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>
        #captions-root {{ position: absolute; inset: 0; pointer-events: none; }}
        #captions-root .cw {{ position: absolute; left: 0; width: {W}px; height: 90px; text-align: center;
          font-family: Inter, sans-serif; font-weight: 900; font-size: 72px; line-height: 90px;
          letter-spacing: -0.015em; color: #ffffff; text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
          visibility: hidden; opacity: 0; }}
      </style>
      <div id="captions-root" data-composition-id="captions" data-width="{W}" data-height="{H}">
        {chr(10).join("        " + s for s in spans).strip()}
      </div>
      <script>
        (() => {{
        const tl = gsap.timeline({{ paused: true }});
        {chr(10).join("        " + j for j in js).strip()}
        window.__timelines = window.__timelines || {{}};
        window.__timelines["captions"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""


# ---------------------------------------------------------------------------
# Voice card: where the face-cam card sits in the Kallaway layout.

NBARS = 41


def voice_file():
    env = TM["envelope"]
    bars = "".join(f'<i class="vb" id="vb{i}" style="left:{i * 20}px"></i>' for i in range(NBARS))
    ticks = "".join(f'<i class="vt" style="left:{s["start"] / D * 820:.1f}px"></i>' for s in TM["sections"][1:])
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>
        #voice-root {{ position: absolute; inset: 0; pointer-events: none; {PALETTE} }}
        #voice-root .vc {{ position: absolute; left: 65px; top: 1400px; width: 950px; height: 560px; border-radius: 36px;
          background: linear-gradient(180deg, #19191b, #121213); border: 1px solid rgba(255,255,255,0.1);
          box-shadow: 0 30px 80px rgba(0,0,0,0.7); overflow: hidden; }}
        #voice-root .av {{ position: absolute; left: 50px; top: 44px; width: 96px; height: 96px; border-radius: 50%;
          background: var(--accent); display: flex; align-items: center; justify-content: center;
          font-family: Inter, sans-serif; font-weight: 900; font-size: 40px; color: #fff; letter-spacing: -0.03em; }}
        #voice-root .ring {{ position: absolute; left: 42px; top: 36px; width: 112px; height: 112px; border-radius: 50%;
          border: 3px solid rgba(255, 59, 78, 0.7); }}
        #voice-root .nm {{ position: absolute; left: 176px; top: 50px; font-family: Inter, sans-serif; font-weight: 900;
          font-size: 42px; color: #fff; letter-spacing: -0.02em; }}
        #voice-root .sb {{ position: absolute; left: 176px; top: 104px; font-family: Inter, sans-serif; font-weight: 700;
          font-size: 26px; color: var(--muted); }}
        #voice-root .rec {{ position: absolute; right: 50px; top: 64px; display: flex; align-items: center; gap: 12px;
          font-family: Inter, sans-serif; font-weight: 800; font-size: 24px; color: var(--muted); letter-spacing: 0.08em; }}
        #voice-root .rec b {{ width: 16px; height: 16px; border-radius: 50%; background: var(--accent); display: block; }}
        #voice-root .wave {{ position: absolute; left: 65px; top: 190px; width: 820px; height: 200px; }}
        #voice-root .vb {{ position: absolute; top: 0; width: 10px; height: 200px; border-radius: 5px; background: #fff;
          transform-origin: 50% 50%; transform: scaleY(0.04); }}
        #voice-root .prog {{ position: absolute; left: 65px; top: 440px; width: 820px; height: 6px; border-radius: 3px;
          background: #2a2a2e; }}
        #voice-root .pf {{ position: absolute; left: 0; top: 0; height: 6px; width: 820px; border-radius: 3px;
          background: var(--accent); transform-origin: 0 50%; transform: scaleX(0); }}
        #voice-root .vt {{ position: absolute; top: -5px; width: 4px; height: 16px; margin-left: -2px; border-radius: 2px;
          background: #55555a; }}
      </style>
      <div id="voice-root" data-composition-id="voice" data-width="{W}" data-height="{H}">
        <div class="vc" id="vcard" data-layout-allow-overflow="true">
          <div class="ring" id="vring"></div>
          <div class="av">SL</div>
          <div class="nm">Softwarelance</div>
          <div class="sb">Conversion rate optimisation for D2C</div>
          <div class="rec"><b id="vdot"></b>PRE-CALL BRIEF</div>
          <div class="wave">{bars}</div>
          <div class="prog">{ticks}<i class="pf" id="vprog"></i></div>
        </div>
      </div>
      <script>
        (() => {{
        const ENV = {json.dumps(env)};
        const N = {NBARS}, RATE = 25;
        const bars = Array.from({{length: N}}, (_, i) => document.getElementById("vb" + i));
        const tl = gsap.timeline({{ paused: true }});
        const p = {{t: 0}};
        // Bars ripple out from the centre: bar i shows the loudness a few frames earlier.
        const paint = () => {{
          for (let i = 0; i < N; i++) {{
            const d = Math.abs(i - (N - 1) / 2);
            const k = Math.floor((p.t - d * 0.012) * RATE);
            const e = k >= 0 && k < ENV.length ? ENV[k] : 0;
            const shape = 1 - (d / N) * 0.9;
            const v = Math.max(0.04, e * shape);
            bars[i].style.transform = "scaleY(" + v.toFixed(3) + ")";
            bars[i].style.background = v > 0.55 ? "#ff3b4e" : "#ffffff";
          }}
        }};
        tl.fromTo(p, {{t: 0}}, {{t: {D:.3f}, duration: {D:.3f}, ease: "none", onUpdate: paint}}, 0);
        tl.fromTo("#vprog", {{scaleX: 0}}, {{scaleX: 1, duration: {D:.3f}, ease: "none"}}, 0);
        tl.fromTo("#vring", {{scale: 1, opacity: 0.9}}, {{scale: 1.35, opacity: 0, duration: 1.2, ease: "power1.out", repeat: {int(D / 1.2)}}}, 0);
        tl.fromTo("#vdot", {{opacity: 1}}, {{opacity: 0.2, duration: 0.6, yoyo: true, repeat: {int(D / 0.6)}, ease: "sine.inOut"}}, 0);
        tl.fromTo("#vcard", {{y: 200, autoAlpha: 0}}, {{y: 0, autoAlpha: 1, duration: 0.4, ease: "power3.out"}}, 0);
        {hide_js(0, D, "#voice-root", None)}
        window.__timelines = window.__timelines || {{}};
        window.__timelines["voice"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""


def index_file(sections):
    def clip(cid, a, b, track, extra=""):
        return (f'      <div id="{cid}-host" class="clip" data-composition-id="{cid}"'
                f' data-composition-src="compositions/{cid}.html" data-start="{a:.3f}"'
                f' data-duration="{b - a:.3f}" data-track-index="{track}" data-width="{W}" data-height="{H}"{extra}></div>')
    stages = "\n".join(clip(S.sid, S.start, S.end, 1) for S in sections)
    # whoosh on every cut into and out of a FULL insert
    sfx = []
    for i, (a, b) in enumerate(FULL):
        for j, t in enumerate((a, b)):
            if t < D - 0.5:
                sfx.append(f'      <audio id="sfx{i}{j}" src="assets/sfx/whoosh.wav" data-start="{max(t - 0.12, 0):.3f}"'
                           f' data-duration="0.45" data-track-index="{6 + j}" data-volume="0.35"></audio>')
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0b0b0c; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; {PALETTE}
        background: radial-gradient(circle, var(--dot) 1.2px, transparent 1.6px) 0 0 / 24px 24px, var(--bg); }}
      #bgglow {{ position: absolute; left: -300px; top: 100px; width: 1100px; height: 1100px; z-index: 0;
        background: radial-gradient(circle, rgba(208, 36, 58, 0.16), transparent 65%); pointer-events: none; }}
      #vignette {{ position: absolute; inset: 0; pointer-events: none; z-index: 1;
        background: radial-gradient(ellipse at 50% 40%, transparent 55%, rgba(0, 0, 0, 0.65) 100%); }}
      #root > .clip {{ z-index: 2; }}
      #root > #voice-host {{ z-index: 3; }}
      #root > #full-host {{ z-index: 4; }}
      #root > #captions-host {{ z-index: 5; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}"
         data-width="{W}" data-height="{H}">
      <div id="bgglow"></div>
      <div id="vignette"></div>
{stages}
{clip("voice", 0, D, 2)}
{clip("full", 0, D, 3)}
{clip("captions", 0, D, 4, ' data-track-kind="captions"')}
      <audio id="vo" src="assets/vo.wav" data-start="0" data-duration="{D:.3f}" data-track-index="5" data-volume="1"></audio>
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#bgglow", {{x: 0, y: 0}}, {{x: 500, y: 300, duration: {D / 6:.3f}, ease: "sine.inOut", yoyo: true, repeat: 5}}, 0);
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    comps = ROOT / "compositions"
    comps.mkdir(exist_ok=True)
    sections = [f() for f in BUILDERS]
    for S in sections:
        (comps / f"{S.sid}.html").write_text(stage_file(S))
    (comps / "full.html").write_text(full_file())
    (comps / "captions.html").write_text(captions_file())
    (comps / "voice.html").write_text(voice_file())
    (ROOT / "index.html").write_text(index_file(sections))
    print(f"built {len(sections)} stages + full/captions/voice, {len(TM['words'])} words, {D:.2f}s")
