#!/usr/bin/env python3
"""
Ruskel role scale — the palette gains depth.

Until now every hue had two values: a mark to be seen and a tint to be read.
That is enough to colour a chip and not enough to build a surface. A real
component wants a wash to sit on, a border around it, a solid for the filled
state, and type that survives on top — four jobs, of the same hue, all
related. Without them the component layer improvises with color-mix, which
works once and does not generalise.

So each hue now carries eight steps, and the step names say what the step is
FOR rather than how light it is:

  bg      bg2      the wash and its hover. Text-bearing; barely off ground.
  line    line2    the hairline and its hover/emphasis.
  solid   solid2   the mark and its hover. Seen, not read.
  text    text2    coloured type at AA, and the same at a stronger floor.

Every step is solved against its own exposure's ground, so the scale means
the same thing on paper and on ink even though the numbers differ. That is
the same contract the mark and text rings already had, extended.

  solve_scale.py neutral            the 10-step ramp
  solve_scale.py hue [--nm 520]     the role scale for one hue or all
  solve_scale.py emit               the whole token block, ready to paste
  solve_scale.py check              assert every step hits its target

Gamut is a parameter: --gamut srgb (default) or p3. The structure is
identical in both, which is what lets P3 ride along as a media-query
override rather than a second palette.
"""
import argparse, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from solve import (_s2l, _l2s, oklab_to_rgb, oklch_to_hex, max_chroma,
                   relative_luminance, contrast, oklab, delta_e, HUE, BANDS)

ROOT = Path(__file__).resolve().parent.parent

# ── P3, so the same question can be asked in a wider gamut ────────────────
_M_OKLAB_LMS = [[1, 0.3963377774, 0.2158037573],
                [1, -0.1055613458, -0.0638541728],
                [1, -0.0894841775, -1.2914855480]]
_LMS_XYZ = [[1.2268798758, -0.5578149944, 0.2813910456],
            [-0.0405757452, 1.1122868032, -0.0717110568],
            [-0.0763729366, -0.4214933324, 1.5869240198]]
_XYZ_P3 = [[2.4934969, -0.9313836, -0.4027108],
           [-0.8294890, 1.7626641, 0.0236247],
           [0.0358458, -0.0761724, 0.9568845]]


def _mul(M, v):
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


def _oklab_to_p3(L, a, b):
    lms = [x ** 3 for x in _mul(_M_OKLAB_LMS, [L, a, b])]
    return _mul(_XYZ_P3, _mul(_LMS_XYZ, lms))


def max_chroma_p3(L, H):
    lo, hi = 0.0, 0.5
    for _ in range(48):
        mid = (lo + hi) / 2
        r, g, b = _oklab_to_p3(L, mid * math.cos(math.radians(H)), mid * math.sin(math.radians(H)))
        if min(r, g, b) < -0.0005 or max(r, g, b) > 1.0005:
            hi = mid
        else:
            lo = mid
    return lo


def ceiling(L, H, gamut):
    return max_chroma_p3(L, H) if gamut == "p3" else max_chroma(L, H)


# ══════════════════════════════════════════════════════════════════════════
# THE NEUTRAL RAMP — ten steps, because twelve was two more than anyone used
#
# The old ramp had twelve. Auditing every reference in tokens.css and
# components.css, steps 04, 05 and 06 were cited once between them, and 10
# never. Twelve steps is not more expressive than ten, it is just more
# choices at the point of use, which is the opposite of what a ramp is for.
#
# Endpoints are unchanged, so ink is still ink and paper is still paper and
# nothing about the two grounds moves. The steps between them are spaced on
# a mild ease so the dark end — where surfaces actually stack — keeps its
# resolution, and the light end, where it does not, gives some up.
# ══════════════════════════════════════════════════════════════════════════
N_STEPS = 10
N_HUE = 85

# The shipped twelve. Ten is a resample of THIS curve, not a fresh one — the
# spacing is finer at both poles and loosest through the middle, which is
# where surfaces stack and where a step you cannot see is a step you cannot
# use. Inventing a new distribution would have moved every surface in the
# system for no stated reason; resampling moves only the count.
_RAMP_12 = [(0.145, 0.004), (0.195, 0.006), (0.235, 0.008), (0.285, 0.009),
            (0.360, 0.010), (0.450, 0.011), (0.545, 0.012), (0.640, 0.012),
            (0.730, 0.012), (0.810, 0.011), (0.880, 0.010), (0.937, 0.010)]
N_DARK, N_LIGHT = _RAMP_12[0][0], _RAMP_12[-1][0]


def neutral_ramp():
    """Resample the twelve-step curve at ten points, endpoints pinned.

    Chroma comes along for the ride. An earlier attempt modelled it as an
    arc peaking mid-ramp, which drove it to 0.004 at both poles and quietly
    cooled paper from #EDEAE3 to #EBEAE7 — stripping the warmth out of the
    single most-used value in the system to satisfy a formula.
    """
    out = []
    for i in range(N_STEPS):
        pos = i * (len(_RAMP_12) - 1) / (N_STEPS - 1)
        lo = min(int(pos), len(_RAMP_12) - 2)
        f = pos - lo
        L = _RAMP_12[lo][0] + (_RAMP_12[lo + 1][0] - _RAMP_12[lo][0]) * f
        C = _RAMP_12[lo][1] + (_RAMP_12[lo + 1][1] - _RAMP_12[lo][1]) * f
        out.append((f"{i+1:02d}", round(L, 3), round(C, 3)))
    return out


# ══════════════════════════════════════════════════════════════════════════
# THE ROLE SCALE
#
# Each step is a contrast target against the exposure's own ground, and the
# chroma is whatever that hue can carry at the lightness the target lands
# on. Targets, not lightnesses, because a fixed lightness means something
# different on paper than on ink and the whole system exists to deny that.
#
#   bg     1.06  a wash you can read body copy on top of
#   bg2    1.14  its hover
#   line   1.45  a hairline that reads as a border, not as a fill
#   line2  2.10  the same border, emphasised
#   solid  ----  the mark: not a contrast target but a CHROMA target, at
#                95% of the hue's own ceiling inside the exposure window.
#                This is the one step that is about being vivid.
#   solid2 ----  its hover: away from the ground by dL 0.045, so it darkens
#                on paper and lightens on ink without a per-exposure rule
#   text   4.60 / 6.50   coloured type at AA on its ground
#   text2  7.00 / 9.00   the same, for when it must carry alone
#
# The wash steps take a chroma multiplier rather than the ceiling: at 1.06:1
# a hue at full chroma is a stain, not a surface. 30% and 38% were the point
# at which the wash reads as tinted rather than as coloured.
# ══════════════════════════════════════════════════════════════════════════
GROUND_L = {"editorial": 0.937, "luminous": 0.145}
GROUND_HEX = {"editorial": "#EDEAE3", "luminous": "#0B0A08"}
MARK_WINDOW = {"editorial": (2.2, 7.0), "luminous": (4.5, 9.0)}
# 95%, not 93%. solve.py's docstring said 95 and SYSTEM.md said 93; the
# shipped values were nearer 93 and the two documents had quietly disagreed
# for some time. 95 settles it in the direction that helps twice: the solids
# get more chroma, and the categorical separation goes UP rather than down —
# at 93 the re-solved editorial 520/490 pair measured dE 0.129, under the
# 0.130 floor, and at 95 it measures 0.131. Sitting flush at 100 would be
# the gamut boundary itself, where rounding decides the colour.
MARK_CEIL_PCT = 0.95

STEPS = [
    # name,    kind,        target(editorial, luminous), chroma pct of ceiling
    ("bg",     "contrast",  (1.06, 1.06), 0.30),
    ("bg2",    "contrast",  (1.14, 1.14), 0.38),
    ("line",   "contrast",  (1.45, 1.45), 0.55),
    ("line2",  "contrast",  (2.10, 2.10), 0.70),
    ("solid",  "mark",      (None, None), MARK_CEIL_PCT),
    ("solid2", "markhover", (None, None), MARK_CEIL_PCT),
    ("text",   "contrast",  (4.60, 6.50), 0.78),
    ("text2",  "contrast",  (7.00, 9.00), 0.78),
]


def _solve_contrast(H, exposure, target, chroma_pct, gamut):
    """Walk lightness away from the ground until the target ratio is met."""
    ground = GROUND_HEX[exposure]
    gl = GROUND_L[exposure]
    # on paper we go darker, on ink lighter
    direction = -1 if exposure == "editorial" else 1
    best = None
    for step in range(0, 1000):
        L = gl + direction * step * 0.001
        if not (0.02 <= L <= 0.99):
            break
        C = ceiling(L, H, gamut) * chroma_pct
        hx = oklch_to_hex(L, C, H)
        r = contrast(hx, ground)
        if r >= target:
            best = (round(L, 3), round(C, 3), hx, r)
            break
    if best is None:
        # the target is unreachable for this hue; clamp at the far end
        L = 0.02 if direction < 0 else 0.99
        C = ceiling(L, H, gamut) * chroma_pct
        hx = oklch_to_hex(L, C, H)
        best = (round(L, 3), round(C, 3), hx, contrast(hx, ground))
    return best


def _solve_mark(H, exposure, gamut, hover=False):
    """Max chroma inside the exposure's contrast window — the existing rule."""
    ground = GROUND_HEX[exposure]
    lo, hi = MARK_WINDOW[exposure]
    best = None
    for i in range(400, 900):
        L = i / 1000
        C = ceiling(L, H, gamut) * MARK_CEIL_PCT
        hx = oklch_to_hex(L, C, H)
        r = contrast(hx, ground)
        if lo <= r <= hi and (best is None or C > best[1]):
            best = (round(L, 3), round(C, 3), hx, r)
    if best is None:
        raise SystemExit(f"no mark solution for {H} in {exposure}")
    if hover:
        # Away from the ground, so it darkens on paper and lightens on ink
        # with no per-exposure rule. But the window is not advisory: a hover
        # state that leaves it is a mark that stops behaving like a mark
        # mid-interaction, so the shift is clamped to the window edge rather
        # than allowed to overshoot it.
        def walk(sign):
            L = best[0]
            for _ in range(45):
                trial = round(L + sign * 0.001, 3)
                C = ceiling(trial, H, gamut) * MARK_CEIL_PCT
                if not (lo - 0.01 <= contrast(oklch_to_hex(trial, C, H), ground) <= hi + 0.01):
                    break
                L = trial
            return L

        # Preference is away from the ground: darker on paper, brighter on
        # ink. But the bright hues already sit at the top of the luminous
        # window, so "away" has nowhere to go and the hover comes back
        # identical to the rest state — a state change the eye cannot see is
        # not a state. When the preferred direction yields less than dL 0.02,
        # go the other way instead. Either reads as a deliberate shift; only
        # standing still reads as broken.
        away = -1 if exposure == "editorial" else 1
        L = walk(away)
        if abs(L - best[0]) < 0.02:
            L = walk(-away)
        C = ceiling(L, H, gamut) * MARK_CEIL_PCT
        hx = oklch_to_hex(L, C, H)
        best = (round(L, 3), round(C, 3), hx, contrast(hx, ground))
    return best


def scale_for(nm, exposure, gamut="srgb"):
    H = HUE[nm]
    out = {}
    for name, kind, targets, pct in STEPS:
        if kind == "mark":
            out[name] = _solve_mark(H, exposure, gamut)
        elif kind == "markhover":
            out[name] = _solve_mark(H, exposure, gamut, hover=True)
        else:
            t = targets[0 if exposure == "editorial" else 1]
            out[name] = _solve_contrast(H, exposure, t, pct, gamut)
    return out


# ── commands ──────────────────────────────────────────────────────────────
def cmd_neutral(args):
    print(f"{'step':>5} {'L':>7} {'C':>7} {'hex':>9}   vs ink   vs paper")
    ink = oklch_to_hex(N_DARK, 0.004, N_HUE)
    paper = oklch_to_hex(N_LIGHT, 0.004, N_HUE)
    for step, L, C in neutral_ramp():
        hx = oklch_to_hex(L, C, N_HUE)
        print(f"{step:>5} {L:7.3f} {C:7.3f} {hx:>9}   {contrast(hx, ink):6.2f}   {contrast(hx, paper):6.2f}")


def cmd_hue(args):
    nms = [args.nm] if args.nm else list(HUE)
    for nm in nms:
        band = BANDS.get(nm, "")
        print(f"\n── {nm}nm {('· ' + band) if band else ''} ".ljust(66, "─"))
        print(f"{'step':>7} │ {'editorial':^30} │ {'luminous':^30}")
        ed = scale_for(nm, "editorial", args.gamut)
        lu = scale_for(nm, "luminous", args.gamut)
        for name, *_ in STEPS:
            e, l = ed[name], lu[name]
            print(f"{name:>7} │ {e[2]}  L{e[0]:.3f} C{e[1]:.3f} {e[3]:5.2f}:1 │ "
                  f"{l[2]}  L{l[0]:.3f} C{l[1]:.3f} {l[3]:5.2f}:1")


def cmd_check(args):
    failures, checks = [], 0
    for gamut in ("srgb", "p3"):
        for exposure in ("editorial", "luminous"):
            for nm in HUE:
                sc = scale_for(nm, exposure, gamut)
                for name, kind, targets, pct in STEPS:
                    L, C, hx, r = sc[name]
                    checks += 1
                    ceil = ceiling(L, HUE[nm], gamut)
                    if C > ceil + 0.002:
                        failures.append(f"{gamut} {exposure} {nm} {name} chroma {C:.3f} over ceiling {ceil:.3f}")
                    if kind == "contrast":
                        t = targets[0 if exposure == "editorial" else 1]
                        if r < t - 0.06:
                            failures.append(f"{gamut} {exposure} {nm} {name} {r:.2f}:1 under target {t}")
                    if kind == "mark":
                        lo, hi = MARK_WINDOW[exposure]
                        if not (lo - 0.01 <= r <= hi + 0.01):
                            failures.append(f"{gamut} {exposure} {nm} solid {r:.2f}:1 outside {lo}-{hi}")
                # the scale must be monotonic away from the ground
                order = [sc[n][3] for n in ("bg", "bg2", "line", "line2")]
                checks += 1
                if order != sorted(order):
                    failures.append(f"{gamut} {exposure} {nm} wash/line steps not monotonic: {order}")
    print(f"{checks} checks across 10 hues x 2 exposures x 2 gamuts")
    if failures:
        print("\nFAILED:")
        for f in failures[:40]:
            print("  -", f)
        sys.exit(1)
    print("every step hits its target")


def _emit_block(exposure, gamut):
    lines = []
    for nm in HUE:
        sc = scale_for(nm, exposure, gamut)
        band = BANDS.get(nm)
        tail = f"  /* {band} */" if band else ""
        row = []
        for name, *_ in STEPS:
            L, C, hx, r = sc[name]
            row.append(f"  --rsk-{nm}-{name}: oklch({L:.3f} {C:.3f} var(--rsk-h-{nm}));"
                       f"  /* {hx} {r:5.2f} */")
        lines.append(f"  /* ── {nm}nm{tail} ── */")
        lines.extend(row)
        lines.append("")
    return "\n".join(lines)


def cmd_emit(args):
    print(f"/* generated by tools/solve_scale.py emit --gamut {args.gamut} */\n")
    for exposure in ("editorial", "luminous"):
        print(f'[data-exposure="{exposure}"] {{')
        print(_emit_block(exposure, args.gamut))
        print("}\n")
    print("/* neutral ramp */")
    for step, L, C in neutral_ramp():
        print(f"  --rsk-n-{step}: oklch({L:.3f} {C:.3f} var(--rsk-h-neutral));"
              f"  /* {oklch_to_hex(L, C, N_HUE)} */")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("neutral", cmd_neutral), ("hue", cmd_hue),
                     ("emit", cmd_emit), ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("--gamut", choices=["srgb", "p3"], default="srgb")
        if name == "hue":
            p.add_argument("--nm", choices=list(HUE))
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)
