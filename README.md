# Ruskel

**One spectrum, two exposures.** A design system for interfaces that are
either *read* or *operated* — and which should look like the same author
made both.

```
registry.json        the shadcn registry manifest — this file is the registry
packages/tokens      the token layer: engine output, and the API over it
packages/ui          shadcn primitives, moulded
docs/system.html     the specimen — reads the tokens live, cannot drift
docs/SYSTEM.md       the written system, decision by decision
tools/solve*.py      the colour engine — the palette is its output
```

## Four tiers, and you only type one

```
0  engine      tools/solve.py, tools/solve_scale.py         private
1  primitive   --rsk-spectrum-520-solid, --rsk-neutral-04   generated
2  semantic    --rsk-bg-raised, --rsk-fg-secondary,         THE API
               --rsk-border-default, --rsk-state-hover,
               --rsk-band-solid, --rsk-danger-fg
3  modes       data-exposure, data-density, data-band, data-voice
```

**Wavelengths never appear above tier 1.** The spectrum is how the colours
are *computed*, not how they are *addressed* — you should never have to know
that 470nm is blue, and neither should an agent writing your markup. The
engine can be re-solved, re-gamuted or replaced outright without a component
changing.

Meaning is carried by words instead. A band is a subject:

```html
<tr data-band="intelligence">   <!-- reads --rsk-band-solid, --rsk-band-bg -->
```

Two rules hold the whole thing together:

- **A component reads tier 2 and nothing else.** Measured in CI: the
  component layer makes zero primitive reads.
- **No adjectives without a controlled scale.** There is no `fg-subtle` or
  `border-light` — "subtle" invites an argument about what is subtler than
  what. `primary / secondary / tertiary / metadata` are positions and cannot
  be argued with. Surfaces are levels for the same reason: `canvas`,
  `surface`, `raised`, `overlay`.

---

## The idea

An exposure is not a light/dark theme. A theme recolours a fixed design. An
exposure changes what light is *doing*.

| | Editorial | Luminous |
|---|---|---|
| Ground | paper | ink |
| Voice | author | product |
| Colour behaves as | pigment | light |
| For | site, writing, case studies, proposals | apps, dashboards, demos, client UI |

Editorial **marks** with a band — a rule, a chip, a word. Luminous **emits**
it, with falloff around the source. Ink and paper swap; the spectrum
re-solves for the new ground.

Components never know which exposure they are in. The emission tokens exist
in both and resolve to nothing on paper, so a component writes
`box-shadow: var(--rsk-glow-sm)` unconditionally and simply does not glow in
editorial. A component that needs a `[data-exposure]` override is a bug in
the tokens.

## Use it

Via the shadcn CLI — the repo *is* the registry, so there is nothing hosted
and no build step:

```bash
npx shadcn@latest add phugadev/ruskel/ruskel            # tokens + components
npx shadcn@latest add phugadev/ruskel/ruskel-tokens     # tokens only
npx shadcn@latest add phugadev/ruskel/ruskel-tailwind   # tokens + Tailwind v4 utilities
```

Or plainly, if you are not using shadcn:

```bash
npm install @ruskel/tokens @ruskel/ui
```

```css
@import "@ruskel/tokens";
@import "@ruskel/ui";
```

On Tailwind v4, import the bridge instead of the tokens — it pulls them in
itself and adds the theme keys, so `bg-raised`, `text-fg-secondary`,
`bg-band-solid`, `h-control-md` and `shadow-glow-sm` become real utilities:

```css
@import "tailwindcss";
@import "@ruskel/tokens/tailwind";
```

Every key is declared `inline`, which is load-bearing rather than stylistic:
the role scale lives under `[data-exposure]`, not on `:root`, so a
theme variable emitted at the root would resolve against a value that is not
there. Inlining puts the reference in the utility itself, and it resolves at
the element — inside whatever exposure that element is standing in. Tailwind
utilities obey rule 3 for the same reason components do.

```html
<body data-exposure="editorial">
  <section data-exposure="luminous"> <!-- a product plate inside an essay -->
</body>
```

Shadcn components inherit everything through the variable contract. No
component source is edited.

## The rules

1. **A band never appears decoratively.** `interface`, `systems`, `compute`
   and `intelligence` are subjects, not colours. If something is amber it is
   *about* interface. Corollary: chrome carries no band at all — not the
   focus ring, not the selection, not a link, not a tab indicator. That
   reflex has been corrected four separate times; assume it is you.
2. **Status is not a band.** Health and category are different axes. Status
   carries one hue and otherwise encodes itself in form: hollow = fine,
   ring = watch, filled = critical.
3. **Components don't know their exposure — or their band.** Style against
   tier-2 names. A component that needs a `[data-exposure]` override is a
   bug in the tokens, and one that names a wavelength is a bug in the
   component.
4. **Marks are seen; text is read.** Never swap the two rings.
5. **Mono is metadata, never content.** Labels, figures, timestamps, code.
6. **Numbering must encode order.** Unordered peers get a rule and a label.
7. **Radius encodes role.** *Structure* — cards, dialogs, inputs, buttons,
   frames — is near-square at 2/4/6px. *Tokens* — chips, tags, status dots,
   switches — are pills. The test: does it hold something, or is it a thing?
   Containers get the hard corner, objects get the round one. Mixing them is
   not two schools of design; it is one rule with two outcomes, and the shape
   tells you which kind of element you are looking at.
8. **Spend boldness once per view.** One luminous moment per screen.
9. **Colour is never the only carrier.** The system must survive greyscale.

## The palette is computed, not picked

Every value is the output of a constraint solve, and the solver ships with
the repo. That is what makes the system extendable rather than frozen.

```bash
python3 tools/solve.py ring              # the solid step per exposure
python3 tools/solve.py separation        # pairwise dE across the six series
python3 tools/solve.py bridge            # the Tailwind theme keys still resolve
python3 tools/solve.py verify            # assert every constraint still holds

python3 tools/solve_scale.py hue --nm 520   # one hue's eight role steps
python3 tools/solve_scale.py neutral        # the ten-step ramp
python3 tools/solve_scale.py check          # every step against its target
```

`verify` re-derives each declared token, checks it against its exposure's
contrast window, confirms no chroma exceeds the sRGB ceiling, and asserts
the categorical series never falls below the separation floor. `check` does
the same for all eight role steps of all ten hues, in both gamuts. Both exit
non-zero on failure and both run in CI.

Two constraints worth knowing, because they cost the most to satisfy:

- **The solid step is per-exposure.** The same hue does not have the same
  impact on both grounds; a shared amber measured 8.8:1 on ink and 1.7:1 on
  paper. Each ground solves its own ring, at maximum chroma within a
  contrast window.
- **Six categorical hues, not eight.** Once the warm arc is reserved for
  warning and critical, eight hues cannot separate — cyan/blue and
  indigo/violet collapse. Six is where every stop sits at its own gamut
  ceiling and nothing collides. Past six, label the series directly.
- **Eight role steps per hue, solved against targets rather than fixed
  lightnesses.** `bg` and `bg2` are washes you can set body copy on, `line`
  and `line2` are hairlines, `solid` and `solid2` are the mark and its
  hover, `text` and `text2` are type at AA and above. A fixed lightness
  means something different on paper than on ink, which is the thing this
  system exists to deny.

On a Display P3 screen the hues are re-solved in the wider gamut — same
angles, same lightnesses, same targets, only a higher ceiling. Green gains
35%, cyan 32%. It rides in a `@media (color-gamut: p3)` block, so no name
differs and no component knows.

## Typography

Three registers, assigned by **who is speaking**:

| | speaker | used for |
|---|---|---|
| **Mono** | the machine | figures, timestamps, states, nm readouts, chips |
| **Sans** | the system | labels, nav, controls, body copy |
| **Serif** | a person | article titles, pull quotes |

The test: *if a machine could have written it, it is not serif.*

Inter, IBM Plex Mono, Instrument Serif. Faces are declared, not bundled —
load them in the app (next/font, Fontsource, a `<link>`) and the stacks pick
them up.

The serif is gated on **voice**, which is independent of exposure:

```html
<article data-exposure="luminous" data-voice="author">
```

A dark-ground site that publishes essays is luminous *and* authored, so
gating on the ground would silence the serif exactly where a person is
writing. Product is the default, so it never leaks onto interface surfaces.
It is display-only too: Instrument Serif loses its footing under about 24px.

Mono remains the highest-risk element — keeping it strictly to metadata is
what stops it becoming a costume.

## Releasing

**Bump the version in the PR that ships the change** — never in an earlier
PR of a stack. `@ruskel/ui@0.5.0` was published from a stacked base that had
already taken the number, so the primitives merged afterwards had nowhere to
go and shipped as 0.6.0 instead. The two packages version independently for
the same reason: tokens and ui do not always change together, and forcing
lockstep means publishing empty versions to keep the numbers aligned.

Before publishing, check that what is on npm matches `main`:

```bash
npm pack @ruskel/ui@latest && tar -xzf ruskel-ui-*.tgz
shasum -a 256 package/src/components.css packages/ui/src/components.css
```

## Ownership

Built and maintained by [Enric Trillo](https://github.com/phugadev). It is
a personal design system: the decisions in it are mine, and it moves when I
change my mind about one of them. MIT licensed — free to use in client work,
including work I have nothing to do with.

## Status

**0.9.0.** The token API settled at this version — four tiers, semantic
public layer, spectrum private. Before 0.9 the palette's internals *were*
the interface, so anything written against 0.8 names will not work.

Complete and verified: colour, neutrals, surfaces, typography, geometry,
spacing, density, exposure, and 46 components. Thin: motion is two tokens.
Absent: charts are tokenised but no library is wired, and there is no icon
set. `--rsk-fg-*` rank naming is on trial and may move.

### Published

```bash
npm install @ruskel/tokens @ruskel/ui   # 0.9.0
```

`latest` and `next` both point at **0.9.0**, and `main` matches. The tag
survives so a future release can go up as `next` without moving `latest`
under anyone.

**0.9.0 is breaking against 0.7.x**, which is the point of the minor bump:
the public names changed shape, so `^0.7.0` will not pick it up. If you are
on 0.7.x, `--rsk-n-NN` is now `--rsk-neutral-NN`, `--rsk-520-solid` is
`--rsk-spectrum-520-solid`, and the 80 wavelength-named Tailwind utilities
are gone in favour of `bg-band-solid` and the tier-2 names. Most bare token
names — `--rsk-text`, `--rsk-rule`, `--rsk-ground`, `--rsk-mark-590` — still
resolve, so the migration is usually smaller than it sounds.

**0.7.1 exists on the `release/0.7.x` branch** and is the last healthy 0.7.
0.7.0 shipped a glow that never fired: `--rsk-glow-*` was declared on
`[data-exposure]`, above the element that sets `--rsk-mark`, so it
substituted to `transparent` and inherited that everywhere. If you are
pinned to 0.7 for any reason, be on 0.7.1.
