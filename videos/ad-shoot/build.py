"""Generate the ad's HyperFrames compositions from work/edl.json.

Layout follows the Kallaway style spec: dark dot-grid background, a section
title and a motion-graphics stage in the top 70%, a rounded face-cam card at the
bottom (SPLIT), hard cuts to a full-screen face (FULL), and one caption word at
a time. Stage beats are keyed to the spoken words' times on the edited cut.

    python3 build.py && npx hyperframes check .
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
EDL = json.loads((ROOT / "work" / "edl.json").read_text())
D = EDL["duration"]
W, H = 1080, 1920

# FULL-screen face inserts (global seconds). Everything else is SPLIT.
FULL = [(6.20, 7.667), (14.50, 16.20), (27.45, 29.44), (42.75, 44.633),
        (49.10, 50.70), (61.55, 63.80), (73.00, 74.80)]

# Face card geometry (SPLIT) and the source-frame offset that keeps head and
# shoulders in the card.
CARD = dict(left=65, top=1290, width=950, height=680)
CARD_INNER = dict(left=0, top=-110, width=950, height=round(950 * 1920 / 1080))
PUNCH = 1.12

SECTIONS = [  # id, start, end
    ("hook", 0.0, 7.667),
    ("problem", 7.667, 31.767),
    ("shark", 31.767, 44.633),
    ("proof", 44.633, 69.267),
    ("close", 69.267, D),
]

PALETTE = """
  --bg: #0b0b0c;
  --card: #1a1a1c;
  --card-edge: rgba(255, 255, 255, 0.1);
  --ink: #ffffff;
  --muted: #a0a0a6;
  --accent: #d0243a;
  --glow: rgba(255, 59, 78, 0.5);
  --dot: rgba(255, 255, 255, 0.07);
"""

# Shared component styles, injected into every stage composition.
SHARED_CSS = """
@font-face { font-family: "Instrument Serif"; font-style: italic; font-weight: 400;
  src: url("assets/fonts/InstrumentSerif-Italic.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+2000-206F, U+2191, U+2193, U+2212; }
@font-face { font-family: "Instrument Serif"; font-style: italic; font-weight: 400;
  src: url("assets/fonts/InstrumentSerif-Italic-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+20A0-20C0, U+2113; }
.title { position: absolute; top: 150px; left: 60px; right: 60px; text-align: center;
  font-family: Inter, sans-serif; color: var(--ink); line-height: 1.08;
  text-shadow: 0 0 20px rgba(255,255,255,0.25); }
.title .l1 { display: block; font-size: 58px; font-weight: 800; letter-spacing: -0.02em; }
.title .l2 { display: block; font-size: 60px; font-weight: 800; letter-spacing: -0.02em; margin-top: 6px; }
.title .tw { display: inline-block; }
.serif { font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400;
  font-size: 1.22em; letter-spacing: 0; }
.accent { color: var(--accent); }
.ul { position: relative; display: inline-block; }
.ul::after { content: ""; position: absolute; left: 2%; right: 2%; bottom: -2px; height: 5px;
  background: var(--accent); border-radius: 3px; transform: scaleX(var(--u, 0));
  transform-origin: left center; }
.hl { background: var(--accent); color: #fff; padding: 0 14px 4px; border-radius: 10px;
  text-shadow: none; }
.stage { position: absolute; left: 0; top: 330px; width: 1080px; height: 860px; }
.cam { position: absolute; inset: 0; transform-origin: 50% 50%; }
.card { position: absolute; background: var(--card); border: 1px solid var(--card-edge);
  border-radius: 24px; box-shadow: 0 24px 60px rgba(0,0,0,0.55); color: var(--ink);
  font-family: Inter, sans-serif; }
.chip { position: absolute; display: inline-flex; align-items: center; gap: 14px;
  padding: 16px 28px; border-radius: 999px; background: var(--card);
  border: 1px solid var(--card-edge); color: var(--ink); font-family: Inter, sans-serif;
  font-weight: 800; font-size: 36px; letter-spacing: -0.01em; white-space: nowrap;
  box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.chip.red { background: var(--accent); border-color: transparent; }
.label { font-family: Inter, sans-serif; font-weight: 700; font-size: 30px; color: var(--muted);
  letter-spacing: 0.08em; text-transform: uppercase; }
.big { font-family: Inter, sans-serif; font-weight: 900; color: var(--ink);
  letter-spacing: -0.04em; line-height: 1; }
.glow { filter: drop-shadow(0 0 28px var(--glow)); }
.center-x { left: 50%; transform: translateX(-50%); }
.strike { position: absolute; left: -4%; top: 50%; height: 6px; width: 108%;
  background: var(--accent); border-radius: 3px; transform-origin: left center; }
.tick { color: var(--accent); font-weight: 900; }
.browser { width: 620px; height: 440px; }
.browser .bar { height: 54px; border-bottom: 1px solid var(--card-edge); display: flex;
  align-items: center; gap: 12px; padding: 0 22px; }
.browser .bar i { width: 14px; height: 14px; border-radius: 50%; background: #3a3a3e; }
.browser .hero { margin: 26px; height: 170px; border-radius: 16px;
  background: linear-gradient(135deg, #2a2a2e, #1f1f22); }
.browser .row { margin: 0 26px 16px; height: 22px; border-radius: 11px; background: #2a2a2e; }
.browser .btn { margin: 22px 26px; width: 200px; height: 52px; border-radius: 14px;
  background: var(--accent); }
"""


def L(g):
    """Global seconds -> JS expression for section-local time."""
    return f"L({g})"


def T(at):
    return at if isinstance(at, str) else f"{at:.3f}"


def esc(s):
    return html.escape(s, quote=False)


def title_html(tid, l1, l2):
    """Two-line title. In l2, *word* marks the serif accent; the accent style is
    set per title via the class on the accent span (ul / hl / accent)."""
    def words(s):
        out = []
        for part in s.split(" "):
            out.append(f'<span class="tw">{part}</span>')
        return " ".join(out)
    return (f'<div class="title" id="{tid}"><span class="l1">{words(l1)}</span>'
            f'<span class="l2">{l2}</span></div>')


def title_in(tid, at):
    return (f'tl.fromTo("#{tid} .tw, #{tid} .l2 > span", {{autoAlpha: 0, y: 10, filter: "blur(12px)"}},'
            f' {{autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.27, ease: "power2.out", stagger: 0.066}}, {T(at)});')


def enter(sel, at, dur=0.3, extra=""):
    return (f'tl.fromTo("{sel}", {{autoAlpha: 0, scale: 0.9, filter: "blur(10px)"}},'
            f' {{autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: {dur}, ease: "power3.out"{extra}}}, {T(at)});')


def leave(sel, at, dur=0.2):
    return (f'tl.to("{sel}", {{autoAlpha: 0, filter: "blur(10px)", scale: 0.96,'
            f' duration: {dur}, ease: "power2.in"}}, {T(at)});')


def count(sel, at, dur, frm, to, fmt):
    """Seek-safe count-up: tween a proxy and write the formatted value."""
    return (f'(() => {{ const el = document.querySelector("{sel}"); const p = {{v: {frm}}};'
            f' tl.to(p, {{v: {to}, duration: {dur}, ease: "power2.out",'
            f' onUpdate: () => {{ el.textContent = {fmt}; }} }}, {T(at)}); }})();')


# ---------------------------------------------------------------------------
# Stage compositions. Times in `beats` are GLOBAL seconds; L() converts them to
# section-local time inside each composition's script.

def section_hook(S):
    title = title_html("hook-title", "The Funnel That Got You To ₹5L",
                       '<span class="tw">Won’t</span> <span class="tw">Get</span> <span class="tw">You</span>'
                       ' <span class="tw">To</span> <span class="serif ul" id="hook-ul">₹20 Lakhs</span>')
    body = f"""
{title}
<div class="stage"><div class="cam" id="hook-cam">
  <div class="chip center-x" id="hook-chip" style="top: 40px">D2C Brand Owners</div>
  <div id="hook-ceiling" style="position:absolute; left:90px; right:90px; top:170px; height:0;
      border-top: 6px dashed var(--accent);">
    <div class="chip red" style="right:0; top:-40px; font-size:32px; padding:10px 22px">₹20L / month</div>
  </div>
  <svg id="hook-funnel" class="glow" width="560" height="440" viewBox="0 0 560 440"
       style="position:absolute; left:260px; top:230px; overflow:visible">
    <path id="hook-funnel-path" d="M20 20 H540 L340 250 V410 H220 V250 Z" fill="rgba(208,36,58,0.12)"
      stroke="#ffffff" stroke-width="10" stroke-linejoin="round" pathLength="1"
      stroke-dasharray="1" stroke-dashoffset="1"/>
  </svg>
  <div class="card" id="hook-bag1" style="left:230px; top:170px; width:130px; height:130px"></div>
  <div class="card" id="hook-bag2" style="left:475px; top:140px; width:130px; height:130px"></div>
  <div class="card" id="hook-bag3" style="left:720px; top:170px; width:130px; height:130px"></div>
  <div id="hook-rev" style="position:absolute; left:0; right:0; top:690px; text-align:center">
    <span class="big" id="hook-rev-num" style="font-size:150px">₹0L</span>
    <span class="label" style="font-size:36px">&nbsp;/ month</span>
  </div>
</div></div>"""
    bag = ('<svg width="130" height="130" viewBox="0 0 130 130"><path d="M38 50 h54 l6 52 h-66 z" '
           'fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round"/><path d="M50 50 v-8 '
           'a15 15 0 0 1 30 0 v8" fill="none" stroke="#d0243a" stroke-width="7"/></svg>')
    for i in (1, 2, 3):
        body = body.replace(f'height:130px"></div>', f'height:130px">{bag}</div>', 1)
    js = [
        title_in("hook-title", 0.0),
        'tl.fromTo("#hook-ul", {"--u": 0}, {"--u": 1, duration: 0.5, ease: "power2.inOut"}, L(5.75));',
        'tl.fromTo("#hook-cam", {scale: 1}, {scale: 1.04, duration: L(7.667), ease: "none"}, 0);',
        enter("#hook-chip", 0.07),
        enter("#hook-bag1, #hook-bag2, #hook-bag3", 0.6, 0.35, ', stagger: 0.12'),
        'tl.fromTo(["#hook-bag1", "#hook-bag3"], {y: 0}, {y: -14, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 1}, 0.95);',
        'tl.fromTo("#hook-funnel-path", {strokeDashoffset: 1}, {strokeDashoffset: 0, duration: 0.55, ease: "power2.inOut"}, L(1.83));',
        'tl.fromTo("#hook-funnel", {autoAlpha: 0}, {autoAlpha: 1, duration: 0.1}, L(1.80));',
        'tl.to("#hook-bag1", {x: 200, y: 250, scale: 0.35, autoAlpha: 0, duration: 0.45, ease: "power2.in"}, L(2.25));',
        'tl.to("#hook-bag2", {y: 250, scale: 0.35, autoAlpha: 0, duration: 0.45, ease: "power2.in"}, L(2.35));',
        'tl.to("#hook-bag3", {x: -200, y: 250, scale: 0.35, autoAlpha: 0, duration: 0.45, ease: "power2.in"}, L(2.45));',
        enter("#hook-rev", L(2.55), 0.25),
        count("#hook-rev-num", L(2.63), 0.6, 0, 5, '"₹" + p.v.toFixed(0) + "L"'),
        'tl.fromTo("#hook-funnel-path", {stroke: "#ffffff"}, {stroke: "#d0243a", duration: 0.3}, L(4.07));',
        enter("#hook-ceiling", L(5.55), 0.25),
        'tl.to(["#hook-funnel", "#hook-rev"], {y: -60, duration: 0.18, ease: "power2.out"}, L(5.80));',
        'tl.to(["#hook-funnel", "#hook-rev"], {y: 0, duration: 0.3, ease: "bounce.out"}, L(5.98));',
        'tl.fromTo("#hook-ceiling", {x: 0}, {x: 10, duration: 0.05, yoyo: true, repeat: 5, ease: "sine.inOut"}, L(5.95));',
        leave("#hook-cam", L(6.18), 0.02),  # hidden behind the FULL insert that closes the hook
    ]
    return body, js


def section_problem(S):
    dots = "".join(
        f'<circle class="pb-dot" cx="{150 + (i % 6) * 52}" cy="{60 + (i // 6) * 50}" r="16" fill="#fff"/>'
        for i in range(18))
    body = f"""
{title_html("pb-title", "The Bottleneck Most Brands", '<span class="serif hl">Never See Coming</span>')}
<div class="stage"><div class="cam" id="pb-cam">
  <div id="pb-bottle-g">
    <svg id="pb-bottle" class="glow" width="620" height="620" viewBox="0 0 620 620"
         style="position:absolute; left:230px; top:60px; overflow:visible">
      <path d="M60 20 H560 L360 330 V600 H260 V330 Z" fill="rgba(255,255,255,0.04)" stroke="#fff"
        stroke-width="10" stroke-linejoin="round"/>
      <g id="pb-dots">{dots}</g>
      <circle cx="310" cy="345" r="18" fill="#d0243a"/>
    </svg>
    <div class="chip red center-x" id="pb-chip" style="top:690px">The Bottleneck</div>
    <div id="pb-q" class="big glow" style="position:absolute; left:0; right:0; top:170px; text-align:center;
         font-size:300px; color: var(--accent)">?</div>
  </div>
  <div id="pb-tests">
    <div class="label center-x" id="pb-tests-l" style="position:absolute; top:40px">So you keep testing</div>
    <div class="chip" id="pb-t1" style="left:190px; top:140px; width:700px; justify-content:center">New Creatives</div>
    <div class="chip" id="pb-t2" style="left:190px; top:300px; width:700px; justify-content:center">New Audiences</div>
    <div class="chip red" id="pb-t3" style="left:190px; top:460px; width:700px; justify-content:center">More Ad Spend ↑</div>
  </div>
  <div id="pb-site">
    <div class="card browser" id="pb-browser" style="left:230px; top:40px">
      <div class="bar"><i></i><i></i><i></i></div>
      <div class="hero"></div><div class="row" style="width:70%"></div><div class="row" style="width:50%"></div>
      <div class="btn"></div>
    </div>
    <div class="chip" id="pb-c1" style="left:150px; top:540px"><span class="tick">✓</span> Looks good</div>
    <div class="chip" id="pb-c2" style="left:520px; top:540px"><span class="tick">✓</span> Covers the points</div>
    <div class="center-x" id="pb-quote" style="position:absolute; top:670px; text-align:center; width:900px;
         font-size:54px; color: var(--muted)"><span class="serif">“Changing it won't matter”</span></div>
  </div>
  <div class="card" id="pb-chart" style="left:90px; top:40px; width:900px; height:700px">
    <svg width="900" height="560" viewBox="0 0 900 560" style="position:absolute; left:0; top:40px">
      <line x1="80" y1="500" x2="840" y2="500" stroke="#3a3a3e" stroke-width="3"/>
      <path id="pb-spend" d="M80 470 C 300 440, 520 300, 820 90" fill="none" stroke="#fff"
        stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
      <path id="pb-conv" d="M80 400 L820 400" fill="none" stroke="#d0243a" stroke-width="10"
        stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
    </svg>
    <div class="label" style="position:absolute; left:640px; top:70px; color:#fff">Ad spend</div>
    <div class="label" id="pb-conv-l" style="position:absolute; left:80px; top:600px; color: var(--accent)">
      Conversion: stays the same</div>
  </div>
</div></div>"""
    js = [
        title_in("pb-title", 0.05),
        'tl.fromTo("#pb-cam", {scale: 1}, {scale: 1.03, duration: L(31.767), ease: "none"}, 0);',
        enter("#pb-bottle", L(8.30), 0.3),
        'tl.fromTo(".pb-dot", {y: -260, autoAlpha: 0}, {y: 0, autoAlpha: 1, duration: 0.35, ease: "bounce.out", stagger: 0.05}, L(8.45));',
        enter("#pb-chip", L(9.18), 0.25),
        'tl.to("#pb-bottle", {opacity: 0.35, duration: 0.25}, L(11.50));',
        enter("#pb-q", L(11.50), 0.3),
        'tl.fromTo("#pb-q", {rotation: -8}, {rotation: 8, duration: 0.8, yoyo: true, repeat: 2, ease: "sine.inOut"}, L(11.80));',
        leave("#pb-bottle-g", L(14.45), 0.05),
        enter("#pb-tests-l", L(16.66), 0.25),
        enter("#pb-t1", L(17.30)), enter("#pb-t2", L(18.12)), enter("#pb-t3", L(19.64)),
        'tl.fromTo("#pb-t3", {scale: 1}, {scale: 1.06, duration: 0.2, yoyo: true, repeat: 1}, L(20.28));',
        leave("#pb-tests", L(21.70)),
        enter("#pb-browser", L(21.93), 0.35),
        enter("#pb-c1", L(22.89)), enter("#pb-c2", L(23.95)),
        enter("#pb-quote", L(25.15)),
        leave("#pb-site", L(27.40), 0.05),
        enter("#pb-chart", L(29.44), 0.25),
        'tl.fromTo("#pb-spend", {strokeDashoffset: 1}, {strokeDashoffset: 0, duration: 1.0, ease: "power2.inOut"}, L(29.50));',
        'tl.fromTo("#pb-conv", {strokeDashoffset: 1}, {strokeDashoffset: 0, duration: 1.0, ease: "none"}, L(29.90));',
        enter("#pb-conv-l", L(30.86), 0.25),
    ]
    return body, js


def section_shark(S):
    streams = "".join(
        f'<div class="sk-dot" style="position:absolute; left:{300 + (i * 67) % 480}px; top:{40 + (i * 37) % 160}px;'
        f' width:26px; height:26px; border-radius:50%; background:#fff"></div>' for i in range(14))
    title = title_html("sk-title", "More Traffic",
                       '<span class="serif accent">Doesn’t Mean</span> <span class="tw">More</span>'
                       ' <span class="tw">Revenue</span>')
    body = f"""
{title}
<div class="stage"><div class="cam" id="sk-cam">
  <div id="sk-tv-g">
    <div class="card" id="sk-tv" style="left:140px; top:40px; width:800px; height:470px; overflow:hidden;
         background: repeating-linear-gradient(0deg, #1a1a1c 0 6px, #1e1e21 6px 12px)">
      <div class="label" style="position:absolute; top:70px; left:0; right:0; text-align:center">As featured on</div>
      <div id="sk-name" class="big glow" style="position:absolute; top:160px; left:0; right:0; text-align:center;
           font-size:140px">Shark Tank</div>
    </div>
    <div id="sk-row" style="position:absolute; top:580px; left:0; right:0; display:flex; justify-content:center; gap:22px">
      {"".join(f'<div class="card sk-store" style="position:relative; width:150px; height:150px; display:flex; align-items:center; justify-content:center; font-size:64px"><span class="tick">✓</span></div>' for _ in range(5))}
    </div>
    <div class="label center-x" id="sk-knows" style="position:absolute; top:760px">Every D2C brand knows</div>
  </div>
  <div id="sk-traffic-g">
    {streams}
    <div class="card" id="sk-store" style="left:340px; top:360px; width:400px; height:300px;
         display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px">
      <svg width="140" height="120" viewBox="0 0 140 120"><path d="M10 50 L25 10 H115 L130 50 Z M20 50 V110 H120 V50"
        fill="none" stroke="#fff" stroke-width="8" stroke-linejoin="round"/><rect x="55" y="70" width="30" height="40" fill="#d0243a"/></svg>
      <div class="label" style="color:#fff">Your store</div>
    </div>
    <div class="chip" id="sk-traffic-chip" style="left:90px; top:40px">Traffic ↑</div>
  </div>
  <div id="sk-eq" style="position:absolute; left:0; right:0; top:120px; text-align:center">
    <div class="big" style="font-size:120px">More Traffic</div>
    <div class="big glow" id="sk-neq" style="font-size:200px; color: var(--accent)">≠</div>
    <div class="big" style="font-size:120px">More Revenue</div>
  </div>
</div></div>"""
    js = [
        title_in("sk-title", 0.05),
        'tl.fromTo("#sk-cam", {scale: 1}, {scale: 1.03, duration: L(44.633), ease: "none"}, 0);',
        enter("#sk-tv", L(31.84), 0.35),
        'tl.fromTo("#sk-name", {autoAlpha: 0, scale: 1.3}, {autoAlpha: 1, scale: 1, duration: 0.35, ease: "expo.out"}, L(34.24));',
        enter(".sk-store", L(36.08), 0.3, ', stagger: 0.08'),
        enter("#sk-knows", L(36.80), 0.25),
        leave("#sk-tv-g", L(37.85)),
        enter("#sk-store", L(37.92), 0.3),
        enter("#sk-traffic-chip", L(38.45), 0.25),
        'tl.fromTo(".sk-dot", {autoAlpha: 0, y: -80}, {autoAlpha: 1, y: 0, duration: 0.25, stagger: 0.06}, L(38.10));',
        'tl.to(".sk-dot", {x: (i) => 540 - (300 + (i * 67) % 480) - 13, y: (i) => 480 - (40 + (i * 37) % 160), scale: 0.3, autoAlpha: 0, duration: 0.7, ease: "power2.in", stagger: 0.08}, L(38.70));',
        leave("#sk-traffic-g", L(39.92)),
        enter("#sk-eq", L(40.12), 0.35),
        'tl.fromTo("#sk-neq", {scale: 0.6}, {scale: 1, duration: 0.4, ease: "back.out(2.5)"}, L(41.34));',
    ]
    return body, js


def section_proof(S):
    def stat(i, top, label, init):
        return (f'<div class="card" id="pf-s{i}" style="left:90px; top:{top}px; width:900px; height:210px">'
                f'<div class="label" style="position:absolute; left:44px; top:34px">{label}</div>'
                f'<div class="big" id="pf-v{i}" style="position:absolute; left:44px; top:88px; font-size:96px">{init}</div>'
                f'<div class="big accent" id="pf-a{i}" style="position:absolute; right:48px; top:78px; font-size:96px">↑</div></div>')
    body = f"""
{title_html("pf-title", "No New Ads. No Extra Spend.", '<span class="tw">Just</span> <span class="tw">A</span> <span class="serif ul" id="pf-ul">Better Store</span>')}
<div class="stage"><div class="cam" id="pf-cam">
  <div id="pf-site-g">
    <div class="card browser" id="pf-comp1" style="left:-40px; top:180px; transform: scale(0.7); opacity:0.35"></div>
    <div class="card browser" id="pf-comp2" style="left:500px; top:180px; transform: scale(0.7); opacity:0.35"></div>
    <div class="card browser glow" id="pf-browser" style="left:230px; top:110px">
      <div class="bar"><i></i><i></i><i></i></div>
      <div class="hero"></div><div class="row" style="width:70%"></div><div class="row" style="width:50%"></div>
      <div class="btn"></div>
    </div>
    <div class="chip" id="pf-good" style="left:320px; top:620px"><span class="tick">✓</span> Already a good website</div>
  </div>
  <div id="pf-stats-g">
    {stat(1, 20, "Conversion rate", "2%")}
    {stat(2, 260, "Add to cart → checkout", "5%")}
    <div class="card" id="pf-s3" style="left:90px; top:500px; width:900px; height:330px; border-color: rgba(208,36,58,0.6)">
      <div class="label" style="position:absolute; left:44px; top:34px">Revenue</div>
      <div class="big glow accent" id="pf-v3" style="position:absolute; left:44px; top:112px; font-size:180px">+0%</div>
    </div>
  </div>
  <div id="pf-not-g">
    <div class="chip" id="pf-n1" style="left:150px; top:60px; font-size:44px">Fixing their ads<span class="strike" id="pf-x1"></span></div>
    <div class="chip" id="pf-n2" style="left:430px; top:210px; font-size:44px">More ad spend<span class="strike" id="pf-x2"></span></div>
    <div class="label center-x" id="pf-just" style="position:absolute; top:380px">Just by improving</div>
    <div class="chip red" id="pf-y1" style="left:170px; top:460px; font-size:46px">✓ Visual communication</div>
    <div class="chip red" id="pf-y2" style="left:200px; top:610px; font-size:46px">✓ Conversion strategy</div>
  </div>
</div></div>"""
    js = [
        title_in("pf-title", 0.05),
        'tl.fromTo("#pf-ul", {"--u": 0}, {"--u": 1, duration: 0.5, ease: "power2.inOut"}, 0.6);',
        'tl.fromTo("#pf-cam", {scale: 1}, {scale: 1.03, duration: L(69.267), ease: "none"}, 0);',
        enter("#pf-browser", L(44.70), 0.35),
        enter("#pf-good", L(46.62), 0.3),
        'tl.fromTo(["#pf-comp1", "#pf-comp2"], {autoAlpha: 0, x: 0}, {autoAlpha: 0.35, duration: 0.3, stagger: 0.1}, L(47.39));',
        'tl.to("#pf-browser", {scale: 1.06, duration: 0.4, ease: "power2.out"}, L(47.69));',
        leave("#pf-site-g", L(49.05), 0.05),
        enter("#pf-s1", L(50.77), 0.3),
        count("#pf-v1", L(52.77), 0.55, 2, 3.5, 'p.v.toFixed(1).replace(".0", "") + "%"'),
        'tl.fromTo("#pf-a1", {y: 20, autoAlpha: 0}, {y: 0, autoAlpha: 1, duration: 0.3, ease: "back.out(2)"}, L(52.77));',
        enter("#pf-s2", L(54.12), 0.3),
        count("#pf-v2", L(57.16), 0.55, 5, 15, 'p.v.toFixed(0) + "%"'),
        'tl.fromTo("#pf-a2", {y: 20, autoAlpha: 0}, {y: 0, autoAlpha: 1, duration: 0.3, ease: "back.out(2)"}, L(57.40));',
        enter("#pf-s3", L(58.47), 0.3),
        count("#pf-v3", L(59.06), 1.1, 0, 75, '"+" + p.v.toFixed(0) + "%"'),
        'tl.fromTo("#pf-s3", {scale: 1}, {scale: 1.04, duration: 0.2, yoyo: true, repeat: 1}, L(60.20));',
        leave("#pf-stats-g", L(61.50), 0.05),
        enter("#pf-n1", L(63.80), 0.25),
        'tl.fromTo("#pf-x1", {scaleX: 0}, {scaleX: 1, duration: 0.25, ease: "power2.out"}, L(63.95));',
        enter("#pf-n2", L(64.64), 0.25),
        'tl.fromTo("#pf-x2", {scaleX: 0}, {scaleX: 1, duration: 0.25, ease: "power2.out"}, L(65.10));',
        'tl.to(["#pf-n1", "#pf-n2"], {opacity: 0.45, duration: 0.3}, L(65.57));',
        enter("#pf-just", L(65.57), 0.25),
        enter("#pf-y1", L(66.85), 0.3),
        enter("#pf-y2", L(68.05), 0.3),
    ]
    return body, js


def section_close(S):
    body = f"""
{title_html("cl-title", "Take Your Store", '<span class="tw">To</span> <span class="serif ul" id="cl-ul">Another Level</span>')}
{title_html("cl-title2", "Outperform Your Current Store", '<span class="tw">Or</span> <span class="serif hl">Full Refund</span>')}
<div class="stage"><div class="cam" id="cl-cam">
  <div id="cl-link-g">
    <div class="chip red center-x" id="cl-link" style="top:60px; font-size:64px; padding:26px 56px">Link Below</div>
    <div class="big center-x accent glow" id="cl-arrow" style="position:absolute; top:190px; font-size:150px">↓</div>
    <div id="cl-steps">
      <div class="card cl-step" style="left:180px; top:600px; width:220px; height:120px"></div>
      <div class="card cl-step" style="left:430px; top:490px; width:220px; height:230px"></div>
      <div class="card cl-step" style="left:680px; top:380px; width:220px; height:340px; border-color: rgba(208,36,58,0.7)"></div>
      <div class="chip red" id="cl-lvl" style="left:640px; top:300px; font-size:30px">Next level</div>
    </div>
  </div>
  <div id="cl-guar-g">
    <svg id="cl-shield" class="glow" width="300" height="340" viewBox="0 0 300 340"
         style="position:absolute; left:390px; top:30px; overflow:visible">
      <path d="M150 12 L280 60 V160 C280 250 220 305 150 330 C80 305 20 250 20 160 V60 Z"
        fill="rgba(208,36,58,0.18)" stroke="#d0243a" stroke-width="12" stroke-linejoin="round"/>
      <path id="cl-check" d="M90 170 L135 215 L215 125" fill="none" stroke="#fff" stroke-width="18"
        stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
    </svg>
    <div class="big" id="cl-refund" style="position:absolute; left:0; right:0; top:420px; text-align:center; font-size:120px">100% Refund</div>
    <div id="cl-free" style="position:absolute; left:0; right:0; top:580px; text-align:center; font-family: Inter, sans-serif;
         font-size:52px; font-weight:700; color:#fff">or we <span class="serif accent">work for free</span><br>until it does</div>
  </div>
</div></div>"""
    js = [
        title_in("cl-title", 0.05),
        'tl.fromTo("#cl-ul", {"--u": 0}, {"--u": 1, duration: 0.5, ease: "power2.inOut"}, L(72.26));',
        'tl.fromTo("#cl-cam", {scale: 1}, {scale: 1.03, duration: L(%.3f), ease: "none"}, 0);' % D,
        enter("#cl-link", L(69.34), 0.3),
        enter("#cl-arrow", L(69.94), 0.25),
        'tl.fromTo("#cl-arrow", {y: 0}, {y: 40, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut"}, L(70.20));',
        enter(".cl-step", L(71.14), 0.3, ', stagger: 0.18'),
        enter("#cl-lvl", L(72.26), 0.25),
        leave("#cl-link-g", L(72.95), 0.05),
        leave("#cl-title", L(72.95), 0.05),
        title_in("cl-title2", L(74.80)),
        enter("#cl-shield", L(74.83), 0.35),
        'tl.fromTo("#cl-check", {strokeDashoffset: 1}, {strokeDashoffset: 0, duration: 0.4, ease: "power2.out"}, L(75.30));',
        enter("#cl-refund", L(76.75), 0.3),
        enter("#cl-free", L(78.31), 0.3),
    ]
    return body, js


BUILDERS = {"hook": section_hook, "problem": section_problem, "shark": section_shark,
            "proof": section_proof, "close": section_close}


def stage_file(sid, start, end):
    body, js = BUILDERS[sid](start)
    script = "\n        ".join(js)
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
        {SHARED_CSS}
      </style>
      <div id="{sid}-root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
        {body}
      </div>
      <script>
        (() => {{
        const L = (g) => g - {start:.3f};
        const tl = gsap.timeline({{ paused: true }});
        {script}
        window.__timelines = window.__timelines || {{}};
        window.__timelines["{sid}"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""


def in_full(t):
    return any(a - 1e-3 <= t < b - 1e-3 for a, b in FULL)


def captions_file():
    spans, js = [], []
    for i, w in enumerate(EDL["words"]):
        y = 1160 if in_full(w["start"]) else 1225
        spans.append(f'<div class="cw" id="cw{i}" style="top:{y - 40}px">{esc(w["text"])}</div>')
        js.append(f'tl.set("#cw{i}", {{autoAlpha: 1}}, {w["start"]:.3f});'
                  f' tl.fromTo("#cw{i}", {{scale: 0.95}}, {{scale: 1, duration: 0.08, ease: "power1.out"}}, {w["start"]:.3f});'
                  f' tl.set("#cw{i}", {{autoAlpha: 0}}, {min(w["end"], D):.3f});')
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>
        #captions-root {{ position: absolute; inset: 0; pointer-events: none; }}
        #captions-root .cw {{ position: absolute; left: 0; width: {W}px; height: 80px; text-align: center;
          font-family: Inter, sans-serif; font-weight: 900; font-size: 70px; line-height: 80px;
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


def index_file():
    def px(d):
        return ", ".join(f'{k}: {v}' for k, v in d.items())
    full_card = dict(left=0, top=0, width=W, height=H)
    full_inner = dict(left=0, top=0, width=W, height=H)
    js = [f'tl.set("#face", {{{px(CARD)}, borderRadius: 36}}, 0);',
          f'tl.set("#face-inner", {{{px(CARD_INNER)}}}, 0);']
    for a, b in FULL:
        js.append(f'tl.set("#face", {{{px(full_card)}, borderRadius: 0}}, {a:.3f});')
        js.append(f'tl.set("#face-inner", {{{px(full_inner)}}}, {a:.3f});')
        js.append(f'tl.set("#face", {{{px(CARD)}, borderRadius: 36}}, {b:.3f});')
        js.append(f'tl.set("#face-inner", {{{px(CARD_INNER)}}}, {b:.3f});')
    # Jump-cut punch-ins: alternate framing on every cut, only in FULL mode
    # (the card crop is already tight in SPLIT).
    starts = [p["at"] for p in EDL["pieces"]]
    events = sorted(set(starts + [a for a, _ in FULL] + [b for _, b in FULL]))
    for t in events:
        idx = max(i for i, s0 in enumerate(starts) if s0 <= t + 1e-6)
        scale = PUNCH if (in_full(t) and idx % 2) else 1
        js.append(f'tl.set("#face-zoom", {{scale: {scale}}}, {t:.3f});')
    stages = "\n".join(
        f'      <div id="stage-{sid}" class="clip" data-composition-id="{sid}"'
        f' data-composition-src="compositions/{sid}.html" data-start="{a:.3f}"'
        f' data-duration="{b - a:.3f}" data-track-index="1" data-width="{W}" data-height="{H}"></div>'
        for sid, a, b in SECTIONS)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0b0b0c; }}
      #stage {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; {PALETTE}
        background: radial-gradient(circle, var(--dot) 1.2px, transparent 1.6px) 0 0 / 24px 24px, var(--bg); }}
      #vignette {{ position: absolute; inset: 0; pointer-events: none; z-index: 1;
        background: radial-gradient(ellipse at 50% 40%, transparent 55%, rgba(0, 0, 0, 0.65) 100%); }}
      #stage > .clip {{ z-index: 2; }}
      #face {{ position: absolute; z-index: 3; overflow: hidden; background: #000;
        border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 30px 80px rgba(0, 0, 0, 0.7); }}
      #face-inner {{ position: absolute; }}
      #face-zoom {{ position: absolute; inset: 0; transform-origin: 50% 24%; }}
      #aroll {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      #stage > #captions-host {{ z-index: 4; }}
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="main" data-start="0" data-duration="{D:.3f}"
         data-width="{W}" data-height="{H}">
      <div id="vignette"></div>
{stages}
      <div id="face" data-layout-allow-overflow="true">
        <div id="face-inner" data-layout-allow-overflow="true">
          <div id="face-zoom">
            <video id="aroll" class="clip" src="assets/aroll.mp4" data-start="0" data-duration="{D:.3f}"
                   data-track-index="0" muted playsinline></video>
          </div>
        </div>
      </div>
      <div id="captions-host" class="clip" data-composition-id="captions" data-track-kind="captions"
           data-composition-src="compositions/captions.html" data-start="0" data-duration="{D:.3f}"
           data-track-index="2" data-width="{W}" data-height="{H}"></div>
      <audio id="vo" src="assets/aroll.mp4" data-start="0" data-duration="{D:.3f}"
             data-track-index="3" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).strip()}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    (ROOT / "compositions").mkdir(exist_ok=True)
    for sid, a, b in SECTIONS:
        (ROOT / "compositions" / f"{sid}.html").write_text(stage_file(sid, a, b))
    (ROOT / "compositions" / "captions.html").write_text(captions_file())
    (ROOT / "index.html").write_text(index_file())
    print(f"built {len(SECTIONS)} stage comps, {len(EDL['words'])} caption words, {D:.2f}s")
