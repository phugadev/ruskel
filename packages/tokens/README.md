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
contract (`--background`, `--primary`, `--ring`, `--chart-1…8`, `--sidebar-*`),
so shadcn components inherit the system without any component edits.

## Layers

| | |
|---|---|
| `--rsk-n-01 … --rsk-n-12` | neutral ramp, warm, shared by both exposures |
| `--rsk-mark-*` | vivid fills, bars, dots, glows, borders. Seen, not read. |
| `--rsk-text-*` | coloured type. Read, so constrained to AA. |
| `--rsk-deep-*` | second depth per band, chart overflow only |
| `--rsk-ground` `--rsk-surface` `--rsk-rule` `--rsk-text` | chrome |

Never use a `text-*` value as a fill or a `mark-*` value as body type. That
swap is the single most common way to make the system look wrong.

## Tailwind v4

Import the bridge instead of the tokens — it imports them itself:

```css
@import "tailwindcss";
@import "@ruskel/tokens/tailwind";
```

That adds the theme keys Tailwind needs before a utility can exist. The
shadcn contract comes with it (`bg-background`, `text-muted-foreground`),
plus the system's own names:

| utility | what |
|---|---|
| `bg-ground` `bg-surface` `bg-surface-2` | the three chrome levels |
| `text-ink` `text-ink-prose` `text-ink-muted` `text-ink-faint` | type, by role |
| `bg-mark-520` … | the mark ring — fills, bars, dots. Seen, not read. |
| `text-tint-520` … | the text ring — coloured type at AA on its ground |
| `bg-deep-405` … | the second depth per band |
| `bg-mark` `text-tint` `text-on-mark` | resolve against the enclosing `[data-band]` |
| `bg-n-04` … | the neutral ramp, by step |
| `border-rule` `border-rule-strong` | the translucent hairlines |
| `shadow-glow-sm/md/lg` `shadow-dot-ring` | emission — inert on paper |
| `h-control-md` `px-control-x-lg` | the density scale |
| `rounded-sm/md/lg` `rounded-pill` | rule 7: structure vs token |
| `max-w-measure` | 68ch |

`ink` rather than `text` because a `--color-text-muted` key would generate
the class `text-text-muted`.

Tailwind's own palette is left switched on, so `bg-red-500` still works. It
is a hue nobody solved and it will not survive greyscale; to remove it and
everything like it, add one line after the import:

```css
@theme { --color-*: initial; }
```

## Extending it

Colours are the output of a constraint solve, not hand-picked. Add a hue by
adding an angle and re-running the solver:

```bash
python3 tools/solve.py ring --exposure editorial
python3 tools/solve.py verify
```
