# Proposal 02 — the prose register: type re-solves for the reader, not the ground

**Status:** proposed. Values are reasoned, not solved — see *What is asserted*
at the end. Nothing in `tokens.css` is changed by this document.

*Checked against 0.9.0:* the gap is still real — every size, measure and
leading value still sits in `:root` and is identical in both exposures. Note
that 0.9 shipped a prose register for **colour** on the same axis: `.rsk-prose`
sets body at `--rsk-fg-secondary` and `<strong>` at `--rsk-fg-primary`, gated
on a class rather than on voice. This proposal covers **size**, and the two
would want to agree on one gate before either is called finished.

---

## The gap

Ruskel's thesis is that a value asserted to serve two grounds is usually wrong,
and the mark ring is the proof: one shared ring put 590nm at 10.15:1 on ink and
1.71:1 on paper, so each exposure now solves its own.

Type never got that treatment. Both `[data-exposure]` blocks carry colour and
nothing else. Every size, measure, tracking and leading value sits in `:root`
and is identical everywhere:

```
--rsk-text-base: 0.875rem;   /* 14px */
--rsk-measure: 68ch;
```

So editorial — the exposure explicitly *for* "site, writing, case studies,
proposals" — sets prose at 14px. That is instrument-panel sizing. Long-form
reading wants roughly 17px, and `68ch` means something quite different at each
size. The system that refuses to let one amber serve two grounds is letting one
body size serve a dashboard and an essay.

## The correction: the axis is voice, not exposure

My first framing of this was that type should re-solve per exposure, the way
colour does. That is wrong, and `tokens.css` already contains the argument
against it — in the note explaining why the serif is voice-gated:

> `data-exposure` — which ground you are on. `data-voice` — who is speaking.
> Those are orthogonal. A dark-ground site that publishes essays is luminous
> exposure AND author voice.

Reading size follows the same logic exactly. A luminous dashboard has no prose;
a luminous essay does. Gating size on exposure would set an essay at 14px purely
for sitting on ink, which is the identical error the serif gate already avoids.

There is also a cut that gating-by-exposure gets wrong in the other direction.
**The interface scale must stay exposure- and voice-invariant.** If
`--rsk-text-base` moved, every button, input, table cell and label on an
editorial page would grow with it — an essay page's form controls are not
bigger controls. What re-solves is *prose*, which is why this is a new register
rather than a change to the existing scale.

So:

| | axis | why |
|---|---|---|
| interface scale | neither | a control is a control on any ground, in any voice |
| prose size, measure | **voice** | set by who is speaking and how long you read |
| prose leading | **exposure** | halation is a property of light on a dark ground |

## Leading is the one part that *is* a ground property

Light type on a dark ground blooms — strokes spread optically, and lines set for
paper read tighter than they measure. That is about the ground, not the speaker,
so it belongs on exposure while size belongs on voice.

It also has an obvious implementation here, because the codebase just grew the
right pattern. `--rsk-emit` is a unitless scalar set by exposure and consumed by
`calc()` downstream, so glow survives inheritance intact. Halation wants exactly
that shape:

```css
:root                        { --rsk-halation: 0;    }
[data-exposure="luminous"]   { --rsk-halation: 0.06; }
```

One scalar, no per-exposure duplication of the prose block, and it composes with
voice rather than multiplying against it.

## Tokens

```css
/* ── PROSE REGISTER ───────────────────────────────────────────────────
   Sizes for reading, distinct from the interface scale. The default IS
   the interface scale — product surfaces are unchanged, and nothing
   leaks — and only data-voice="author" opens the reading sizes, exactly
   as it opens the serif.

   Leading takes the halation scalar instead: light on ink blooms, so the
   same measure needs a touch more room on a dark ground. That is a
   property of the ground, not the speaker, which is why it rides
   exposure while size rides voice.                                      */

:root {
  --rsk-halation: 0;
  --rsk-prose-size:    var(--rsk-text-base);        /* 14px — product */
  --rsk-prose-measure: var(--rsk-measure);          /* 68ch */
  --rsk-prose-leading: calc(var(--rsk-leading-base) + var(--rsk-halation));
}

[data-exposure="luminous"] { --rsk-halation: 0.06; }

[data-voice="author"] {
  --rsk-prose-size:    1.0625rem;                   /* 17px — reading */
  --rsk-prose-measure: 54ch;
  --rsk-prose-leading: calc(1.62 + var(--rsk-halation));
}
```

And the component it exists for:

```css
.rsk-prose {
  font-size: var(--rsk-prose-size);
  line-height: var(--rsk-prose-leading);
  max-width: var(--rsk-prose-measure);
  color: var(--rsk-text-prose);
}
```

`.rsk-authored` already gates the serif on the same attribute, so an
`<article data-voice="author">` picks up voice, size, measure and leading from
one declaration.

## Why 54ch and not 68ch

`ch` is the width of `0`, which in Inter is substantially wider than the average
lowercase letter, so the conversion is not intuitive and should not be done in
your head. **I first proposed 64ch on the assumption it would land near 72
characters. Rendered and measured, it lands at 85.** The specimen caught it.

Measured in Inter, in the browser, against the rendered `max-width`:

| setting | box | avg char | characters |
|---|---|---|---|
| 68ch @ 14px — as shipped | 601px | 6.66px | **90** |
| 64ch @ 17px — first proposal | 686px | 8.09px | **85** |
| 54ch @ 17px — proposed | 579px | 8.09px | **72** |

So 1ch is about 1.32 average characters in Inter, and the shipped 68ch is not
marginally over the 45–75 band — it is 20% past it. That makes the underlying
complaint stronger than the first draft of this document claimed, and the
correction smaller than it looks: 54ch at 17px is a *wider* column in pixels
than 68ch at 14px, because the type grew more than the measure shrank.

One consequence worth stating: the product default keeps 68ch, which measures 90
characters. That is fine for a dashboard, where nothing is set in paragraphs, and
wrong for anything long. If product-voice long-form ever appears, it needs the
same treatment.

## What is asserted

Proposal 01 is solved: there is a solver, a floor, and a failing exit code.
This one is not, and should not pretend otherwise.

- **Solved-adjacent:** the 45–75 character band is long-established, and the
  `ch`-to-character conversion is arithmetic.
- **Asserted:** 17px, 1.62, and the 0.06 halation increment. Halation is a real
  and well-documented effect; its *magnitude* here is judgement.

The test that would settle it is the same one I would run on the Geist question:
one long-form specimen at author voice, rendered in all four combinations of
exposure and voice, read at arm's length. Nothing about that needs a solver, and
it should not be written up as though it had one.
