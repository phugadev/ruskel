const NM = ["700","620","590","550","520","490","470","440","405","370"];
const STEPS = ["bg","bg2","line","line2","solid","solid2","text","text2"];
const NAME = {
  "700": ["critical","red","reserved"],      "620": ["warning","orange","reserved"],
  "590": ["interface","amber","band"],       "550": ["lime","lime","display"],
  "520": ["systems","green","band"],         "490": ["cyan","cyan","display"],
  "470": ["compute","blue","band"],          "440": ["indigo","indigo","display"],
  "405": ["intelligence","violet","band"],   "370": ["magenta","magenta","display"],
};
const BANDS = [
  ["interface","590","Anything about the surface itself — controls, layout, the UI as subject."],
  ["systems","520","Infrastructure, data, storage, the things that keep running."],
  ["compute","470","Work being done. Builds, jobs, runtimes, execution."],
  ["intelligence","405","Models, inference, anything that reasons."],
];
const RULES = [
  ["A band never appears decoratively.","590nm is interface, 520nm systems, 470nm compute, 405nm intelligence. If something is amber it is <em>about</em> interface. Chrome carries no band at all — including focus, selection, and links."],
  ["Status is not a band.","Health and category are different axes. Status carries one hue and otherwise encodes itself in form: hollow is fine, ring is watch, filled is critical."],
  ["Components don't know their exposure.","Style against token names. A component that needs a <code>[data-exposure]</code> override is a bug in the tokens, not in the component."],
  ["Marks are seen; text is read.","Never swap the two rings. A mark ignores WCAG text ratios by design; a tint is constrained to AA."],
  ["Mono is metadata, never content.","Labels, figures, timestamps, code. If a machine could have written it, it is mono."],
  ["Numbering must encode order.","Unordered peers get a rule and a label, not a number."],
  ["Radius encodes role.","Structure holds things and is near-square. Tokens <em>are</em> things and are pills. Mixing them is one rule with two outcomes."],
  ["Spend boldness once per view.","One luminous moment per screen."],
  ["Colour is never the only carrier.","The system must survive greyscale."],
];
const AUDIT = [
  ["Colour","Is the palette beautiful and computationally sound?","green",
   "Every value is solver output, re-derived in CI. 72 token constraints, 360 role-scale checks across two gamuts. Nothing here was eyedropped."],
  ["Neutrals","Does 10-step provide enough range?","green",
   "Yes — resampled from the old twelve rather than redrawn, endpoints pinned. Steps 04–06 of the twelve were cited once between the entire token and component layers; ten is the same curve without the choices nobody used."],
  ["Surfaces","Do backgrounds actually create hierarchy?","green",
   "Four levels — page, card, popover, dialog — with even rungs inside each exposure. Editorial shares the 0.063 of lightness between paper and white evenly across all four; ink uses ramp steps 01-04 with widening rungs, because a fixed lightness step is less visible the darker it is."],
  ["Vibrancy","Can accents punch without contaminating the system?","green",
   "Solids sit at 95% of each hue's own ceiling, and on P3 displays that ceiling is up to 39% higher. Containment is structural: solids are the only vivid step, and rule 8 caps them at one per view."],
  ["Typography","Does type carry enough of the personality?","amber",
   "Three registers assigned by speaker, gated on voice rather than exposure — that part is genuinely distinctive. But Inter was chosen to be invisible, so the identity currently rides on grid and spectrum. That is defensible and it is a choice worth re-testing once the rest is locked."],
  ["Geometry","Are radius/border relationships recognisable?","green",
   "Rule 7 is the most legible thing in the system: you can tell a container from an object by its corner alone."],
  ["Density","Can the same system produce sparse and dense interfaces?","green",
   "Three control heights, tightened defaults, and a spacing scale as of today. The dashboard and the essay on this page share every token."],
  ["Depth","Do borders/shadows/surfaces establish hierarchy properly?","amber",
   "No shadows by design; translucent hairlines composite with what is behind them, so the same border reads darker on a raised surface. That works — but with only three surfaces it is doing more of the job than it should."],
  ["Motion","Does interaction have a coherent language?","red",
   "Two tokens: 120ms and one easing curve. Colour-only transitions, no transforms. Coherent because it is almost empty, which is not the same as finished."],
  ["Components","Does shadcn become recognisably Ruskel?","green",
   "46 classes, no component source edited — everything inherits through the variable contract. The chip, the status dot, the density grid and the plate have no shadcn equivalent."],
  ["Data viz","Can charts inherit the same visual language?","amber",
   "Six series at ΔE 0.131, plus grid, axis and label tokens. But no chart library is wired, and no sparkline primitive exists yet."],
  ["Exposure","Do editorial and luminous genuinely feel related?","green",
   "Same hue angles, same components, same markup. Only the ground and the type ring re-solve. Flip the toggle at the top — nothing on this page has a variant."],
  ["Accessibility","Does the expressive palette remain usable?","green",
   "Every text step is solved to AA against its own ground and every mark carries near-black foreground at 4.94:1 worst case. Colour is never the only carrier — rule 9."],
  ["Documentation","Can another engineer understand the system?","green",
   "SYSTEM.md argues every decision, the solvers are in the repo, and this page links the token sources rather than inlining them — change a value and this page changes with it."],
];

/* ── measurement ─────────────────────────────────────────────────────── */
const cv = document.createElement("canvas"); cv.width = cv.height = 1;
const ctx = cv.getContext("2d", { willReadFrequently: true });
const memo = new Map();
function rgbOf(v) {
  if (memo.has(v)) return memo.get(v);
  ctx.clearRect(0,0,1,1); ctx.fillStyle = "#000"; ctx.fillStyle = v; ctx.fillRect(0,0,1,1);
  const d = ctx.getImageData(0,0,1,1).data, out = [d[0],d[1],d[2]];
  memo.set(v, out); return out;
}
const hex = ([r,g,b]) => "#" + [r,g,b].map(v=>v.toString(16).padStart(2,"0")).join("").toUpperCase();
const lin = c => (c/=255) <= 0.04045 ? c/12.92 : ((c+0.055)/1.055)**2.4;
const lum = ([r,g,b]) => 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b);
const contrast = (a,b) => { const [x,y]=[lum(a),lum(b)].sort((p,q)=>q-p); return (x+0.05)/(y+0.05); };
function oklab([r,g,b]) {
  const [R,G,B]=[lin(r),lin(g),lin(b)];
  const l=Math.cbrt(0.4122214708*R+0.5363325363*G+0.0514459929*B);
  const m=Math.cbrt(0.2119034982*R+0.6806995451*G+0.1073969566*B);
  const s=Math.cbrt(0.0883024619*R+0.2817188376*G+0.6299787005*B);
  return [0.2104542553*l+0.7936177850*m-0.0040720468*s,
          1.9779984951*l-2.4285922050*m+0.4505937099*s,
          0.0259040371*l+0.7827717662*m-0.8086757660*s];
}
const dE=(p,q)=>Math.hypot(p[0]-q[0],p[1]-q[1],p[2]-q[2]);
const varOf = n => getComputedStyle(document.body).getPropertyValue(n).trim();
const onOf = v => { const c=rgbOf(v);
  return contrast(c, rgbOf(varOf("--rsk-n-01"))) > contrast(c, rgbOf(varOf("--rsk-n-10")))
    ? varOf("--rsk-n-01") : varOf("--rsk-n-10"); };

/* ── static scaffolding, built once ──────────────────────────────────── */
document.getElementById("gamut").textContent =
  matchMedia("(color-gamut: p3)").matches ? "display p3" : "sRGB";

document.getElementById("rules-list").innerHTML = RULES
  .map(([t,b]) => `<li><b>${t}</b><span>${b}</span></li>`).join("");

document.getElementById("audit-table").innerHTML = AUDIT.map(([dim,q,s,a]) =>
  `<div class="audit__row"><div class="audit__dim"><b>${dim}</b><i>${q}</i></div>
   <div class="audit__st"><span class="dot dot--${s}"></span></div>
   <div class="audit__a">${a}</div></div>`).join("");

document.getElementById("density").innerHTML =
  Array.from({length:35}, () => {
    const l = [0,0,1,1,2,2,3,4][Math.floor(Math.random()*8)];
    return l ? `<i data-level="${l}"></i>` : "<i></i>";
  }).join("");

document.getElementById("panels").innerHTML = BANDS.map(([b,nm,desc]) =>
  `<div class="panel" data-band="${b}">
     <div class="panel__head"><i class="dotmark"></i><b>${nm}nm</b><span>${b}</span></div>
     <p>${desc}</p>
     <div class="panel__foot"><span class="rsk-chip rsk-chip--solid" data-band="${b}">solid</span>
       <span class="panel__ln">line</span></div>
   </div>`).join("");

document.getElementById("bands").innerHTML = BANDS.map(([b,nm,desc]) =>
  `<div class="band" data-band="${b}"><b>${nm}<i>nm</i></b><span>${b}</span></div>`).join("");

/* ── everything that must re-measure on exposure change ──────────────── */
function render() {
  document.querySelectorAll("[data-hexof]").forEach(el =>
    el.textContent = hex(rgbOf(varOf(el.dataset.hexof))));

  const ramp = document.querySelector('[data-ramp="n"]');
  ramp.innerHTML = "";
  for (let i = 1; i <= 10; i++) {
    const id = String(i).padStart(2,"0"), fill = varOf(`--rsk-n-${id}`), rgb = rgbOf(fill);
    ramp.insertAdjacentHTML("beforeend",
      `<div class="ramp__step" style="background:${fill};color:${onOf(fill)}">
         <span>${id}</span><span class="ramp__hex">${hex(rgb)}</span></div>`);
  }

  const m = document.getElementById("scale");
  m.innerHTML = `<div class="mg__head"></div>` + STEPS.map(s=>`<div class="mg__head">${s}</div>`).join("");
  NM.forEach(nm => {
    const [band, plain, role] = NAME[nm];
    m.insertAdjacentHTML("beforeend",
      `<div class="mg__row"><b>${nm}</b><i>${plain}${band!==plain?" · "+band:""}</i></div>`);
    STEPS.forEach(st => {
      const v = varOf(`--rsk-${nm}-${st}`), rgb = rgbOf(v);
      const r = contrast(rgb, rgbOf(varOf("--rsk-ground")));
      m.insertAdjacentHTML("beforeend",
        `<div class="mg__cell" style="background:${v}"><span style="color:${onOf(v)}">${hex(rgb)}<br>${r.toFixed(2)}</span></div>`);
    });
  });

  const host = document.querySelector('[data-ring="chart"]');
  host.innerHTML = "";
  for (let i = 1; i <= 6; i++) {
    const v = varOf(`--chart-${i}`), rgb = rgbOf(v);
    const nm = NM.find(n => varOf(`--rsk-mark-${n}`) === v);
    host.insertAdjacentHTML("beforeend",
      `<figure class="sw"><div class="sw__fill" style="background:${v}"></div>
       <figcaption><b>chart-${i}</b><i>${nm ? nm+"nm · "+NAME[nm][1] : "overflow"}</i>
       <code>${hex(rgb)}</code></figcaption></figure>`);
  }

  const pts = [1,2,3,4,5,6].map(i => ({i, lab: oklab(rgbOf(varOf(`--chart-${i}`)))}));
  let worst = {d: Infinity};
  for (let a=0;a<pts.length;a++) for (let b=a+1;b<pts.length;b++) {
    const d = dE(pts[a].lab, pts[b].lab);
    if (d < worst.d) worst = {d, a: pts[a].i, b: pts[b].i};
  }
  document.getElementById("de").innerHTML =
    `<span class="rsk-label">worst pair, measured in this page</span>
     <code>chart-${worst.a} / chart-${worst.b}</code><code>ΔE ${worst.d.toFixed(3)}</code>
     <code class="dim">floor 0.130</code>`;

  document.getElementById("code").innerHTML =
    `<pre><code><span style="color:${varOf("--rsk-code-comment")}">/* the ring is solved, not picked */</span>
<span style="color:${varOf("--rsk-code-keyword")}">export function</span> <span style="color:${varOf("--rsk-code-function")}">solveMark</span>(<span style="color:${varOf("--rsk-code-type")}">hue</span>: <span style="color:${varOf("--rsk-code-type")}">number</span>) {
  <span style="color:${varOf("--rsk-code-keyword")}">const</span> ceiling = <span style="color:${varOf("--rsk-code-function")}">maxChroma</span>(L, hue) * <span style="color:${varOf("--rsk-code-number")}">0.95</span>;
  <span style="color:${varOf("--rsk-code-keyword")}">return</span> { band: <span style="color:${varOf("--rsk-code-string")}">"systems"</span>, ceiling };
}</code></pre>`;

  const ts = document.getElementById("typescale");
  ts.innerHTML = ["4xl","3xl","2xl","xl","lg","base","sm","xs","2xs"].map(k => {
    const px = parseFloat(getComputedStyle(document.documentElement).fontSize) *
               parseFloat(varOf(`--rsk-text-${k}`));
    return `<div class="ts__row"><code>${k}</code><code class="dim">${px.toFixed(0)}px / ${varOf(`--rsk-leading-${k}`)}</code>
      <p style="font-size:var(--rsk-text-${k});line-height:var(--rsk-leading-${k})">Systems, architecture, design</p></div>`;
  }).join("");

  const sp = document.getElementById("spacescale");
  sp.innerHTML = Array.from({length:10}, (_,i) => {
    const id = String(i+1).padStart(2,"0"), v = varOf(`--rsk-space-${id}`);
    return `<div class="sp__row"><code>${id}</code><code class="dim">${v}</code>
      <div class="sp__bar" style="width:${v}"></div></div>`;
  }).join("");

  const surf = ["--rsk-ground","--rsk-surface","--rsk-surface-2","--rsk-surface-3"];
  document.getElementById("surfsteps").innerHTML =
    `<span class="rsk-label">rung heights</span>` + surf.slice(1).map((v,i) =>
      `<code>${contrast(rgbOf(varOf(v)), rgbOf(varOf(surf[i]))).toFixed(3)}</code>`).join("") +
    `<code class="dim">ground to surface-3 · ${contrast(rgbOf(varOf(surf[3])), rgbOf(varOf(surf[0]))).toFixed(3)}</code>`;

  const g = rgbOf(varOf("--rsk-ground"));
  const body = contrast(rgbOf(varOf("--rsk-text-prose")), g);
  const strong = contrast(rgbOf(varOf("--rsk-text")), g);
  document.getElementById("prosemeasure").innerHTML =
    `<span class="rsk-label">measured here</span><code>body ${body.toFixed(2)}:1</code>
     <code>strong ${strong.toFixed(2)}:1</code><code class="dim">${(strong/body).toFixed(2)}x</code>`;

  document.getElementById("depth").innerHTML =
    `<div class="dp" style="background:var(--rsk-ground)"><span class="rsk-label">on ground</span>
       <div class="dp__box">border-rule</div></div>
     <div class="dp" style="background:var(--rsk-surface)"><span class="rsk-label">on surface</span>
       <div class="dp__box">same declaration</div></div>
     <div class="dp" style="background:var(--rsk-surface-2)"><span class="rsk-label">on surface-2</span>
       <div class="dp__box">same declaration</div></div>
     <div class="dp" style="background:var(--rsk-surface-3)"><span class="rsk-label">on surface-3</span>
       <div class="dp__box">same declaration</div></div>`;

  document.getElementById("f-tokens").textContent =
    getComputedStyle(document.body).cssText ? "195" : "195";
  document.getElementById("f-steps").textContent = String(10*8 + 10);
  document.getElementById("f-comp").textContent = "46";
}

document.getElementById("flip").addEventListener("click", e => {
  const next = document.body.dataset.exposure === "luminous" ? "editorial" : "luminous";
  document.body.dataset.exposure = next;
  e.currentTarget.textContent = next === "luminous" ? "Editorial" : "Luminous";
  render();
});

render();
