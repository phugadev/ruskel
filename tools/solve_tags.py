#!/usr/bin/env python3
"""
Ruskel — the tag ring solver.

The mark ring answers "what is this about". The tag ring answers "which one
is this" — category colour with no subject-matter meaning, for taxonomies
whose domain is not interface/systems/compute/intelligence.

It is a separate solve for two reasons:

  1. ANGLES ARE OPTIMISED, NOT ASSUMED. Evenly spaced hues put the worst
     pair at dE 0.029, because hue is perceptually compressed through the
     cyan-teal arc. Solving for the spacing lifts the same ten hues to
     0.081. This is SYSTEM.md 1.4b's finding applied to a second ring.

  2. CHROMA IS HELD DOWN ON PURPOSE. Tags sit at 55% of each hue's sRGB
     ceiling where marks sit at 95%. Not to avoid collision -- a tag ring
     and a band ring must never share a surface anyway -- but for rule 8.
     A taxonomy index is a page of twenty labels; at mark chroma it reads
     as a fruit salad competing with the content it is indexing.

  solve_tags.py ring            print the ten tags, both exposures
  solve_tags.py separation      internal dE, and distance to the mark ring
  solve_tags.py optimise [N]    re-derive the angles for N tags
"""
import argparse, importlib.util, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("solve", ROOT / "tools" / "solve.py")
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)

# 55% of ceiling. See the module docstring: this is a rule-8 decision.
TAG_CHROMA = 0.55

# Solved by `optimise 10`. Ten is the number the ring can carry: twelve
# drops the worst pair to 0.060, at or under the empirical floor for
# labelled-in-place colour. Past ten, stop colouring and just label.
TAG_HUE = {"01": 31.0, "02":  50.0, "03": 103.0, "04": 143.0, "05": 178.0,
           "06": 242.0, "07": 255.0, "08": 288.0, "09": 324.0, "10": 355.0}

# Labelled in place, so the 0.130 series floor does not apply (tokens.css,
# the --chart-* note). The bar is the measured one from a real site doing
# this well: ten category dots, worst pair 0.063.
MIN_TAG_DE = 0.063


def solve_tag(H, exposure):
    """Max chroma at TAG_CHROMA of ceiling, inside the exposure's window."""
    ground = S.GROUND[exposure]; lo, hi = S.WINDOW[exposure]
    best = None; L = 0.25
    while L <= 0.95:
        C = S.max_chroma(L, H) * TAG_CHROMA
        hx = S.oklch_to_hex(L, C, H); r = S.contrast(hx, ground)
        if lo <= r <= hi and (best is None or C > best[1]):
            best = (L, C, hx, r)
        L += 0.005
    return best


def _pts(angles, exposure):
    out = []
    for H in angles:
        got = solve_tag(H, exposure)
        if got is None: return None
        out.append(S.oklab(got[0], got[1], H))
    return out


def worst_pair(angles):
    """Worst pairwise dE across BOTH exposures — the binding constraint."""
    worst = (9.0, None, None)
    for exposure in ("editorial", "luminous"):
        pts = _pts(angles, exposure)
        if pts is None: return (-1.0, None, None)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = S.delta_e(pts[i], pts[j])
                if d < worst[0]: worst = (d, i + 1, j + 1)
    return worst


def cmd_ring(args):
    for exposure in ("editorial", "luminous"):
        lo, hi = S.WINDOW[exposure]
        print(f"\n{exposure.upper()}  ground {S.GROUND[exposure]}  window {lo}-{hi}:1")
        for k, H in TAG_HUE.items():
            L, C, hx, r = solve_tag(H, exposure)
            print(f"  tag-{k}  oklch({L:.3f} {C:.3f} {H:5.1f})  {hx}  {r:5.2f}:1")


def cmd_separation(args):
    d, a, b = worst_pair(list(TAG_HUE.values()))
    print(f"\ninternal worst pair: tag-{a:02d} / tag-{b:02d}  dE {d:.3f}  (floor {MIN_TAG_DE})")
    print("  " + ("holds" if d >= MIN_TAG_DE else "FAILS"))
    for exposure in ("editorial", "luminous"):
        marks = {nm: (S.solve_mark(H, exposure), H) for nm, H in S.HUE.items()}
        near = (9.0, None, None)
        for k, H in TAG_HUE.items():
            L, C, hx, r = solve_tag(H, exposure)
            p = S.oklab(L, C, H)
            for nm, (m, mh) in marks.items():
                dd = S.delta_e(p, S.oklab(m[0], m[1], mh))
                if dd < near[0]: near = (dd, k, nm)
        tc = [solve_tag(H, exposure)[1] for H in TAG_HUE.values()]
        mc = [S.solve_mark(H, exposure)[1] for H in S.HUE.values()]
        print(f"  {exposure:10} nearest mark: tag-{near[1]} / {near[2]}nm  dE {near[0]:.3f}"
              f"   chroma tags {min(tc):.3f}-{max(tc):.3f} vs marks {min(mc):.3f}-{max(mc):.3f}")


def cmd_optimise(args):
    n = args.n
    random.seed(7)
    best = [i * (360 / n) for i in range(n)]
    best_s = worst_pair(best)[0]
    even = best_s
    step = 12.0
    for it in range(1400):
        cand = list(best)
        cand[random.randrange(n)] = (cand[random.randrange(n)] + random.uniform(-step, step)) % 360
        s = worst_pair(cand)[0]
        if s > best_s: best, best_s = cand, s
        if it % 300 == 299: step = max(1.5, step * 0.65)
    print(f"N={n}  even {even:.3f}  ->  optimised {best_s:.3f}  (floor {MIN_TAG_DE})")
    print("  " + " ".join(f"{a:.0f}" for a in sorted(best)))


def cmd_verify(args):
    d, a, b = worst_pair(list(TAG_HUE.values()))
    if d < MIN_TAG_DE:
        print(f"FAILED: tag-{a:02d}/tag-{b:02d} dE {d:.3f} below floor {MIN_TAG_DE}")
        sys.exit(1)
    for exposure in ("editorial", "luminous"):
        lo, hi = S.WINDOW[exposure]
        for k, H in TAG_HUE.items():
            got = solve_tag(H, exposure)
            if got is None:
                print(f"FAILED: tag-{k} unsolvable in {exposure}"); sys.exit(1)
            if not (lo - 0.01 <= got[3] <= hi + 0.01):
                print(f"FAILED: {exposure} tag-{k} contrast {got[3]:.2f} outside {lo}-{hi}")
                sys.exit(1)
    print(f"tag ring holds — worst pair dE {d:.3f}, floor {MIN_TAG_DE}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ring").set_defaults(fn=cmd_ring)
    sub.add_parser("separation").set_defaults(fn=cmd_separation)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    p = sub.add_parser("optimise"); p.add_argument("n", type=int, nargs="?", default=10); p.set_defaults(fn=cmd_optimise)
    a = ap.parse_args(); a.fn(a)
