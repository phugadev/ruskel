# Wavelength — the two-exposure system

**v6 · August 2026**

> Swiss grid, instrument-panel detail, prism colour — exposed two ways.

One grid, one type scale, one spectrum. Two **exposures** of it:

| | Editorial | Luminous |
|---|---|---|
| Ground | paper `#EDEAE3` | ink `#0B0A08` |
| Voice | author | product |
| Colour behaves as | pigment | light |
| Used for | site, writing, case studies, docs, proposals | apps, dashboards, demos, capstones, client UI |

An exposure is not a light/dark theme. A theme recolours a fixed design. An exposure changes what light is *doing*: editorial **marks** with a band — a rule, a chip, a word — while luminous **emits** it, with falloff around the source. Ink and paper swap; the spectrum re-solves for the new ground.

---

## 1. Colour

### 1.1 The correction: four bands were never a palette

The original system had four hand-picked bands. That is a **portfolio taxonomy**, and it cannot dress a product. A real dashboard needs eight or more categorical hues for charts and tags, a status axis, and a neutral chrome ramp. Bolting those on as unrelated colours would have left the wavelength idea as decoration on top of a generic UI palette.

The fix is to stop treating the four bands as the palette and start treating them as **four named positions on a spectrum**. Everything else — chart series, tag colours, accents — is then derived from the same construction rather than bolted on. (How far to extend the ring is answered in §1.4b: further than four for *display*, but not for anything categorical.)

### 1.2 Four layers

| Layer | What | Rule |
|---|---|---|
| **L0 Neutral** | the ink↔paper ramp, 12 steps | all chrome. Carries no hue meaning. |
| **L1 Bands** | the four named wavelengths | subject-matter taxonomy. Aliases onto L2. |
| **L2 Categorical** | the four named bands + a deep stop for each | charts, tags, series |
| **L2b Display** | 550 / 490 / 440 / 370 | spectrum strips and gradients **only** — never categorical |
| **L3 Functional** | 620nm warning, 700nm critical | **reserved** — excluded from L2 |

L3 is excluded from L2 so an alarm can never be mistaken for a category, and carries **elevated chroma** so it outshouts every category. That is the correct hierarchy: a warning must be louder than a classification.

> **Naming note, 0.9.0.** This document describes the *engine* and still says
> "mark ring" and "text ring". Those are now the `solid` and `text` steps of
> an eight-step role scale, and neither is reachable from the public API —
> components read `--rsk-band-solid` and `--rsk-fg-*` instead. The physics
> below is unchanged; only the spelling above it moved. See the README for
> the four tiers, or `docs/system.html` for the whole thing rendered.

### 1.3 Two rings, because colour has two jobs

**This is the correction that made v2 look dull.** v2 held lightness *and* chroma constant across the ring so every hue would carry identical WCAG contrast. That is correct for text and disastrous for everything else, because the **sRGB gamut ceiling is not flat** — it varies about 2.5× by hue at any given lightness. At L=0.65, magenta reaches C=0.309 while cyan tops out at C=0.111. Pinning one chroma for all ten hues pins the whole palette to its weakest member. The ring was living at cyan's ceiling. Hence: mud.

The deeper error was treating one ring as if it had one job. It has two, with opposite requirements:

| | Job | Construction |
|---|---|---|
| **MARK** | fills, bars, dots, glows, solid buttons, borders. Must be **seen**, not read — WCAG text ratios do not apply. | per-hue chroma at **93% of that hue's own sRGB ceiling**. Lightness free in 0.62–0.78. Vivid. |
| **TEXT** | coloured type on a ground. Must be **read**. | chroma and lightness pulled back until it passes AA (4.6:1 on paper, 6.5:1 on ink). |

Same hue angle in both, so they read as one colour.

**The mark ring is shared by both exposures.** A vivid mark is a vivid mark: `#32D885` is the same green on paper and on ink. Only the text ring re-solves per ground. This is also how a real brand palette behaves — brand colours don't change between light and dark, only the type does.

```css
--mk-520: oklch(0.780 0.177 155.6);  /* mark  — shared      */
--tx-520: oklch(0.505 0.111 155.6);  /* text  — on paper    */
--tx-520: oklch(0.650 0.143 155.6);  /* text  — on ink      */
```

**One clean consequence.** Checked across all ten hues, every mark takes near-black text — worst case 4.94:1 at 405nm, the rest 5.0–10.7. So `--on-mark` is ink, always, in both exposures, no per-hue exceptions. Solid buttons, filled chips and legend swatches share one foreground rule.

**Accepted trade-off:** the mark ring is *not* equal-lightness. 590/550/520/490 sit at L≈0.78 while 470/440/405 sit at L≈0.62, because sRGB does not permit a vivid dark yellow or a vivid light blue. Chasing equal lightness there is a fight with the gamut that colour always wins. Lightness stays constant where it matters — within each text ring.

### 1.3b Chips: the other reason v2 looked washed

The v2 chip put coloured text on a tinted background *of the same hue* — two weak signals cancelling each other out. The vivid mark now carries the colour as a **dot**, and the chip's text sits at full `--text` contrast. Crisper, and it survives being shrunk. A `.chip-solid` variant takes the vivid mark as a fill with near-black type, for where the chip itself is the signal rather than a qualifier.

### 1.4 The neutral hue fix

The original neutrals were **inconsistent in hue**: darks sat at H≈270° (cool blue-grey) while paper sat at H≈90° (warm). The two exposures' greys were not the same family — ink mode read blue-screen, paper read warm.

Both are now **H=85, warm**. A warm charcoal is cohesive with paper, and it walks away from the blue-grey every other dev-tool dark mode uses — which is free differentiation in the exact category you're competing in.

### 1.4b The chart ramp is four hues, not eight

An earlier version ran the chart slots through the ring in dispersion order. It looks wonderful as a swatch strip and it is wrong for a chart: the unnamed hues sit *between* the named bands, which is exactly where they collide. Measured as OKLab ΔE:

| Pair | ΔE |
|---|---|
| 470 compute ↔ 440 indigo | **0.078** — effectively the same colour |
| 440 indigo ↔ 405 intelligence | **0.079** — effectively the same colour |
| 590 interface ↔ 550 lime | 0.104 |
| 520 systems ↔ 490 cyan | 0.124 |
| 405 intelligence ↔ 370 magenta | 0.128 |

Every filler was nearly a named band. Adding hues *between* four well-spaced ones cannot work — the gaps are where the confusion lives.

**Fix: four named hues, each with a second much deeper stop.** Worst pair across the whole eight-series set goes from ΔE 0.078 to **0.155**. Semantic bonus: a fifth series reads as a *variant of a band* rather than a new category nobody can name. Past eight series, stop using colour and label directly.

`550 / 490 / 440 / 370` survive as a **display ramp** — spectrum strips, gradients, the dispersion mark, places where adjacency is the point. Never categorical, never meaningful.

**On 520 green specifically:** resolved by removing 550 lime from anything categorical. 520 now only ever competes with deep-520, which differs by 0.28 in lightness — the easiest distinction there is. And green still never means "healthy"; status stays form-only.

### 1.5 Status is not a band

Health and category are different axes and must not share a hue, or 520nm green means both "systems" and "healthy" in one view. Status carries **one** hue and otherwise encodes itself in form:

- **fine** → hollow, `--text-faint`, no colour
- **watch** → ring, no fill
- **critical** → filled `--critical`, glows in luminous

Minimum ink. If everything is green, nothing needs reading.

**Tightest adjacency — fixed in v6.** 590nm interface and 620nm warning were 16° apart, measuring **ΔE 0.054** — tighter than the 0.078 pair this system already rejected for chart series. Interface moved toward yellow (71.3° → **78°**) and warning toward red-orange (55° → **45°**): a 33° gap, ΔE **0.106–0.118**.

That also makes warning and critical read as a severity ramp, which is correct — those two *are* related, and interface is related to neither. Both functional marks are now exposure-invariant: `#FA6E1C` warning and `#FA2033` critical, identical on paper and ink. An alarm is an alarm.

It remains the system's tightest pair. The mitigation is structural rather than chromatic: interface appears as a category chip or rail, warning as a status rail or dot — they never occupy the same slot. If they ever must sit adjacent in one row, label them.

**Mark contrast floor — also v6.** Editorial marks were pinned at exactly 3:1 against paper, which on the warm hues sits well below the chroma peak and cost 9–13% saturation; amber read as brown. The floor is now **2.2:1**, putting 590nm at C 0.140 (was 0.128) and 520nm at C 0.158 (was 0.140). A fill that carries a label does not need 3:1 with the page — only an affordance does. Small marks (6px dots, 2px rails) get a `--dot-ring` hairline instead of a darker hue: a component fix, not a colour one.

---

## 2. Typography

**One sans, one mono.** Two families total.

### 2.1 Sans: Inter, at two optical sizes

Not Geist. Geist is Vercel's house font, and adopting it as your identity face makes your work read as *built by someone using Vercel's defaults* — the precise opposite of the differentiation you're buying. Inter is more ubiquitous but **invisible**, which is what you want: in this system identity is carried by grid and spectrum, and the type's job is to get out of the way. That is also the orthodox Swiss position — Helvetica was chosen for neutrality, not personality.

Rather than pairing a second display face, use Inter's optical-size axis: `font-optical-sizing: auto` plus `-0.022em` tracking at `--text-2xl` and above. One family, two voices, no trend exposure.

### 2.2 Mono: JetBrains Mono, at two scales

Metadata **and** code from one family. Splitting them across two monos is defensible in a larger system but here it just buys a second font load.

Mono is the highest-risk element you own — it is what makes the work read as *engineer* rather than *designer*, and it is the thing most likely to date. Two disciplines keep it honest:

- **Mono is metadata, never content.** Labels, figures, tags, timestamps, state, nm readouts. Uppercase, tracked `0.09em`, never above `--text-xs`. Body copy and headings are never mono.
- **No serif enters this system at any size.**

**Upgrade path, if you want it:** the one paid font worth considering is **Berkeley Mono** (~£60 desktop, webfont extra). It is genuinely distinctive where JetBrains Mono is genuinely common, and swapping only the metadata mono is a one-token change. Not urgent — do it when the system is otherwise settled.

### 2.3 Scale

1.25 minor third, 16px base, `--text-2xs` (0.64rem) through `--text-4xl` (3.05rem). Running text never exceeds `--measure` (68ch).

---

## 3. Building on shadcn

Correct call. shadcn is copy-in source, not a dependency, so "shaping the aesthetics" means editing the token layer and a handful of variants — not rewriting primitives.

### 3.1 The mapping is the whole job

shadcn components only read a fixed set of variable names. `wavelength.css` maps the system onto that contract, so every primitive inherits the house style **without touching component source**:

```
--background --foreground --card --popover --primary --secondary
--muted --accent --destructive --border --input --ring
--chart-1…8 --sidebar-*
```

Two mappings worth defending:

- **`--primary` is `--text`** — ink on paper, paper on ink. An earlier version made it the 590nm amber mark, which was the one place the system broke its own first rule: a button is *chrome*, not something that is *about* interface. Amber also sits 16° from the 620nm warning hue, so an amber primary quietly read as caution. Maximum-contrast ink is also the more Swiss answer — the button is a block of type, not a colour event.
- **`--ring` keeps `--mk-590`.** A focus state is a signal, not chrome.
- **`--destructive` is `--mk-700`,** the reserved alarm hue, never a categorical.

shadcn ships five chart slots. Five is not enough for real dashboards; the mapping extends to eight, in dispersion order, so a multi-series chart is literally a prism.

### 3.2 Three global overrides remove most of the "default shadcn" tell

1. **`--radius: 0.25rem`** (from shadcn's `0.5rem`). The single biggest reason every shadcn app looks alike.
2. **Shadows off, hairlines on.** Depth in editorial comes from rules; in luminous from emission and a raised surface. Never from a blur-heavy shadow.
3. **Warm neutral hue** (§1.4), replacing the default cool slate.

### 3.3 Components that still need a variant

Everything else inherits. These four carry the identity and are worth hand-shaping:

- **Badge** → becomes the band chip (`.chip`): tinted fill, band hairline, band text, glow in luminous.
- **Card** → hairline border, no shadow, near-square.
- **Table** → hairline rules, mono for all figures and timestamps.
- **Separator** → the system's most-used element; make sure it's `--rule`, not shadcn's default border.

---

## 4. The rules

1. **A band never appears decoratively.** If something is amber, it is *about* interface. Corollary: page chrome uses no band at all.
2. **Status is not a band.** §1.5.
3. **Components don't know their exposure.** Style against token names, never values. Emission tokens exist in both exposures and resolve to `none` on paper, so `box-shadow: var(--glow-sm)` is written unconditionally. A component needing a `[data-exposure]` override is a bug in the tokens.
4. **Adding a hue means adding an angle**, never a hand-picked colour. Then solve it for both rings.
4b. **Never use a text-ring value as a fill, or a mark value as body type.** That swap is exactly what made v2 look muddy in one direction and would fail AA in the other.
5. **Mono is metadata, never content.** §2.2.
6. **Numbering must encode order.** `01 / EXPERTISE` is legitimate only where sequence carries information. Unordered peers get a hairline and a label. Decorative numbering is the fastest route to looking like every other technical portfolio.
7. **Geometry is near-square.** Radii 2/4/6px. No pills except status dots.
8. **Spend boldness once per view.** One luminous moment per screen. Two competing glows read as a template.
9. **Colour is never the only carrier.** Every chip carries its nm figure or name. The system must survive being printed in greyscale by a hiring manager.

---

## 5. Which exposure, when

- **Editorial by default for anything read** — site, writing, case studies, proposals. Its restraint is the credibility argument.
- **Luminous for anything operated** — product UI, dashboards, capstone demos, client app work.
- A case study that *contains* a product screenshot is editorial with a luminous plate inside it. That composition is the best demonstration of the system: it shows both voices belong to the same author.

---

## Files

- `wavelength.css` — tokens, shadcn mapping, primitives. Drop-in.
- Migration note: this **supersedes** `lib/palette.ts`. The v1 luminous exposure reproduced it verbatim; v2 regularises it onto the ring, which moves every value slightly and 470nm/405nm noticeably. That is the point — but it is a repaint, not a patch.
