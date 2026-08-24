# @ruskel/tokens

The two-exposure token layer.

```bash
npm install @ruskel/tokens
```

```css
@import "@ruskel/tokens";
```

Then set an exposure on any subtree:

```html
<body data-exposure="editorial">   <!-- ink on paper — the author voice -->
<div  data-exposure="luminous">    <!-- paper on ink — the product voice -->
```

Nothing else is required. The file maps itself onto the shadcn variable
contract (`--background`, `--primary`, `--ring`, `--chart-1…6`, `--sidebar-*`),
so shadcn components inherit the system without any component edits.

## Four tiers, and you only type one

```
0  engine      tools/solve.py, tools/solve_scale.py         private
1  primitive   --rsk-spectrum-520-solid, --rsk-neutral-04   generated
2  semantic    --rsk-bg-raised, --rsk-fg-secondary, …       THE API
3  modes       data-exposure, data-density, data-band, data-voice
```

**Tier 1 is not for you.** It is solver output — wavelengths, gamut
ceilings, contrast solves — and it exists so tier 2 can be derived rather
than picked. Read it and you are coupled to how the palette is currently
computed. The engine is free to change; the API is not.

## Tier 2 — the API

| | |
|---|---|
| `--rsk-bg-canvas` `-surface` `-raised` `-overlay` | the surface stack, bottom to top |
| `--rsk-fg-primary` `-secondary` `-tertiary` `-metadata` | type, by contrast rank — 16.5 / 10 / 5.5 / 4 : 1 |
| `--rsk-fg-on-solid` | type on a vivid fill |
| `--rsk-border-default` `-strong` | translucent hairlines that composite with what is behind |
| `--rsk-state-hover` `-pressed` `-selected` | translucent overlays — composite, do not replace |
| `--rsk-state-focus` `-disabled` | the ring, and an opacity scalar |
| `--rsk-band-bg` `-line` `-solid` `-fg` (+ `-hover`, `-strong`) | resolved by the enclosing `[data-band]` |
| `--rsk-danger-*` `--rsk-warning-*` `--rsk-success-*` | status, as words |
| `--rsk-size-control-sm/md/lg` `--rsk-size-hairline` | remapped by `[data-density]` |
| `--rsk-space-inset` `-stack` `-section` | spacing by relationship; `section` ≥ 2 × `stack` |
| `--rsk-space-01 … -10` | the raw 4px scale, when none of the three is what you mean |

Two rules hold this together:

- **A component reads tier 2 and nothing else.** Enforced in CI.
- **No adjectives without a controlled scale.** There is no `fg-subtle` or
  `border-light`, because "subtle" invites an argument about what is subtler
  than what. Ranks and levels cannot be argued with.

Never set type in a `-solid` or fill with a `-fg`. That swap is still the
single most common way to make the system look wrong.

## Bands carry the meaning

A band is a **subject**, not a colour:

```html
<tr data-band="intelligence">
```

```css
.thing { background: var(--rsk-band-bg); color: var(--rsk-band-fg); }
```

`interface`, `systems`, `compute`, `intelligence`, `warning`, `critical`.
The component names none of them and works in all six — it does not know its
exposure, and it does not know its band.

Rule 1: a band never appears decoratively. If something is amber it is
*about* interface. Chrome carries no band at all — not focus, not selection,
not a link, not a tab indicator.

## Modes

```html
<body data-exposure="luminous" data-density="compact">
```

`data-exposure` is `editorial` or `luminous`. `data-density` is `compact`,
`default` or `spacious`, and moves you **one rung on the control scale** —
compact's `md` is default's `sm`. They are orthogonal and compose: an
editorial plate can be spacious inside a compact luminous dashboard.

`data-voice="author"` is the only thing that unlocks the serif, on either
ground.

## Tailwind v4

Import the bridge instead of the tokens — it imports them itself:

```css
@import "tailwindcss";
@import "@ruskel/tokens/tailwind";
```

The shadcn contract comes with it (`bg-background`, `text-muted-foreground`),
plus tier 2 as utilities: `bg-raised`, `text-fg-secondary`,
`border-border-default`, `bg-band-solid`, `bg-danger-bg`, `h-control-md`,
`p-inset`, `shadow-glow-md`, `rounded-pill`, `max-w-measure`.

No utility names a wavelength. `bg-band-solid` needs you to know the element
sits in a band, which its own markup already says.

The neutral ramp is the one primitive still exposed, as `bg-neutral-04` and
friends — a grey has no meaning to leak, so reaching for a rung is an escape
hatch rather than a coupling. Prefer `bg-surface` and `text-fg-tertiary`.

Tailwind's own palette is left switched on, so `bg-red-500` still works. It
is a hue nobody solved and it will not survive greyscale; to remove it and
everything like it, add one line after the import:

```css
@theme { --color-*: initial; }
```

## Extending it

Colours are solver output, not hand-picked. Add a hue by adding an angle and
re-running:

```bash
python3 tools/solve_scale.py hue --nm 520   # one hue's eight role steps
python3 tools/solve_scale.py check          # every step against its target
python3 tools/solve.py verify               # every constraint the system claims
```

Adding a **band** is a different act from adding a hue: a band asserts that a
subject exists. The four display stops (550, 490, 440, 370) deliberately have
no band, because they name colours rather than subjects — and an attribute
where half the values mean something and half are just hues is the mixed
vocabulary this layer exists to prevent.
