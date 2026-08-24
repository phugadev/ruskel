#!/usr/bin/env python3
"""
Ruskel colour tooling.

The palette is not a set of hexes someone picked — it is the output of a
constraint solve, and this is the solver. Keeping it in the repo is what
makes the system extensible: adding a hue means adding an angle and
re-running, not eyedropping something that looks close.

  solve.py ring [--exposure editorial|luminous]
      Print the mark ring for an exposure: per-hue chroma at 95% of that
      hue's own sRGB ceiling, within the exposure's contrast window.

  solve.py separation [--exposure ...]
      Pairwise OKLab dE across the categorical series. This is the number
      that decides how many series the system can carry.

  solve.py bridge
      Check the Tailwind v4 theme bridge against the token file: every
      variable it points at must exist, and no theme key may reference a
      custom property of its own name.

  solve.py verify
      Parse packages/tokens/src/tokens.css, recompute every mark and text
      value, and assert the constraints the system claims to hold. Runs the
      bridge check too. Exit 1 on failure. Run it in CI.
"""
import argparse, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "packages" / "tokens" / "src" / "tokens.css"
BRIDGE = ROOT / "packages" / "tokens" / "src" / "tailwind.css"

# ── colour space ──────────────────────────────────────────────────────────
def _s2l(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def _l2s(c): return 12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4))-0.055

def oklab_to_rgb(L, a, b):
    l_, m_, s_ = L+0.3963377774*a+0.2158037573*b, L-0.1055613458*a-0.0638541728*b, L-0.0894841775*a-1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    return (_l2s( 4.0767416621*l-3.3077115913*m+0.2309699292*s),
            _l2s(-1.2684380046*l+2.6097574011*m-0.3413193965*s),
            _l2s(-0.0041960863*l-0.7034186147*m+1.7076147010*s))

def oklch_to_hex(L, C, H):
    a, b = C*math.cos(math.radians(H)), C*math.sin(math.radians(H))
    r, g, bb = oklab_to_rgb(L, a, b)
    f = lambda x: max(0, min(255, round(x*255)))
    return "#{:02X}{:02X}{:02X}".format(f(r), f(g), f(bb))

def max_chroma(L, H):
    """Largest in-gamut chroma at this lightness and hue."""
    lo, hi = 0.0, 0.45
    for _ in range(48):
        mid = (lo+hi)/2
        a, b = mid*math.cos(math.radians(H)), mid*math.sin(math.radians(H))
        r, g, bb = oklab_to_rgb(L, a, b)
        if min(r, g, bb) < -0.0005 or max(r, g, bb) > 1.0005: hi = mid
        else: lo = mid
    return lo

def relative_luminance(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    return 0.2126*_s2l(r)+0.7152*_s2l(g)+0.0722*_s2l(b)

def contrast(a, b):
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi+0.05)/(lo+0.05)

def oklab(L, C, H):
    return (L, C*math.cos(math.radians(H)), C*math.sin(math.radians(H)))

def delta_e(p, q):
    return math.sqrt(sum((p[i]-q[i])**2 for i in range(3)))

# ── the system's constants ────────────────────────────────────────────────
HUE = {"700": 22.0, "620": 42.0, "590": 88.0, "550": 110.0, "520": 155.6,
       "490": 210.0, "470": 252.3, "440": 275.0, "405": 296.1, "370": 320.0}
BANDS = {"590": "interface", "520": "systems", "470": "compute", "405": "intelligence"}
CATEGORICAL = ["590", "520", "490", "470", "405", "370"]   # the six chart series
FUNCTIONAL = ["620", "700"]

GROUND = {"editorial": "#EDEAE3", "luminous": "#0B0A08"}
WINDOW = {"editorial": (2.2, 7.0), "luminous": (4.5, 9.0)}   # mark contrast window
TEXT_TARGET = {"editorial": 4.6, "luminous": 6.5}            # coloured type floor
# The design floor for categorical separation. The shipped set measures 0.131
# at its worst pair, so the bar sits just under it: the constraint is "no
# closer than this", and stating it as the measured value itself makes the
# test fail on floating-point noise.
MIN_SERIES_DE = 0.130

def solve_mark(H, exposure):
    ground = GROUND[exposure]; lo, hi = WINDOW[exposure]
    best = None; L = 0.25
    while L <= 0.95:
        C = max_chroma(L, H)*0.95
        hx = oklch_to_hex(L, C, H); r = contrast(hx, ground)
        if lo <= r <= hi and (best is None or C > best[1]):
            best = (L, C, hx, r)
        L += 0.005
    return best

# ── commands ──────────────────────────────────────────────────────────────
def cmd_ring(args):
    for exposure in ([args.exposure] if args.exposure else ["editorial", "luminous"]):
        lo, hi = WINDOW[exposure]
        print(f"\n{exposure.upper()}  ground {GROUND[exposure]}  window {lo}-{hi}:1")
        for nm in ["700", "620"] + CATEGORICAL:
            L, C, hx, r = solve_mark(HUE[nm], exposure)
            role = BANDS.get(nm, "functional" if nm in FUNCTIONAL else "categorical")
            print(f"  {nm}nm {role:13} oklch({L:.3f} {C:.3f} {HUE[nm]:5.1f})  {hx}  {r:5.2f}:1")

def cmd_separation(args):
    for exposure in ([args.exposure] if args.exposure else ["editorial", "luminous"]):
        pts = {}
        for nm in CATEGORICAL:
            L, C, hx, _ = solve_mark(HUE[nm], exposure)
            pts[nm] = (oklab(L, C, HUE[nm]), hx)
        print(f"\n{exposure.upper()} — pairwise OKLab dE across the six series")
        print("        " + "".join(f"{n:>8}" for n in CATEGORICAL))
        for a in CATEGORICAL:
            row = "".join(f"{delta_e(pts[a][0], pts[b][0]):8.3f}" if a != b else "       ·" for b in CATEGORICAL)
            print(f"  {a:5} {row}")
        worst = min((delta_e(pts[a][0], pts[b][0]), a, b)
                    for i, a in enumerate(CATEGORICAL) for b in CATEGORICAL[i+1:])
        print(f"  worst pair: {worst[1]}nm / {worst[2]}nm  dE {worst[0]:.3f}  (floor {MIN_SERIES_DE})")

def parse_tokens():
    """Pull the declared oklch() values out of the stylesheet, per exposure."""
    css = TOKENS.read_text()
    out = {}
    for exposure in ("editorial", "luminous"):
        block = re.search(r'\[data-exposure="%s"\]\s*\{(.*?)\n\}' % exposure, css, re.S)
        if not block:
            raise SystemExit(f"could not find the {exposure} block in {TOKENS}")
        found = {}
        for m in re.finditer(r'--rsk-(mark|text)-(\d{3}):\s*oklch\(([\d.]+)\s+([\d.]+)\s+var\(--rsk-h-(\d{3})\)\)', block.group(1)):
            found[(m.group(1), m.group(2))] = (float(m.group(3)), float(m.group(4)), m.group(5))
        out[exposure] = found
    return out

def cmd_bridge(args):
    """The bridge is a second contract, and a rename in tokens.css breaks it silently.

    A Tailwind utility built on a variable that does not exist renders
    nothing at all — no warning at build time, no error in the console, just
    a component that is quietly the wrong colour. So the check is blunt:
    every var() the bridge reaches for must be declared in the token file.

    The second check is the cycle trap. A theme key that references a custom
    property of its own name — `--radius-sm: var(--radius-sm)` — compiles,
    emits, and voids itself at computed-value time. It is invisible in the
    output CSS and fatal at runtime, which is why the radius tokens carry a
    --rsk- source name for the bridge to point at.
    """
    if not BRIDGE.exists():
        raise SystemExit(f"no bridge at {BRIDGE}")
    strip = lambda t: re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    tokens, bridge = strip(TOKENS.read_text()), strip(BRIDGE.read_text())
    # Declarations are not one per line — the scale packs three to a row and
    # [data-band] declares its pair inline — so this cannot be line-anchored.
    declared = set(re.findall(r'(--[\w-]+)\s*:', tokens))
    failures, checks = [], 0

    for key, value in re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', bridge):
        for ref in re.findall(r'var\(\s*(--[\w-]+)', value):
            checks += 1
            if ref == key:
                failures.append(f"{key} references itself — the cycle voids the declaration")
            elif ref not in declared:
                failures.append(f"{key} -> {ref} is not declared in {TOKENS.name}")

    print(f"{checks} bridge references against {TOKENS.relative_to(ROOT)}")
    if failures:
        print("\nFAILED:")
        for f in failures: print(f"  - {f}")
        sys.exit(1)
    print("the bridge resolves")

def cmd_verify(args):
    declared = parse_tokens()
    failures, checks = [], 0

    for exposure, found in declared.items():
        ground = GROUND[exposure]
        lo, hi = WINDOW[exposure]
        for (role, nm), (L, C, href) in sorted(found.items()):
            hx = oklch_to_hex(L, C, HUE[nm]); r = contrast(hx, ground); checks += 1
            if href != nm:
                failures.append(f"{exposure} {role}-{nm} references --rsk-h-{href}")
            if role == "mark":
                if not (lo - 0.01 <= r <= hi + 0.01):
                    failures.append(f"{exposure} mark-{nm} {hx} contrast {r:.2f} outside window {lo}-{hi}")
                ceiling = max_chroma(L, HUE[nm])
                if C > ceiling + 0.002:
                    failures.append(f"{exposure} mark-{nm} chroma {C:.3f} exceeds gamut ceiling {ceiling:.3f}")
            else:
                if r < TEXT_TARGET[exposure] - 0.05:
                    failures.append(f"{exposure} text-{nm} {hx} contrast {r:.2f} below AA target {TEXT_TARGET[exposure]}")

        pts = {}
        for nm in CATEGORICAL:
            if ("mark", nm) in found:
                L, C, _ = found[("mark", nm)]
                pts[nm] = oklab(L, C, HUE[nm])
        keys = list(pts)
        for i, a in enumerate(keys):
            for b in keys[i+1:]:
                checks += 1
                d = delta_e(pts[a], pts[b])
                if d < MIN_SERIES_DE:
                    failures.append(f"{exposure} series {a}nm/{b}nm dE {d:.3f} below floor {MIN_SERIES_DE}")

        for nm_a, nm_b, floor, why in [("590", "620", 0.130, "interface must never be confusable with a warning")]:
            if ("mark", nm_a) in found and ("mark", nm_b) in found:
                checks += 1
                pa = oklab(*found[("mark", nm_a)][:2], HUE[nm_a])
                pb = oklab(*found[("mark", nm_b)][:2], HUE[nm_b])
                d = delta_e(pa, pb)
                if d < floor:
                    failures.append(f"{exposure} {nm_a}nm/{nm_b}nm dE {d:.3f} below {floor} — {why}")

    print(f"{checks} checks against {TOKENS.relative_to(ROOT)}")
    if failures:
        print("\nFAILED:")
        for f in failures: print(f"  - {f}")
        sys.exit(1)
    print("all constraints hold")
    cmd_bridge(args)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("ring", cmd_ring), ("separation", cmd_separation)):
        p = sub.add_parser(name); p.add_argument("--exposure", choices=["editorial", "luminous"]); p.set_defaults(fn=fn)
    sub.add_parser("bridge").set_defaults(fn=cmd_bridge)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    a = ap.parse_args(); a.fn(a)
