# Proposal 01 — the tag ring: colour that identifies without signifying

**Status:** proposed. Solver shipped at `tools/solve_tags.py`; tokens below are
its output. Nothing in `tokens.css` is changed by this document.

*Checked against 0.9.0:* the values below still match `solve_tags.py ring`
exactly — the tag ring solves at 55% of ceiling on its own angles, so neither
the move to 95% for marks nor the P3 layer touched it. If this ships, the
public names would be `--rsk-tag-NN` at tier 1 with a contextual
`--rsk-tag-*` set resolved by `[data-tag]`, mirroring how `[data-band]`
works — a raw ordinal index is exactly the kind of primitive 0.9 moved
behind the API.

---

## The gap

Every hue in Ruskel is a named position with a meaning. 590nm *is* interface,
520nm *is* systems, 405nm *is* intelligence, and rule 1 enforces it: a band
never appears decoratively.

That is right for the domain the system was built in, and it does not travel.
Tag a personal-site essay taxonomy, or a client whose subject matter is not
interface/systems/compute/intelligence, and there is no legal way to colour a
category. You either assign "interface amber" to a post about cooking — rule 1
broken, and the band vocabulary quietly devalued — or you go monochrome.

The system already knows this case exists. The `--chart-*` note in `tokens.css`
carves it out:

> When every instance is labelled *in place* (filter chips, tag lists, category
> dots beside their name) colour is redundant reinforcement and the floor does
> not apply.

But the escape hatch hands back the same loaded hues — the four bands plus four
display stops. **A rule exists for unmeaning colour and no tokens exist to serve
it.** That is the gap.

## The construction

A second ring, solved separately, that answers *which one is this* rather than
*what is this about*.

**Ordinal names, never nm.** `--rsk-tag-01` … `--rsk-tag-10`, mirroring the
`--rsk-neutral-01..10` neutral ramp. An nm name would imply spectrum membership and
therefore meaning, which is the precise thing this ring must not have. Ordinal
says "index, no semantics" in the same breath as the greys.

**Angles are solved, not assumed.** Ten evenly-spaced hues put the worst pair at
dE 0.029 — hue is perceptually compressed through the cyan-teal arc, which is
the same wall §1.4b hit at eight chart hues. Optimising the spacing lifts the
identical ten hues to **0.081**.

```
N=10   even-spaced 0.042   ->  optimised 0.081
N=12   even-spaced 0.035   ->  optimised 0.060
```

**Ten is the number.** Twelve falls to 0.060, at or under the empirical floor.
The bar here is not the 0.130 series floor — these are always labelled in place —
but the measured 0.063 from a real site doing exactly this. Past ten, stop
colouring and label directly, exactly as the chart ring says past six.

**Chroma is held at 55% of ceiling, where marks sit at 95%.** Not to avoid
collision — a tag ring and a band ring must never share a surface anyway — but
for **rule 8**. A taxonomy index is a page of twenty labels at once; at mark
chroma it reads as a fruit salad competing with the content it indexes. The
measured register gap:

```
                 tags          marks
editorial   0.070-0.173    0.113-0.294
luminous    0.075-0.173    0.122-0.294
```

**Mark role only — no text ring.** `.rsk-chip` already does the right thing:
the hue is a dot, the label stays `--rsk-text` at full contrast. So a tag needs
one value, not two, and rule 9 is satisfied structurally — the name is always
right there in neutral type.

## Integration

Set `--rsk-mark`, and every existing primitive works untouched — chip, status
dot, meter, density grid, and the proposed `.rsk-spark`. No component learns a
new contract.

```css
[data-tag="01"] { --rsk-mark: var(--rsk-tag-01); }
/* … through 10 */
```

## The rule this adds

> **A tag ring and a band ring never share a surface.** Bands classify subject
> matter; tags distinguish members of a set. A surface that needs both is a
> surface with two taxonomies, which is a content problem, not a colour problem.

## Tokens

```css
/* ── L2c TAG RING — ten hues, no meaning ──────────────────────────────
   Category colour for taxonomies outside the band vocabulary. Ordinal by
   construction: these are indices, not wavelengths. 55% of gamut ceiling
   (marks are 95%) so a page of twenty reads as an index, not an alarm.
   Angles solved by tools/solve_tags.py; worst pair dE 0.080 against a
   0.063 floor. Never on the same surface as a band.                     */

[data-exposure="editorial"] {
  --rsk-tag-01: oklch(0.635 0.136  31.0);   /* #D06756  3.04 */
  --rsk-tag-02: oklch(0.710 0.103  50.0);   /* #D68E65  2.21 */
  --rsk-tag-03: oklch(0.700 0.081 103.0);   /* #A7A165  2.20 */
  --rsk-tag-04: oklch(0.690 0.127 143.0);   /* #69AF65  2.21 */
  --rsk-tag-05: oklch(0.690 0.070 178.0);   /* #6AAA9B  2.23 */
  --rsk-tag-06: oklch(0.700 0.091 242.0);   /* #69A5D3  2.21 */
  --rsk-tag-07: oklch(0.625 0.113 255.0);   /* #578ACB  2.96 */
  --rsk-tag-08: oklch(0.510 0.161 288.0);   /* #6551BB  5.07 */
  --rsk-tag-09: oklch(0.670 0.173 324.0);   /* #C86BD0  2.70 */
  --rsk-tag-10: oklch(0.650 0.147 355.0);   /* #D26594  2.90 */
}

[data-exposure="luminous"] {
  --rsk-tag-01: oklch(0.635 0.136  31.0);   /* #D06756  5.42 */
  --rsk-tag-02: oklch(0.720 0.105  50.0);   /* #DA9168  7.76 */
  --rsk-tag-03: oklch(0.745 0.086 103.0);   /* #B6AF6E  8.81 */
  --rsk-tag-04: oklch(0.735 0.135 143.0);   /* #73BF6F  8.87 */
  --rsk-tag-05: oklch(0.740 0.075 178.0);   /* #75BBAB  8.91 */
  --rsk-tag-06: oklch(0.705 0.092 242.0);   /* #6AA7D5  7.63 */
  --rsk-tag-07: oklch(0.625 0.113 255.0);   /* #578ACB  5.56 */
  --rsk-tag-08: oklch(0.585 0.133 288.0);   /* #796DC6  4.54 */
  --rsk-tag-09: oklch(0.670 0.173 324.0);   /* #C86BD0  6.10 */
  --rsk-tag-10: oklch(0.650 0.147 355.0);   /* #D26594  5.68 */
}
```

Note tags 01, 07, 09, 10 carry identical values in both exposures — those hues
land inside both contrast windows at the same lightness. That is the ring
behaving like the mark ring, which also coincides at 700nm and 470nm.

## Open question

Tags 01 (31°) and 10 (355°) sit in the warm arc that rule 1 reserves for warning
and critical. At 55% chroma they are terracotta and rose rather than alarm
red — nearest-mark dE 0.088 and 0.130 respectively — and they never co-occur
with a band. I think that clears it. If you disagree, dropping both leaves eight
tags and lifts the worst pair, at the cost of a taxonomy with no warm end.
