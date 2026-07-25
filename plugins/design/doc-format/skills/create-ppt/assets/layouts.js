// layouts.js — theme-parameterized layout library for the code-native deck skill.
//
// Ported and generalized from a reading-deck reference implementation. Each layout is
// a pure function `fn(pres, T, ctx, c)`:
//   pres  pptxgenjs presentation (layout already set to LAYOUT_WIDE by render.js)
//   T     a theme token object from themes.js
//   ctx   per-deck build state (currently { pageNo })
//   c     the slide's content object (from content.js) — pure data, keyed to slots
//
// Design contract carried over from the source system:
//   - Talking headers: every content header is a full-sentence finding, <=2 lines.
//   - Single-emphasis (Mode 1): exactly ONE accent-colored mark per slide; everything
//     else neutral. Charts, stat rows, tables, milestone/step lines obey this.
//   - Category palette (Mode 2): multi-identity diagrams (timeline lanes, architecture,
//     roadmap) use T.cat — flat tint fill, no outline, label inside in the category color.
//   - Sources: any slide presenting data should carry c.source (a bottom-left footnote);
//     a terminal `sources` bibliography slide collects the full list.
//   - Prevention-first overflow: item lists are CLAMPED to what the geometry holds, and
//     bar/card heights are computed from item count — the layout cannot overflow the frame.
//
// Fonts: family+bold for base families; STATIC named faces (T.serif, T.displayMedium,
// T.bodyMedium) for the serif + Medium tiers — these resolve by face string under LibreOffice.

const path = require("path");

const W = 13.333, H = 7.5, M = 0.85;
const COVERS_DIR = path.join(__dirname, "covers");

// ---------- small helpers ----------

// Clamp a list to the max the layout can hold without overflowing.
// WARNS when it drops items — silent truncation would let content (including source
// citations) vanish from the deck while the build exits clean.
const clamp = (arr, n) => {
  if (!Array.isArray(arr)) return [];
  if (arr.length > n) {
    console.warn(`layouts WARNING: clamped ${arr.length} → ${n} items; ${arr.length - n} DROPPED from the deck. Trim content.js to fit the layout.`);
  }
  return arr.slice(0, n);
};

// Relative luminance of a hex color (0..1). Used to pick readable text on any fill,
// replacing the source's hardcoded dark-background allowlist.
function luminance(hex) {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  const lin = (v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}
// Readable text color on a given fill: theme ink for light fills, white for dark.
const onFill = (bgHex, T) => (luminance(bgHex) > 0.5 ? T.ink : "FFFFFF");

// Round a value UP to a clean axis maximum (1/2/4/5/10 × 10^k) so quarter gridlines land on
// numbers a reader can name (25/50/75/100) instead of on quarters of the tallest bar.
// Restricted to 1,2,4,5,10 precisely so the quarters stay clean.
function niceCeil(v) {
  const p = Math.pow(10, Math.floor(Math.log10(Math.max(1, v))));
  const r = v / p;
  const m = r <= 1 ? 1 : r <= 2 ? 2 : r <= 4 ? 4 : r <= 5 ? 5 : 10;
  return m * p;
}

// New slide. Content slides get a SHORT accent tick top-left (brand marker) + page number.
// A full-width top stripe reads as generated furniture; a short corner tick keeps the clean
// top margin the reading-deck aesthetic depends on.
function slide(pres, T, ctx, opts = {}) {
  const { footer = true, topBar = true } = opts;
  const s = pres.addSlide();
  s.background = { color: T.paper };
  if (topBar) {
    s.addShape("rect", { x: 0, y: 0, w: 1.35, h: 0.09, fill: { color: T.accent }, line: { type: "none" } });
  }
  if (footer) {
    ctx.pageNo += 1;
    s.addText(String(ctx.pageNo), {
      x: W - M - 1.0, y: 7.08, w: 1.0, h: 0.3, align: "right",
      fontFace: T.body, fontSize: 9.5, color: T.muted, margin: 0,
    });
    // Deck-level confidentiality marker. Set `confidential: true` (or a custom string) at the TOP
    // level of content.js and every content slide carries it — a per-slide flag would inevitably
    // be forgotten on the one slide that mattered. Sits right of the source note and left of the
    // page number, in the same muted footer tier so it reads as chrome, not as content.
    if (ctx.confidential) {
      s.addText(String(ctx.confidential === true ? "CONFIDENTIAL" : ctx.confidential).toUpperCase(), {
        x: W - M - 3.6, y: 7.08, w: 2.5, h: 0.3, align: "right",
        fontFace: T.body, bold: true, fontSize: 8, color: T.muted, charSpacing: 1.2, margin: 0,
      });
    }
  }
  return s;
}

// Talking-header block: optional kicker, the finding header, optional subtitle.
function headerBlock(s, T, c, opts = {}) {
  const hw = opts.w || (W - 2 * M);
  let y = 0.55;
  if (c.kicker) {
    s.addText(String(c.kicker).toUpperCase(), {
      x: M, y, w: hw, h: 0.3, fontFace: T.body, bold: true, fontSize: 10,
      color: T.accentText, charSpacing: 3, margin: 0,
    });
    y += 0.38;
  }
  s.addText(c.header || "", {
    x: M, y, w: hw, h: opts.hh || 1.1, fontFace: T.display, bold: true,
    fontSize: opts.hs || 23, color: T.ink, margin: 0, lineSpacingMultiple: 1.18, valign: "top",
  });
  y += (opts.hh || 1.1) + 0.08;
  if (c.sub) {
    s.addText(c.sub, {
      x: M, y, w: opts.sw || hw - 1.2, h: opts.sh || 0.6, fontFace: T.body,
      fontSize: 13, color: T.sec, margin: 0, lineSpacingMultiple: 1.35, valign: "top",
    });
  }
}

// Bottom-left source footnote (data provenance). No-op when absent.
function sourceNote(s, T, text) {
  if (!text) return;
  s.addText(`Source: ${text}`, {
    x: M, y: 7.08, w: 9.6, h: 0.3, fontFace: T.body, fontSize: 8.5, color: T.muted, margin: 0,
  });
}

// Draw a straight segment between two arbitrary points.
//
// OOXML shape extents MUST be non-negative. A line emitted with a negative cx/cy makes
// PowerPoint declare the file corrupt and offer to "repair" it — and after repairing, it
// clamps the segment flat, so every rising line in a chart renders horizontal.
//
// LibreOffice silently normalises the same XML, which is why PDF-based QA never caught this:
// the exported PDF looked correct while the .pptx it came from was malformed. Any layout
// drawing a sloped line MUST go through this helper, never `addShape("line")` with a computed
// h that can go negative.
function seg(s, x1, y1, x2, y2, line) {
  const o = {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), line,
  };
  // The `line` preset runs corner-to-corner. When dx and dy have opposite signs the segment
  // needs the other diagonal of the same box, which is a vertical flip.
  if ((x2 - x1) * (y2 - y1) < 0) o.flipV = true;
  s.addShape("line", o);
}

// Fixed-order category color pairs for Mode-2 diagrams.
const { CAT_ORDER } = require("./themes.js");
const catAt = (T, i) => T.cat[CAT_ORDER[i % CAT_ORDER.length]];

// ============================================================
// LAYOUTS
// ============================================================

// 1 · COVER — image-backed brand cover. Title ends in the accent full stop; kicker above.
// The theme's cover config sets the background image and text placement: align "left"
// (plain gradient, title left) or "right" (title clears a baked-in brand mark).
// content: { title, accentStop=true, kicker, subtitle, footnote }
function cover(pres, T, ctx, c) {
  const s = slide(pres, T, ctx, { footer: false, topBar: false });
  const cv = T.cover || {};
  const img = !!cv.bg;
  if (img) {
    s.background = { color: T.band };
    s.addImage({ path: path.join(COVERS_DIR, cv.bg), x: 0, y: 0, w: W, h: H });
  }
  const ink = img ? (cv.ink || "FFFFFF") : T.ink;
  const stopColor = img ? (cv.eyebrow || "FFFFFF") : T.accentText;
  const eyebrow = img ? (cv.eyebrow || "FFFFFF") : T.accentText;
  const right = cv.align === "right";
  const bx = right ? 5.55 : M - 0.03;
  const bw = right ? W - 5.55 - 0.55 : 11.6;
  const al = right ? "right" : "left";
  // Vertical anchor: right-aligned covers sit in the right column (clear of a left-side
  // mark); left covers sit mid-upper. Length-aware size so a long title never overflows.
  // Right-column covers run smaller since the column is narrower.
  const tLen = (c.title || "").length;
  const tSize = right
    ? (tLen > 40 ? 28 : tLen > 24 ? 34 : 40)
    : (tLen > 48 ? 40 : tLen > 30 ? 48 : 56);
  const eyeY = right ? 3.55 : 1.95;
  const titleY = right ? 3.95 : 2.1;
  const subY = right ? 6.15 : 4.75;

  if (c.kicker) {
    s.addText(String(c.kicker).toUpperCase(), {
      x: bx, y: eyeY, w: bw, h: 0.35, align: al, fontFace: T.body, bold: true, fontSize: 11,
      color: eyebrow, charSpacing: 4, margin: 0,
    });
  }
  const title = c.accentStop === false
    ? [{ text: c.title || "", options: { color: ink } }]
    : [{ text: c.title || "", options: { color: ink } }, { text: ".", options: { color: stopColor } }];
  s.addText(title, {
    x: bx, y: titleY, w: bw, h: 1.9, align: al, fontFace: T.serif,
    fontSize: tSize, margin: 0, lineSpacingMultiple: 1.08, valign: "top",
  });
  if (c.subtitle) {
    s.addText(c.subtitle, {
      x: right ? bx : M, y: subY, w: right ? bw : 9.0, h: 0.7, align: al,
      fontFace: T.body, fontSize: right ? 12 : 15, color: img ? (cv.ink || "FFFFFF") : T.sec,
      margin: 0, lineSpacingMultiple: 1.4,
    });
  }
  if (!img) {
    s.addShape("line", { x: M, y: 6.5, w: 3.2, h: 0, line: { color: T.hair, width: 1 } });
    if (c.footnote) s.addText(c.footnote, { x: M, y: 6.65, w: 9, h: 0.35, fontFace: T.body, fontSize: 10.5, color: T.muted, margin: 0 });
  } else if (c.footnote) {
    // Branded (image) covers keep the confidentiality / synthetic-disclaimer line too —
    // previously it only rendered on plain covers and silently vanished on the real brand cover.
    s.addText(c.footnote, { x: bx, y: 6.95, w: bw, h: 0.3, align: al, fontFace: T.body, fontSize: 9.5, color: cv.ink || "FFFFFF", margin: 0 });
  }
  s.addNotes(c.notes || "");
  return s;
}

// 2 · SECTION DIVIDER — accent part label, hairline, section as a talking header.
// content: { part, header }
function sectionDivider(pres, T, ctx, c) {
  const s = slide(pres, T, ctx, { topBar: false });
  if (c.part) {
    s.addText(String(c.part).toUpperCase(), {
      x: M, y: 2.45, w: 5, h: 0.4, fontFace: T.body, bold: true, fontSize: 12,
      color: T.accentText, charSpacing: 5, margin: 0,
    });
  }
  s.addShape("line", { x: M, y: 3.0, w: 11.6, h: 0, line: { color: T.ink, width: 1.25 } });
  s.addText(c.header || "", {
    x: M, y: 3.3, w: 11.4, h: 1.9, fontFace: T.serif, fontSize: 33,
    color: T.ink, margin: 0, lineSpacingMultiple: 1.18, valign: "top",
  });
  s.addNotes(c.notes || "");
  return s;
}

// 3 · CONTENT COLUMNS — up to 3 flat columns: hairline, accent number, head, body.
// content: { kicker, header, sub, columns:[{n,title,body}] }  (clamped to 3)
function contentColumns(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  const cols = clamp(c.columns, 3);
  cols.forEach((col, i) => {
    const cw = 3.65, gap = 0.35, x = M + i * (cw + gap), y = 2.82;
    s.addShape("line", { x, y, w: cw, h: 0, line: { color: T.ink, width: 1.5 } });
    s.addText(col.n || String(i + 1).padStart(2, "0"), {
      // Body face, NOT serif: LibreOffice misplaces repeated static-serif text boxes during
      // PDF export (v1.6 QA finding) — so the index earns its size from scale instead.
      // 26pt (was 17, which matched the title and read as a label, not an index).
      x, y: y + 0.18, w: 1.4, h: 0.55, fontFace: T.body, bold: true, fontSize: 26, color: T.accentText, margin: 0,
    });
    s.addText(col.title || "", {
      x, y: y + 0.92, w: cw, h: 0.45, fontFace: T.display, bold: true, fontSize: 17, color: T.ink, margin: 0,
    });
    s.addText(col.body || "", {
      x, y: y + 1.48, w: cw - 0.15, h: 2.56, fontFace: T.body, fontSize: 12, color: T.sec,
      margin: 0, lineSpacingMultiple: 1.45, valign: "top",
    });
  });
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 4 · COMPARISON — weaker option flat on surface (muted); stronger inside an ink keyline.
// content: { kicker, header, sub, weak:{label,title,body}, strong:{label,title,body} }
function comparison(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  const by = 2.85, bh = 3.5, bw = 5.6;
  const wk = c.weak || {}, st = c.strong || {};
  // weaker — SAME face and size as the strong title: only color, fill and the keyline carry
  // the hierarchy. The old serif-vs-sans mismatch across the two panels read as two different
  // slides sharing a frame rather than one comparison (v1.9 sleek pass).
  s.addShape("rect", { x: M, y: by, w: bw, h: bh, fill: { color: T.surface }, line: { type: "none" } });
  s.addText(String(wk.label || "Before").toUpperCase(), {
    x: M + 0.45, y: by + 0.38, w: 3, h: 0.3, fontFace: T.body, bold: true, fontSize: 9.5, color: T.muted, charSpacing: 2, margin: 0,
  });
  s.addText(wk.title || "", {
    x: M + 0.45, y: by + 0.82, w: bw - 0.9, h: 0.9, fontFace: T.display, bold: true, fontSize: 18, color: T.muted, margin: 0, lineSpacingMultiple: 1.2, valign: "top",
  });
  s.addText(wk.body || "", {
    x: M + 0.45, y: by + 1.7, w: bw - 0.9, h: 1.6, fontFace: T.body, fontSize: 12, color: T.muted, margin: 0, lineSpacingMultiple: 1.45, valign: "top",
  });
  // stronger
  const ax = M + bw + 0.4;
  s.addShape("rect", { x: ax, y: by, w: bw, h: bh, fill: { color: T.paper }, line: { color: T.ink, width: 1.25 } });
  s.addText(String(st.label || "After").toUpperCase(), {
    x: ax + 0.45, y: by + 0.38, w: 3, h: 0.3, fontFace: T.body, bold: true, fontSize: 9.5, color: T.accentText, charSpacing: 2, margin: 0,
  });
  s.addText(st.title || "", {
    x: ax + 0.45, y: by + 0.82, w: bw - 0.9, h: 0.9, fontFace: T.display, bold: true, fontSize: 18, color: T.ink, margin: 0, lineSpacingMultiple: 1.2, valign: "top",
  });
  s.addText(st.body || "", {
    x: ax + 0.45, y: by + 1.7, w: bw - 0.9, h: 1.6, fontFace: T.body, fontSize: 12, color: T.sec, margin: 0, lineSpacingMultiple: 1.45, valign: "top",
  });
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 5 · NUMBERED CHALLENGES — each risk paired with its response on one line.
// content: { kicker, header, sub, leftLabel, rightLabel, items:[{challenge,response}] } (clamp 3)
function numberedChallenges(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  s.addText(String(c.leftLabel || "Potential challenge").toUpperCase(), {
    x: M + 1.15, y: 2.68, w: 4, h: 0.3, fontFace: T.body, bold: true, fontSize: 8.5, color: T.muted, charSpacing: 2, margin: 0,
  });
  s.addText(String(c.rightLabel || "How we respond").toUpperCase(), {
    x: M + 6.6, y: 2.68, w: 4, h: 0.3, fontFace: T.body, bold: true, fontSize: 8.5, color: T.muted, charSpacing: 2, margin: 0,
  });
  const items = clamp(c.items, 3);
  items.forEach((it, i) => {
    const y = 3.08 + i * 1.24;
    s.addText(String(i + 1).padStart(2, "0"), {
      x: M, y: y - 0.02, w: 0.9, h: 1.0, fontFace: T.serif, fontSize: 27, color: T.accentText, margin: 0, valign: "middle",
    });
    s.addText(it.challenge || "", {
      x: M + 1.15, y: y + 0.05, w: 4.85, h: 1.0, fontFace: T.bodyMedium, fontSize: 12.5, color: T.ink, margin: 0, lineSpacingMultiple: 1.32,
    });
    s.addText(it.response || "", {
      x: M + 6.6, y: y + 0.05, w: 5.0, h: 1.0, fontFace: T.body, fontSize: 11.5, color: T.sec, margin: 0, lineSpacingMultiple: 1.32,
    });
    if (i < items.length - 1) s.addShape("line", { x: M, y: y + 1.02, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } });
  });
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 6 · CHART + TAKEAWAY — ARGUMENT rail left, EVIDENCE right, takeaway band beneath.
// The proportions carry the point: in a consulting exhibit the argument is the subject and
// the chart is the evidence, so the plot is sized as evidence (~1.85in tall, ~49% width,
// 1.05in bar cap) and the left rail carries the stat, its label, AND a short reading of
// the chart. Depth is layered, not colored — ink cap rule over the stat, hairline sub-rule
// over the reading, small-caps micro-labels, T.bar leader ticks.
// Emphasis budget: the ONE accent is the hot bar (and its own value label). The rail is
// ink/sec/muted/bar only. The takeaway band uses T.band, a separate role, not the accent.
// content: { kicker, header, sub, statValue, statLabel,
//            reads:[str], readsLabel,      // optional — the left-hand reading (clamp 3, ≤10 words each)
//            chartLabel,                   // optional — small-caps unit label over the plot
//            bars:[{label,value,hot}], takeaway, source }   (bars clamp 6)
function chartTakeaway(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  // ---- left rail: the argument -------------------------------------------------------
  // Flows top-down from a single cursor so the rail composes with or without any part
  // (stat only, reads only, both) instead of relying on fixed slots.
  const LX = M, LW = 4.25;
  const reads = clamp(c.reads, 3);
  let ly = 2.82;
  s.addShape("line", { x: LX, y: ly, w: LW, h: 0, line: { color: T.ink, width: 1.5 } });
  ly += 0.16;
  if (c.statValue) {
    const sv = String(c.statValue);
    // Two ramps: the stat gives up size when it has to share the rail with a reading.
    const statSize = reads.length
      ? (sv.length > 5 ? 38 : sv.length > 4 ? 44 : 50)
      : (sv.length > 5 ? 46 : sv.length > 4 ? 54 : 62);
    const statH = reads.length ? 0.86 : 1.15;
    s.addText(sv, {
      x: LX, y: ly, w: LW, h: statH, fontFace: T.body, bold: true,
      fontSize: statSize, color: T.ink, margin: 0, valign: "top",
    });
    ly += statH;
    if (c.statLabel) {
      s.addText(c.statLabel, {
        x: LX, y: ly, w: LW - 0.3, h: reads.length ? 0.54 : 0.95, fontFace: T.bodyMedium,
        fontSize: 12, color: T.sec, margin: 0, lineSpacingMultiple: 1.4, valign: "top",
      });
      ly += reads.length ? 0.58 : 1.0;
    }
  }
  if (reads.length) {
    s.addShape("line", { x: LX, y: ly, w: LW, h: 0, line: { color: T.hair, width: 0.75 } });
    ly += 0.14;
    s.addText(String(c.readsLabel || "What this means").toUpperCase(), {
      x: LX, y: ly, w: LW, h: 0.26, fontFace: T.body, bold: true, fontSize: 8.5,
      color: T.muted, charSpacing: 2, margin: 0,
    });
    ly += 0.30;
    // Prevention-first: row height is computed from item count against the band top, so
    // the rail cannot run into the takeaway band no matter how many reads are supplied.
    const readBottom = c.takeaway ? 6.02 : 6.80;
    const rowH = Math.min(0.66, Math.max(0.34, (readBottom - ly) / reads.length));
    reads.forEach((r, i) => {
      const y = ly + i * rowH;
      s.addShape("line", { x: LX, y: y + 0.115, w: 0.14, h: 0, line: { color: T.bar, width: 1.5 } });
      s.addText(String(r), {
        x: LX + 0.26, y, w: LW - 0.26, h: rowH - 0.03, fontFace: T.body, fontSize: 10.5,
        color: T.sec, margin: 0, lineSpacingMultiple: 1.22, valign: "top",
      });
    });
  }

  // ---- right: the evidence -----------------------------------------------------------
  const bars = clamp(c.bars, 6);
  if (bars.length) {
    const cx0 = 5.75, gap = 0.34, cbase = 5.42, cmax = 1.85;
    const plotW = W - M - cx0;
    const cw = Math.min(1.05, (plotW - (bars.length - 1) * gap) / bars.length);
    // Centre the block when the bar cap leaves slack, so a 3-bar chart doesn't hug the
    // rail and strand 2.5in of white space at the right edge.
    const blockW = bars.length * cw + (bars.length - 1) * gap;
    const bx0 = cx0 + Math.max(0, (plotW - blockW) / 2);
    if (c.chartLabel) {
      s.addText(String(c.chartLabel).toUpperCase(), {
        x: bx0, y: 2.78, w: plotW - (bx0 - cx0), h: 0.26, fontFace: T.body, bold: true,
        fontSize: 8.5, color: T.muted, charSpacing: 2, margin: 0,
      });
    }
    const maxAbs = Math.max(1, ...bars.map((b) => Math.abs(Number(b.value) || 0)));
    // Negative bars grow DOWN from the baseline; cap the scale so they clear the
    // takeaway band (y=6.05) or the footer, preserving proportions across all bars.
    // The shorter plot only ADDS clearance here — cbase moved UP (5.6 → 5.42), so
    // downRoom grew from 0.09 to 0.27in. Do not tighten these constants.
    const negVals = bars.map((b) => Number(b.value) || 0).filter((v) => v < 0);
    let scale = cmax / maxAbs;
    if (negVals.length) {
      const downRoom = (c.takeaway ? 6.05 : 6.95) - cbase - 0.36; // 0.36 = value label + pad
      const negMaxAbs = Math.max(...negVals.map(Math.abs));
      scale = Math.min(scale, Math.max(0.05, downRoom) / negMaxAbs);
    }
    bars.forEach((b, i) => {
      const x = bx0 + i * (cw + gap);
      const v = Number(b.value) || 0;
      const barH = Math.abs(v) * scale;
      const hot = !!b.hot;
      const fill = hot ? T.accent : T.bar;
      if (v >= 0) {
        s.addText(String(b.value), { x, y: cbase - barH - 0.32, w: cw, h: 0.28, align: "center", fontFace: T.body, fontSize: 10.5, color: hot ? T.accentText : T.sec, margin: 0 });
        s.addShape("rect", { x, y: cbase - barH, w: cw, h: barH, fill: { color: fill }, line: { type: "none" } });
      } else {
        s.addShape("rect", { x, y: cbase, w: cw, h: barH, fill: { color: fill }, line: { type: "none" } });
        // Keep negative value labels above the shared baseline. When a takeaway band is
        // present, the space below the baseline is intentionally shallow; putting both the
        // value and category label there causes them to collide at the supported six-bar cap.
        s.addText(String(b.value), { x, y: cbase - 0.32, w: cw, h: 0.28, align: "center", fontFace: T.body, fontSize: 10.5, color: hot ? T.accentText : T.sec, margin: 0 });
      }
      s.addText(String(b.label || ""), { x, y: cbase + 0.08, w: cw, h: 0.28, align: "center", fontFace: T.body, fontSize: 9.5, color: T.sec, margin: 0 });
    });
    s.addShape("line", { x: bx0 - 0.15, y: cbase, w: blockW + 0.3, h: 0, line: { color: T.hair, width: 1 } });
  }

  if (c.takeaway) {
    // Label and sentence are SEPARATE boxes so a wrapped sentence keeps one left margin
    // (a single mixed-run box wraps the tail back under the label). ty sits lower to clear
    // the chart's week labels. onFill picks readable text for the band fill.
    const ty = 6.16, th = 0.7, white = onFill(T.band, T);
    s.addShape("rect", { x: M, y: ty, w: W - 2 * M, h: th, fill: { color: T.band }, line: { type: "none" } });
    s.addText("TAKEAWAY", { x: M + 0.45, y: ty, w: 1.3, h: th, fontFace: T.body, bold: true, fontSize: 10, color: white, charSpacing: 3, margin: 0, valign: "middle" });
    s.addText(c.takeaway, { x: M + 1.95, y: ty, w: W - M - 1.95 - 0.45, h: th, fontFace: T.serif, fontSize: 14.5, color: white, margin: 0, valign: "middle", lineSpacingMultiple: 1.05 });
  }
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 7 · TIMELINE GANTT (Mode 2) — left-rail lane titles, thin bars on a week grid, phase
// brackets above, milestone diamonds ON the axis with hairline leaders, optional status line.
//
// Sleek-first geometry. Lane titles moved OUT of the bars into a LEFT RAIL, so bar length now
// reads as duration instead of as a text container, and the rail can carry a derived meta line
// (auto duration + owner) the reader never had to compute. Bars are thin against an ADAPTIVE
// row pitch — three lanes get air, six lanes tighten rather than overrun the footer. Progress
// is encoded by FILL vs HOLLOW (solid tint = elapsed, hairline outline = remaining), never by a
// second color, which keeps the tint ramp one hue and leaves the single accent free for the one
// lane — or the one milestone — that carries the argument.
//
// Every added field is OPTIONAL. A pre-uplift content object (months / weeks / lanes /
// milestone) renders unchanged apart from the new rail geometry: `milestone` (singular) folds
// into the milestone list, absent `pct` means a solid bar end to end, absent `phases` /
// `today` simply reclaim their vertical band.
//
// Single-emphasis: at most ONE hot across all lanes and milestones. A hot lane accents its bar
// and its rail title (same object, two marks — the roadmap hot-phase precedent); a hot milestone accents
// its diamond and label. Milestone diamonds and the status line are INK, not accent.
//
// content: { kicker, header, sub,
//   months:[..] (≤4), weeks, railLabel? ("Workstream"), unitLabel? ("wks"),
//   lanes:[{ title, catIndex?, start, end, hot?, pct? (0–100), meta? }] (≤6),
//   phases:[{ label, start, end }] (≤4)        — spanning brackets above the axis
//   milestones:[{ label, week, hot? }] (≤4)    — diamonds on the axis + hairline leaders
//   milestone:{ label, week }                  — LEGACY single milestone, still honored
//   today?, todayLabel? ("Today"), categorical?, source }
function timelineGantt(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const weeks = Math.max(1, Number(c.weeks) || 12);
  const lanes = clamp(c.lanes, 6);
  const months = clamp(c.months || ["Month 1", "Month 2", "Month 3"], 4);
  const phases = clamp(c.phases, 4);
  // Legacy singular `milestone` folds into the list so pre-uplift content still renders.
  const stones = clamp(c.milestones || (c.milestone ? [c.milestone] : []), 4);
  const hasToday = Number.isFinite(Number(c.today));

  const railW = 2.40, gx = M + railW, gw = W - M - gx;
  const xAt = (wk) => gx + (Math.max(0, Math.min(weeks, Number(wk) || 0)) / weeks) * gw;
  // Keep centered caption boxes inside the frame near the grid edges.
  const capX = (cx, cw) => Math.min(Math.max(cx - cw / 2, 0.1), W - 0.1 - cw);

  // Vertical solve: reserve the optional rails, split what remains across the lanes, then nudge
  // the whole block down when there is slack. The layout cannot overrun the footer.
  const top = 2.76, bottom = hasToday ? 6.66 : 6.86;
  const phaseH = phases.length ? 0.44 : 0;
  const axisH = 0.40 + (stones.length ? 0.48 : 0.12);
  const laneTop0 = top + phaseH + axisH;
  const rowH = Math.max(0.32, Math.min(0.76, (bottom - laneTop0) / Math.max(1, lanes.length)));
  const used = phaseH + axisH + lanes.length * rowH;
  const y0 = top + Math.max(0, (bottom - top - used) * 0.40);

  const monthY = y0 + phaseH;
  const tickY = monthY + 0.28;
  const msLabY = monthY + 0.38;
  const axisY = monthY + 0.40 + (stones.length ? 0.30 : 0.02);
  const laneTop = axisY + (stones.length ? 0.18 : 0.10);
  const gridBot = laneTop + lanes.length * rowH;

  // — phase brackets: hairline span with end ticks, small-caps label centered above
  phases.forEach((p) => {
    const x0 = xAt(p.start), pw = Math.max(0.5, xAt(p.end) - x0);
    s.addText(String(p.label || "").toUpperCase(), {
      x: x0, y: y0, w: pw, h: 0.24, align: "center", fontFace: T.body, bold: true,
      fontSize: 8, color: T.muted, charSpacing: 2, margin: 0,
    });
    s.addShape("line", { x: x0, y: y0 + 0.26, w: pw, h: 0, line: { color: T.hair, width: 1 } });
    s.addShape("line", { x: x0, y: y0 + 0.26, w: 0, h: 0.08, line: { color: T.hair, width: 1 } });
    s.addShape("line", { x: x0 + pw, y: y0 + 0.26, w: 0, h: 0.08, line: { color: T.hair, width: 1 } });
  });

  // — axis header: rail label + month labels + week ticks, closed by ONE ink rule spanning
  //   rail and track (the ruled-matrix idiom — this is a matrix, not a floating chart).
  s.addText(String(c.railLabel || "Workstream").toUpperCase(), {
    x: M, y: monthY, w: railW - 0.22, h: 0.28, fontFace: T.body, bold: true, fontSize: 9,
    color: T.muted, charSpacing: 2, margin: 0,
  });
  months.forEach((m, i) => {
    const mw = gw / months.length;
    s.addText(String(m).toUpperCase(), {
      x: gx + i * mw + 0.07, y: monthY, w: mw - 0.07, h: 0.28,
      fontFace: T.body, bold: true, fontSize: 9, color: T.muted, charSpacing: 2, margin: 0,
    });
  });
  if (weeks <= 16) {
    for (let i = 1; i < weeks; i++) {
      s.addShape("line", { x: xAt(i), y: tickY, w: 0, h: 0.10, line: { color: T.hair, width: 0.75 } });
    }
  }
  s.addShape("line", { x: M, y: axisY, w: W - 2 * M, h: 0, line: { color: T.ink, width: 1.25 } });

  // — milestone leaders + grid verticals, drawn BEHIND the bars
  stones.forEach((mst) => {
    s.addShape("line", {
      x: xAt(mst.week), y: axisY + 0.11, w: 0, h: Math.max(0.05, gridBot - axisY - 0.11),
      line: { color: T.hair, width: 0.75 },
    });
  });
  for (let i = 1; i <= months.length; i++) {
    s.addShape("line", { x: gx + i * (gw / months.length), y: axisY, w: 0, h: gridBot - axisY, line: { color: T.hair, width: 1 } });
  }
  s.addShape("line", { x: gx, y: axisY, w: 0, h: gridBot - axisY, line: { color: T.hair, width: 1 } });

  // — lanes: rail title (+ derived meta when the pitch allows), thin bar, row hairline
  const showMeta = rowH >= 0.46;
  lanes.forEach((l, i) => {
    const rowY = laneTop + i * rowH, cy = rowY + rowH / 2;
    const cat = c.categorical ? catAt(T, l.catIndex != null ? l.catIndex : i) : T.cat.data;
    const hot = !!l.hot;
    const x0 = xAt(l.start), span = Math.max(0.06, xAt(l.end) - x0);
    const barH = Math.max(0.15, Math.min(0.30, rowH * 0.42)), by = cy - barH / 2;
    const pct = Number.isFinite(Number(l.pct)) ? Math.max(0, Math.min(100, Number(l.pct))) : null;
    const doneW = pct == null ? span : span * (pct / 100);
    if (doneW > 0.01) {
      s.addShape("rect", { x: x0, y: by, w: doneW, h: barH, fill: { color: hot ? T.accent : cat.b }, line: { type: "none" } });
    }
    if (pct != null && span - doneW > 0.01) {
      s.addShape("rect", { x: x0 + doneW, y: by, w: span - doneW, h: barH, fill: { type: "none" }, line: { color: T.hair, width: 0.75 } });
    }
    s.addText(l.title || "", {
      x: M, y: showMeta ? cy - 0.27 : rowY, w: railW - 0.22, h: showMeta ? 0.26 : rowH,
      fontFace: hot ? T.body : T.bodyMedium, bold: hot, fontSize: 11.5,
      color: hot ? T.accentText : T.ink, margin: 0, valign: showMeta ? "bottom" : "middle",
    });
    if (showMeta) {
      const dur = Math.max(0, (Number(l.end) || 0) - (Number(l.start) || 0));
      const meta = [dur ? `${dur} ${c.unitLabel || "wks"}` : "", l.meta || ""].filter(Boolean).join(" · ");
      if (meta) s.addText(meta.toUpperCase(), {
        x: M, y: cy + 0.01, w: railW - 0.22, h: 0.22, fontFace: T.body, fontSize: 8,
        color: T.muted, charSpacing: 1.5, margin: 0, valign: "top",
      });
    }
    s.addShape("line", { x: M, y: rowY + rowH, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } });
  });

  // — milestones sit ON the axis rule, label tucked above the diamond
  stones.forEach((mst) => {
    // The diamond and its label need DIFFERENT accent tiers: the shape can carry the bright
    // brand accent, but the 8pt label is text and would fall to 2.06:1 on sphera.
    const mx = xAt(mst.week);
    const mfill = mst.hot ? T.accent : T.ink;
    const mlab = mst.hot ? T.accentText : T.ink;
    s.addShape("diamond", { x: mx - 0.11, y: axisY - 0.11, w: 0.22, h: 0.22, fill: { color: mfill }, line: { type: "none" } });
    s.addText(String(mst.label || "").toUpperCase(), {
      x: capX(mx, 2.10), y: msLabY, w: 2.10, h: 0.20, align: "center", fontFace: T.body, bold: true,
      fontSize: 8, color: mlab, charSpacing: 2, margin: 0, valign: "bottom",
    });
  });

  // — status line last, so it reads as an overlay across the plan
  if (hasToday) {
    const tx = xAt(c.today);
    s.addShape("line", { x: tx, y: axisY, w: 0, h: gridBot - axisY, line: { color: T.ink, width: 1.25, dashType: "dash" } });
    s.addText(String(c.todayLabel || "Today").toUpperCase(), {
      x: capX(tx, 2.0), y: gridBot + 0.07, w: 2.0, h: 0.22, align: "center", fontFace: T.body,
      bold: true, fontSize: 8.5, color: T.ink, charSpacing: 2, margin: 0,
    });
  }

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 8 · STEP LINE (Mode 1) — numbered circles on one progress-weighted connector, with optional
// phase brackets above, decision gates between steps, and a ruled detail rail below.
//
// The uplift is density without noise. The connector still encodes progress (solid ink up to the
// argued step, hairline after — the best thing about the original), but the slide now answers
// "who / how long / what does it hand off" through a small ruled matrix keyed to the step
// columns. That is the `roadmap` idiom, so it reads as house furniture rather than a new device.
// Steps sit in an even COLUMN GRID instead of stretching to the frame edges, which is what gives
// the detail rail's row labels a left gutter to live in.
//
// Everything added is OPTIONAL and geometry degrades to the original: with no `detailRows`,
// `phases`, or `gates`, the vertical solve puts the connector at y≈3.95 — the pre-uplift position.
//
// Single-emphasis: the hot step's circle fills with the band color; its detail column steps up to
// ink + Medium. WEIGHT, not a second color. Gate diamonds are hollow (paper fill, ink keyline) so
// they stay quieter than the gantt's solid milestone diamonds.
//
// content: { kicker, header, sub,
//   steps:[{ n?, name, desc, hot?, details:[..] }] (≤5),
//   detailRows:[label] (≤3)            — row labels for the lower rail; cells come from step.details
//   phases:[{ label, from, to }] (≤3)  — 0-based step-index spans, bracketed above the line
//   gates:[{ after, label }] (≤4)      — decision diamonds between step `after` and `after+1`
//   source }
function stepLine(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  const steps = clamp(c.steps, 5);
  const n = steps.length || 1;
  const rows = clamp(c.detailRows, 3);
  const phases = clamp(c.phases, 3);
  const gates = clamp(c.gates, 4);

  // Column grid. A detail rail claims a left gutter for its row labels; without one the columns
  // spread across the full content width.
  const railW = rows.length ? 1.55 : 0;
  const colX0 = M + railW, colW = (W - M - colX0) / n;
  const stepX = (i) => colX0 + (i + 0.5) * colW;
  const cellW = Math.min(2.15, colW - 0.16);

  // Vertical solve: measure the block, then center it in the content band with an upward bias.
  const phaseH = phases.length ? (gates.length ? 0.74 : 0.56) : 0;
  const drowH = 0.50, band0 = 2.80, band1 = 6.86;
  const blockH = phaseH + 1.18 + (rows.length ? 0.64 + rows.length * drowH : 0.50);
  const y0 = band0 + Math.max(0, (band1 - band0 - blockH) * 0.34);
  const lineY = y0 + phaseH + 0.34;
  const nameY = lineY + 0.50, descY = nameY + 0.34, ruleY = descY + 0.54;
  const cr = 0.34;

  // — phase brackets over step-index spans
  phases.forEach((p) => {
    const a = Math.max(0, Math.min(n - 1, Number(p.from) || 0));
    const b = Math.max(a, Math.min(n - 1, Number(p.to != null ? p.to : p.from) || 0));
    const x0 = stepX(a) - cellW / 2, pw = stepX(b) + cellW / 2 - x0;
    s.addText(String(p.label || "").toUpperCase(), {
      x: x0, y: y0, w: pw, h: 0.22, align: "center", fontFace: T.body, bold: true,
      fontSize: 8, color: T.muted, charSpacing: 2, margin: 0,
    });
    s.addShape("line", { x: x0, y: y0 + 0.26, w: pw, h: 0, line: { color: T.hair, width: 1 } });
    s.addShape("line", { x: x0, y: y0 + 0.26, w: 0, h: 0.08, line: { color: T.hair, width: 1 } });
    s.addShape("line", { x: x0 + pw, y: y0 + 0.26, w: 0, h: 0.08, line: { color: T.hair, width: 1 } });
  });

  // — progress-weighted connector: ink to the argued step, hairline after
  if (n > 1) {
    const xa = stepX(0), xb = stepX(n - 1);
    const hotIdx = steps.findIndex((st) => st.hot);
    if (hotIdx <= 0) {
      s.addShape("line", { x: xa, y: lineY, w: xb - xa, h: 0, line: { color: T.ink, width: 1.5 } });
    } else {
      const hx = stepX(hotIdx);
      s.addShape("line", { x: xa, y: lineY, w: hx - xa, h: 0, line: { color: T.ink, width: 1.5 } });
      s.addShape("line", { x: hx, y: lineY, w: xb - hx, h: 0, line: { color: T.hair, width: 1 } });
    }
  }

  // — decision gates ride the connector between columns
  gates.forEach((g) => {
    const i = Number(g.after);
    if (!(i >= 0 && i < n - 1)) return;
    const gxp = (stepX(i) + stepX(i + 1)) / 2, lw = Math.min(1.6, Math.max(0.7, colW - 0.74));
    s.addShape("diamond", { x: gxp - 0.10, y: lineY - 0.10, w: 0.20, h: 0.20, fill: { color: T.paper }, line: { color: T.ink, width: 1.25 } });
    s.addText(String(g.label || "").toUpperCase(), {
      x: gxp - lw / 2, y: lineY - 0.60, w: lw, h: 0.22, align: "center", fontFace: T.body, bold: true,
      fontSize: 7.5, color: T.sec, charSpacing: 1.5, margin: 0, valign: "bottom",
    });
  });

  // — steps
  steps.forEach((st, i) => {
    const x = stepX(i), hot = !!st.hot;
    s.addShape("ellipse", {
      x: x - cr, y: lineY - cr, w: cr * 2, h: cr * 2,
      fill: { color: hot ? T.band : T.paper }, line: { color: hot ? T.band : T.ink, width: 1.25 },
    });
    s.addText(st.n || String(i + 1).padStart(2, "0"), {
      x: x - cr, y: lineY - cr, w: cr * 2, h: cr * 2, align: "center", valign: "middle",
      fontFace: T.body, bold: true, fontSize: 10.5, color: hot ? "FFFFFF" : T.ink, margin: 0,
    });
    s.addText(st.name || "", {
      x: x - cellW / 2, y: nameY, w: cellW, h: 0.30, align: "center",
      fontFace: hot ? T.display : T.displayMedium, bold: hot, fontSize: 13.5, color: T.ink, margin: 0,
    });
    s.addText(st.desc || "", {
      x: x - cellW / 2, y: descY, w: cellW, h: 0.50, align: "center", fontFace: T.body,
      fontSize: 9.5, color: T.sec, margin: 0, lineSpacingMultiple: 1.25,
    });
  });

  // — detail rail: ink header rule, small-caps row labels, hairline-ruled rows
  if (rows.length) {
    s.addShape("line", { x: M, y: ruleY, w: W - 2 * M, h: 0, line: { color: T.ink, width: 1.25 } });
    rows.forEach((lab, r) => {
      const ry = ruleY + 0.10 + r * drowH;
      s.addText(String(lab).toUpperCase(), {
        x: M, y: ry, w: railW - 0.18, h: drowH - 0.10, fontFace: T.body, bold: true, fontSize: 8.5,
        color: T.muted, charSpacing: 2, margin: 0, valign: "middle",
      });
      steps.forEach((st, i) => {
        const hot = !!st.hot;
        s.addText(String((st.details || [])[r] || ""), {
          x: stepX(i) - cellW / 2, y: ry, w: cellW, h: drowH - 0.10, align: "center",
          fontFace: hot ? T.bodyMedium : T.body, fontSize: 10, color: hot ? T.ink : T.sec,
          margin: 0, valign: "middle", lineSpacingMultiple: 1.2,
        });
      });
      s.addShape("line", { x: M, y: ry + drowH - 0.06, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } });
    });
  }

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 9 · ARCHITECTURE (Mode 2) — a layered system exhibit. Flat boxes + arrows, optionally
// organised on a TIER RAIL (horizontal planes with small-caps labels down the left gutter) with
// a CROSS-CUTTING RAIL on the right for concerns that span every plane. Depth comes from
// LAYERING and TYPOGRAPHIC TIERS — hairline lane rules, tech chips, sub-items, numbered flow
// badges, plated arrow labels — NOT from more color, gradients or shadows. Monochrome by
// default; category tint is opt-in per box (catIndex) and should encode the TIER, not decorate.
// Emphasis stays an INK KEYLINE (b.hot) — never a second accent (the kicker owns the accent).
//
// EVERY new field is optional. Content carrying only { groups, boxes, arrows, legend } renders
// as it always did.
//
// Canonical 3-tier geometry (copy it — bands are author-supplied, like groups/boxes):
//   tiers  y 2.72 h 1.26 · y 4.12 h 1.26 · y 5.52 h 1.26   (field ends 6.78, clears the footer)
//   boxes  y band.y+0.13, h 1.00 · x 2.10 → right edge 10.36 · rail x 10.60 w 1.88
//
// content: {
//   kicker, header, sub, source, notes,
//   tiers:[{ label, y, h }]              (≤4) horizontal planes: hairline lane rules + gutter label
//   tierFill?: bool                      wash each lane in T.surface (untinted boxes flip to paper)
//   tierLabelW?: num                     gutter width, default 1.05
//   groups:[{ label, x, y, w, h }]       hairline sub-frames — unchanged
//   boxes:[{ x, y, w, h, label, desc?, items?:[≤3], chips?:[≤4], n?, catIndex?, hot? }]  (≤12)
//   arrows:[{ x, y, len, dir?:"down"|"up"|"left", to?:{x,y}, elbow?:"hv"|"vh", label? }]
//   rail:{ label, sub?, x, y, w, h, items:[{ label, desc }] }   (≤5) cross-cutting column
//   legend:[{ label, catIndex }]         (≤6) shown only when a box uses catIndex AND no tiers
// }
function architecture(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const tiers = clamp(c.tiers, 4);
  const gutW = c.tierLabelW != null ? c.tierLabelW : 1.05;
  const fieldX = M + gutW; // where the diagram field starts (right of the plane labels)

  // ---- tier rail: lane rules + small-caps plane labels in the left gutter ----
  if (tiers.length) {
    const last = tiers[tiers.length - 1];
    // Optional surface wash FIRST so the hairlines stay on top of it.
    if (c.tierFill) tiers.forEach((t) => {
      s.addShape("rect", { x: fieldX, y: t.y, w: W - M - fieldX, h: t.h, fill: { color: T.surface }, line: { type: "none" } });
    });
    // One rule per boundary (top, each inter-band midpoint, bottom) — never two parallel
    // hairlines a gap apart, which reads as a mistake rather than a lane.
    const rules = [tiers[0].y];
    for (let i = 0; i < tiers.length - 1; i++) rules.push((tiers[i].y + tiers[i].h + tiers[i + 1].y) / 2);
    rules.push(last.y + last.h);
    rules.forEach((y) => s.addShape("line", { x: M, y, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } }));
    s.addShape("line", { x: fieldX, y: rules[0], w: 0, h: rules[rules.length - 1] - rules[0], line: { color: T.hair, width: 0.75 } });
    tiers.forEach((t) => {
      // 8pt / 1.2 tracking, not 8.5 / 2: at the wider setting "APPLICATION" exceeded the 1.05in
      // gutter and broke MID-WORD ("APPLICATIO / N PLANE"). Wrapping between words is fine.
      s.addText(String(t.label || "").toUpperCase(), {
        x: M, y: t.y, w: gutW, h: t.h, fontFace: T.body, bold: true, fontSize: 8,
        color: T.muted, charSpacing: 1.2, margin: 0, valign: "middle", lineSpacingMultiple: 1.25,
      });
    });
  }

  // ---- optional group containers (unchanged): hairline frame + small-caps label ----
  (c.groups || []).forEach((g) => {
    s.addShape("rect", { x: g.x, y: g.y, w: g.w, h: g.h, fill: { type: "none" }, line: { color: T.hair, width: 1 } });
    if (g.label) s.addText(String(g.label).toUpperCase(), {
      x: g.x + 0.04, y: g.y - 0.28, w: g.w, h: 0.26, fontFace: T.body, bold: true, fontSize: 9,
      color: T.muted, charSpacing: 2, margin: 0,
    });
  });

  // ---- boxes: badge · label · desc/items · chip row ----
  const boxes = clamp(c.boxes, 12);
  boxes.forEach((b) => {
    const tinted = b.catIndex != null;
    const cat = tinted ? catAt(T, b.catIndex) : null;
    const fill = tinted ? cat.b : (c.tierFill && tiers.length ? T.paper : T.surface);
    const line = b.hot ? { color: T.ink, width: 1.5 } : (tinted ? { type: "none" } : { color: T.hair, width: 0.75 });
    const labelColor = tinted ? cat.t : T.ink;
    s.addShape("rect", { x: b.x, y: b.y, w: b.w, h: b.h, fill: { color: fill }, line });

    const ix = b.x + 0.16, iw = b.w - 0.32;

    // Chips are packed into only as many rows as the box height can hold; overflow is DROPPED
    // with a warning (prevention-first, same contract as clamp) rather than colliding with desc.
    const chipH = 0.20, chipGapX = 0.06, chipGapY = 0.05;
    const maxRows = Math.max(0, Math.min(2, Math.floor((b.h - 0.55) / (chipH + chipGapY))));
    const packed = [];
    let droppedChips = 0;
    {
      let row = [], used = 0;
      for (const t of clamp(b.chips, 4)) {
        const cw = Math.min(iw, 0.18 + String(t).length * 0.056);
        if (row.length && used + chipGapX + cw > iw + 0.001) { packed.push(row); row = []; used = 0; }
        if (packed.length >= maxRows) { droppedChips += 1; continue; }
        row.push({ t, w: cw }); used += (used ? chipGapX : 0) + cw;
      }
      if (row.length) { if (packed.length < maxRows) packed.push(row); else droppedChips += row.length; }
    }
    if (droppedChips) console.warn(`layouts WARNING: architecture box "${b.label}" DROPPED ${droppedChips} chip(s) — they don't fit. Shorten the chips or widen/heighten the box.`);
    const chipBlockH = packed.length ? packed.length * chipH + (packed.length - 1) * chipGapY : 0;
    // 0.08 bottom pad (was 0.11) buys the desc block the ~0.03in it needed to fit two lines
    // above a chip row inside a 1.00in box; at 0.11 the second line clipped.
    const chipTop = b.y + b.h - 0.08 - chipBlockH;

    // numbered flow badge — lets a reader trace 1→N without labelling every arrow
    const hasN = b.n != null;
    if (hasN) {
      const badge = tinted ? cat.t : T.ink;
      s.addShape("rect", { x: ix, y: b.y + 0.12, w: 0.21, h: 0.21, fill: { color: badge }, line: { type: "none" } });
      s.addText(String(b.n), {
        x: ix, y: b.y + 0.12, w: 0.21, h: 0.21, align: "center", valign: "middle",
        fontFace: T.body, bold: true, fontSize: 7.5, color: onFill(badge, T), margin: 0,
      });
    }
    s.addText(b.label || "", {
      x: hasN ? ix + 0.27 : ix, y: b.y + 0.10, w: iw - (hasN ? 0.27 : 0), h: 0.26,
      fontFace: T.body, bold: true, fontSize: 10.5, color: labelColor, margin: 0, valign: "middle",
    });

    let ty = b.y + 0.37;
    const bottom = chipTop - 0.04;
    const subItems = clamp(b.items, 3);
    if (b.desc) {
      // 7.5pt / 1.14 so a two-line desc clears the chip row in a 1.00in box.
      const dh = subItems.length ? 0.30 : Math.max(0.18, bottom - ty);
      s.addText(b.desc, {
        x: ix, y: ty, w: iw, h: dh, fontFace: T.body, fontSize: 7.5, color: T.sec,
        margin: 0, lineSpacingMultiple: 1.14, valign: "top",
      });
      ty += dh + 0.03;
    }
    if (subItems.length) {
      s.addText(subItems.map((t) => `·  ${t}`).join("\n"), {
        x: ix, y: ty, w: iw, h: Math.max(0.18, bottom - ty), fontFace: T.body, fontSize: 7.5,
        color: T.muted, margin: 0, lineSpacingMultiple: 1.3, valign: "top",
      });
    }

    const chipFill = tinted ? T.paper : (fill === T.surface ? T.paper : T.surface);
    const chipLine = tinted ? { type: "none" } : { color: T.hair, width: 0.5 };
    packed.forEach((row, ri) => {
      let cx = ix;
      const cy = chipTop + ri * (chipH + chipGapY);
      row.forEach((ch) => {
        s.addShape("rect", { x: cx, y: cy, w: ch.w, h: chipH, fill: { color: chipFill }, line: chipLine });
        s.addText(String(ch.t), {
          x: cx, y: cy, w: ch.w, h: chipH, align: "center", valign: "middle",
          fontFace: T.body, fontSize: 8, color: tinted ? cat.t : T.sec, margin: 0,
        });
        cx += ch.w + chipGapX;
      });
    });
  });

  // ---- cross-cutting rail: dashed hairline column spanning every tier ----
  const rail = c.rail;
  if (rail && rail.items && Number.isFinite(rail.x) && Number.isFinite(rail.w)) {
    // Paper fill knocks the lane rules out of the column, so it reads as one continuous span.
    s.addShape("rect", { x: rail.x, y: rail.y, w: rail.w, h: rail.h, fill: { color: T.paper }, line: { color: T.hair, width: 1, dashType: "dash" } });
    const rx = rail.x + 0.12, rw = rail.w - 0.24;
    s.addText(String(rail.label || "").toUpperCase(), {
      x: rx, y: rail.y + 0.10, w: rw, h: 0.24, fontFace: T.body, bold: true, fontSize: 8.5,
      color: T.muted, charSpacing: 2, margin: 0, valign: "middle",
    });
    let iy = rail.y + 0.40;
    if (rail.sub) {
      s.addText(rail.sub, { x: rx, y: rail.y + 0.34, w: rw, h: 0.20, fontFace: T.body, italic: true, fontSize: 7.5, color: T.muted, margin: 0 });
      iy = rail.y + 0.60;
    }
    const rItems = clamp(rail.items, 5);
    const ih = (rail.y + rail.h - 0.10 - iy) / Math.max(1, rItems.length);
    rItems.forEach((it, i) => {
      const y = iy + i * ih;
      if (i) s.addShape("line", { x: rx, y: y - 0.04, w: rw, h: 0, line: { color: T.hair, width: 0.75 } });
      s.addText(it.label || "", { x: rx, y: y + 0.03, w: rw, h: 0.28, fontFace: T.body, bold: true, fontSize: 9, color: T.ink, margin: 0, lineSpacingMultiple: 1.12, valign: "top" });
      if (it.desc) s.addText(it.desc, { x: rx, y: y + 0.32, w: rw, h: Math.max(0.18, ih - 0.38), fontFace: T.body, fontSize: 7.5, color: T.muted, margin: 0, lineSpacingMultiple: 1.28, valign: "top" });
    });
  }

  // ---- arrows: straight or elbow, with plated labels ----
  const labelW = (t) => 0.17 + String(t).length * 0.057;
  const plate = (cx, cy, t) => {
    const w = labelW(t), h = 0.21;
    s.addShape("rect", { x: cx - w / 2, y: cy - h / 2, w, h, fill: { color: T.paper }, line: { type: "none" } });
    s.addText(String(t), { x: cx - w / 2, y: cy - h / 2, w, h, align: "center", valign: "middle", fontFace: T.body, fontSize: 8, color: T.muted, margin: 0 });
  };
  // Axis-aligned segment drawn from its min corner with a POSITIVE extent; direction is carried
  // by begin/endArrowType rather than a negative w/h (negative shape extents are not reliably
  // exported). Diagonals are never drawn — elbow legs and straight arrows are axis-aligned.
  const seg = (x1, y1, x2, y2, head) => {
    const line = { color: T.muted, width: 2 };
    if (head) line[(x2 < x1 || y2 < y1) ? "beginArrowType" : "endArrowType"] = "triangle";
    s.addShape("line", { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), line });
  };
  (c.arrows || []).forEach((a) => {
    let x2, y2;
    if (a.to) { x2 = a.to.x; y2 = a.to.y; }
    else if (a.dir === "down") { x2 = a.x; y2 = a.y + a.len; }
    else if (a.dir === "up") { x2 = a.x; y2 = a.y - a.len; }
    else if (a.dir === "left") { x2 = a.x - a.len; y2 = a.y; }
    else { x2 = a.x + a.len; y2 = a.y; }
    const dx = x2 - a.x, dy = y2 - a.y;
    let lx, ly, vertical;
    if (a.to && Math.abs(dx) > 0.01 && Math.abs(dy) > 0.01) {
      // Orthogonal routing: leg 1 unheaded, leg 2 carries the arrowhead. "hv" is the default.
      const corner = a.elbow === "vh" ? { x: a.x, y: y2 } : { x: x2, y: a.y };
      seg(a.x, a.y, corner.x, corner.y, false);
      seg(corner.x, corner.y, x2, y2, true);
      vertical = a.elbow === "vh";
      lx = vertical ? a.x : (a.x + corner.x) / 2;
      ly = vertical ? (a.y + corner.y) / 2 : a.y;
    } else {
      seg(a.x, a.y, x2, y2, true);
      vertical = Math.abs(dy) > Math.abs(dx);
      lx = (a.x + x2) / 2; ly = (a.y + y2) / 2;
    }
    // Label rides a paper plate so it knocks out the line, the lane rules and any tier wash
    // beneath it. Vertical legs take it beside the line; horizontal legs above it.
    if (a.label) {
      if (vertical) plate(lx + 0.07 + labelW(a.label) / 2, ly, a.label);
      else plate(lx, ly - 0.19, a.label);
    }
  });

  // Legend only when boxes actually encode category color (else it decodes nothing) AND there
  // is no tier rail — the plane labels already decode the tints, and the rail owns that band.
  if (!tiers.length && boxes.some((b) => b.catIndex != null)) {
    const legend = clamp(c.legend, 6);
    let lx = M;
    legend.forEach((lg) => {
      const cat = catAt(T, lg.catIndex || 0);
      const label = String(lg.label || "").toUpperCase();
      const cw = 0.34 + label.length * 0.095;
      s.addShape("rect", { x: lx, y: 6.28, w: cw, h: 0.32, fill: { color: cat.b }, line: { type: "none" } });
      s.addText(label, { x: lx, y: 6.28, w: cw, h: 0.32, align: "center", fontFace: T.body, bold: true, fontSize: 8.5, color: cat.t, charSpacing: 2, margin: 0, valign: "middle" });
      lx += cw + 0.28;
    });
  } else if (tiers.length && (c.legend || []).length) {
    console.warn("layouts WARNING: architecture `legend` SUPPRESSED — the tier rail already decodes the tints and occupies that band. Drop `legend` when using `tiers`.");
  }

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 10 · ROADMAP MATRIX (Mode 1, category opt-in) — phase names sit IN INK directly over the ink
// header rule, and the RULE carries the emphasis: the argued phase takes the accent on its name
// and a thickened accent segment of the rule beneath it. No chips.
//
// The v1.9 chip row was the last piece of tinted furniture in the deck: three filled boxes that
// said nothing the phase name did not already say, and that forced the accent to compete with a
// category tint for the same 0.34in of frame. Deleting them buys back a whole band, lets the
// matrix read as ruling (the stepLine idiom), and gives the single emphasis somewhere
// structural to live. Row rules now fall BETWEEN rows only — the trailing rule under the last row
// had nothing beneath it and read as an unclosed table.
//
// Geometry re-derives the column width from the phase count, so the cap could rise from 3 to 4
// without the columns falling off the frame. At n=3 the derived width is 3.19in — identical to the
// old hardcoded value, so pre-uplift content renders in exactly the same columns.
//
// Everything added is OPTIONAL. A pre-uplift content object (rowLabels / phases[].cells) renders
// unchanged apart from the chip deletion.
//
// Single-emphasis: at most ONE hot phase. Its name goes accentText, its rule segment goes accent
// (same object, two marks — the timelineGantt hot-lane precedent) and its cells step from sec to
// ink. WEIGHT, not a third color. `categorical: true` is Mode 2 and is mutually exclusive with
// `hot`: category tints colour every phase name and rule segment, so a hot phase would be a
// seventh hue rather than an emphasis. A hot passed alongside categorical is dropped with a warning.
//
// content: { kicker, header, sub,
//   rowLabels:[label] (<=3, default Objective/Activities/Deliverables) — <=4 accepted, pitch adapts
//   phases:[{ title, meta?, cells:[..], hot?, catIndex? }] (<=4)
//     title  the phase name, in ink over the rule (<= 2 words)
//     meta   optional per-phase metadata line (dates, owner) — small-caps, muted
//     cells  one per rowLabels entry (<= 8 words each)
//   metaPos?: "above"|"below"  — meta band above the names (default) or tucked under them
//   The dashed "we are here" rule takes ONE of two mutually exclusive fields. They are separate
//   fields on purpose: a single overloaded `now` where "0–1 means a fraction and >1 means a phase
//   index" makes `now: 1` — by far the most natural way to write "we have finished one phase" —
//   silently mean "100% complete", which draws the rule at the far right and inverts the slide's
//   claim. It did exactly that on first render. One field, one meaning:
//   nowAfterPhase?  INTEGER count of phases already complete (0..n). Draws in the gutter that
//                   OPENS the next phase. This is the normal case.
//   now?            FRACTION 0–1 across the phase span, for a mid-phase marker.
//   nowLabel? (default "Today"), railLabel?, categorical?, source, notes }
function roadmap(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const phases = clamp(c.phases, 4);
  const n = Math.max(1, phases.length);
  const rows = clamp(c.rowLabels || ["Objective", "Activities", "Deliverables"], 4);

  // — horizontal: the row-label gutter is fixed, the columns split what is left.
  const gut = 1.45, leftW = 1.35, tg = 0.30;
  const colX0 = M + gut;                      // 2.30
  const region = (W - M) - colX0;             // 10.1833 — the phase span
  const tw = (region - (n - 1) * tg) / n;     // 3.19 at n=3 (the pre-uplift width), 2.32 at n=4
  const colX = (i) => colX0 + i * (tw + tg);
  const cellW = Math.max(0.6, tw - 0.05);
  const capX = (cx, cw) => Math.min(Math.max(cx - cw / 2, 0.1), W - 0.1 - cw);

  // — single emphasis: one hot, and never alongside category tints.
  const catMode = !!c.categorical;
  const anyHot = phases.some((p) => p.hot);
  if (catMode && anyHot) {
    console.warn("layouts WARNING: roadmap `hot` IGNORED because `categorical` is set — category tints already colour every phase, so a hot phase would read as a seventh hue, not as emphasis. Drop one of the two.");
  }
  const hotIdx = catMode ? -1 : phases.findIndex((p) => p.hot);

  // — vertical solve. Header band (meta + names + rule) is measured, the rows split the rest, and
  //   the block cannot reach the footer band at 7.08.
  const hasMeta = phases.some((p) => p.meta);
  const metaAbove = c.metaPos !== "below";
  const bandTop = 2.80, metaH = hasMeta ? 0.24 : 0, nameH = 0.34;
  const nameY = hasMeta && metaAbove ? bandTop + metaH : bandTop;
  const metaY = metaAbove ? bandTop : bandTop + nameH + 0.01;
  const ruleY = bandTop + metaH + nameH + 0.14;   // 3.28 bare, 3.52 with a meta band

  const nowIdx = Number(c.nowAfterPhase), nowFrac = Number(c.now);
  const hasIdx = Number.isFinite(nowIdx), hasFrac = Number.isFinite(nowFrac);
  if (hasIdx && hasFrac) {
    console.warn("layouts WARNING: roadmap got BOTH `nowAfterPhase` and `now`; using `nowAfterPhase` and ignoring `now`. They are alternatives, not a pair.");
  }
  const hasNow = hasIdx || hasFrac;
  const rowTop = ruleY + 0.18;
  const bandBot = hasNow ? 6.70 : 6.82;           // the now label claims the strip below the rows
  const rowH = Math.max(0.56, Math.min(1.24, (bandBot - rowTop) / rows.length));
  const rowsBot = rowTop + rows.length * rowH;
  const cellFs = rowH >= 0.95 ? 11 : 10;

  // — optional left-gutter head, filling the empty corner cell above the row labels
  if (c.railLabel) {
    s.addText(String(c.railLabel).toUpperCase(), {
      x: M, y: nameY, w: leftW, h: nameH, fontFace: T.body, bold: true, fontSize: 8.5,
      color: T.muted, charSpacing: 2, margin: 0, valign: "bottom",
    });
  }

  // — phase names (and their meta line) sitting on the rule
  phases.forEach((p, i) => {
    const x = colX(i), hot = i === hotIdx;
    const cat = catMode ? catAt(T, p.catIndex != null ? p.catIndex : i) : null;
    s.addText(String(p.title || ""), {
      x, y: nameY, w: cellW, h: nameH,
      fontFace: hot ? T.display : T.displayMedium, bold: hot, fontSize: 14,
      color: hot ? T.accentText : cat ? cat.t : T.ink, margin: 0, valign: "bottom",
    });
    if (p.meta) {
      s.addText(String(p.meta).toUpperCase(), {
        x, y: metaY, w: cellW, h: 0.22, fontFace: T.body, fontSize: 8,
        color: T.muted, charSpacing: 1.5, margin: 0, valign: metaAbove ? "bottom" : "top",
      });
    }
  });

  // — the header rule: ink across the full width, then the emphasis segments over their columns
  s.addShape("line", { x: M, y: ruleY, w: W - 2 * M, h: 0, line: { color: T.ink, width: 1.25 } });
  if (catMode) {
    phases.forEach((p, i) => {
      const cat = catAt(T, p.catIndex != null ? p.catIndex : i);
      s.addShape("line", { x: colX(i), y: ruleY, w: tw, h: 0, line: { color: cat.t, width: 2.5 } });
    });
  } else if (hotIdx >= 0) {
    s.addShape("line", { x: colX(hotIdx), y: ruleY, w: tw, h: 0, line: { color: T.accent, width: 3.25 } });
  }

  // — the "we are here" rule, drawn before the rows so the cell text prints over it
  if (hasNow) {
    let nx;
    if (hasIdx) {
      const i = Math.max(0, Math.min(n, Math.round(nowIdx)));
      // The gutter that opens phase i. Clamped inside the span so i=0 and i=n stay on the frame.
      nx = Math.min(colX0 + region, Math.max(colX0, colX0 + i * (tw + tg) - tg / 2));
    } else {
      nx = colX0 + Math.max(0, Math.min(1, nowFrac)) * region;
    }
    s.addShape("line", {
      x: nx, y: ruleY + 0.02, w: 0, h: Math.max(0.1, rowsBot - ruleY - 0.02),
      line: { color: T.ink, width: 1.25, dashType: "dash" },
    });
    s.addText(String(c.nowLabel || "Today").toUpperCase(), {
      x: capX(nx, 1.9), y: rowsBot + 0.06, w: 1.9, h: 0.22, align: "center", fontFace: T.body,
      bold: true, fontSize: 8.5, color: T.ink, charSpacing: 2, margin: 0,
    });
  }

  // — rows: small-caps label in the gutter, cells per phase, hairline BETWEEN rows only
  rows.forEach((lab, r) => {
    const y = rowTop + r * rowH;
    s.addText(String(lab).toUpperCase(), {
      x: M, y, w: leftW, h: 0.3, fontFace: T.body, bold: true, fontSize: 8.5,
      color: T.muted, charSpacing: 2, margin: 0, valign: "top",
    });
    phases.forEach((p, i) => {
      s.addText(String((p.cells || [])[r] || ""), {
        x: colX(i), y: y - 0.04, w: cellW, h: rowH - 0.16, fontFace: T.bodyMedium,
        fontSize: cellFs, color: i === hotIdx ? T.ink : T.sec, margin: 0,
        lineSpacingMultiple: 1.32, valign: "top",
      });
    });
    if (r < rows.length - 1) {
      s.addShape("line", { x: M, y: y + rowH - 0.12, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.5 } });
    }
  });

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 11 · ROADMAP TRACK (Mode 1) — the same plan told as a JOURNEY rather than a matrix: 3–5 equal
// segments of ONE continuous horizontal track, one outcome line per segment, hollow gate diamonds
// at the boundaries.
//
// The routing test against `roadmap` is whether the phases are PARALLEL or SEQUENTIAL. A matrix
// invites the reader to compare cells down a column — right when each phase has an objective, a
// scope and a gate to line up. A track says the phases only happen in order and each one has to
// clear a gate before the next starts, which is a different claim and needs a different exhibit.
// Reach for the track when there is one sentence per phase; reach for `roadmap` when there are
// three or more.
//
// Progress borrows the timelineGantt idiom exactly: a single `pct` across the whole track paints
// SOLID ink up to where the plan has actually got to and leaves a HAIRLINE for what remains — fill
// vs hollow, never a second colour. Gate diamonds are hollow (paper fill, ink keyline), the
// stepLine convention, so they stay quieter than the gantt's solid milestone diamonds.
//
// Single-emphasis: at most ONE hot phase, which takes accentText on its name and an accent segment
// of the track. The accent segment paints the whole phase span, so `pct` shading is OVERRIDDEN
// inside it — set `hot` on the phase you are arguing for, not on a half-elapsed one. Monochrome by
// design: there is no `categorical` here, because one track cannot be six identities.
//
// content: { kicker, header, sub,
//   phases:[{ name, meta?, outcome, items?:[..], gate?, hot? }] (<=5, >=3 recommended)
//     name     the phase (<= 2 words), left-aligned at the head of its segment
//     meta     optional metadata line above the name (dates, owner) — small-caps, muted
//     outcome  ONE sentence: what is true when this phase ends (<= 14 words)
//     items    optional parallel rows beneath the outcome (<=3, <= 5 words each — item r should
//              mean the same thing in every phase, e.g. scope / evidence / owner)
//     gate     optional label for the diamond that CLOSES this phase (<= 3 words)
//   pct?  0–100 progress across the whole track (absent = a solid track end to end)
//   source, notes }
function roadmapTrack(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const phases = clamp(c.phases, 5);
  const n = Math.max(1, phases.length);
  const trackX0 = M, trackW = W - 2 * M;      // 0.85 → 12.4833
  const segW = trackW / n;                     // 2.33 at n=5, 3.88 at n=3
  const segX = (i) => trackX0 + i * segW;
  const colW = Math.max(0.6, segW - 0.24);
  const capX = (cx, cw) => Math.min(Math.max(cx - cw / 2, 0.1), W - 0.1 - cw);

  const hasMeta = phases.some((p) => p.meta);
  const hasGate = phases.some((p) => p.gate);
  const itemsN = Math.min(3, phases.reduce((m, p) => Math.max(m, Array.isArray(p.items) ? p.items.length : 0), 0));
  const hotIdx = phases.findIndex((p) => p.hot);

  // — vertical solve: measure the block, then centre it in the content band with an upward bias.
  //   With items the block fills the band exactly; without them it floats a little higher.
  const band0 = 2.86, bandBot = 6.80;
  const metaH = hasMeta ? 0.24 : 0, nameH = 0.34;
  const gapNT = 0.20;                          // name → track
  const gapTO = hasGate ? 0.52 : 0.34;         // track → outcome (gate labels ride this gap)
  const headH = metaH + nameH + gapNT + gapTO;
  const avail = bandBot - band0 - headH;
  const outH = itemsN ? 0.86 : Math.min(1.9, Math.max(0.6, avail));
  const itemRowH = itemsN ? Math.max(0.30, Math.min(0.66, (avail - outH - 0.10) / itemsN)) : 0;
  const blockH = headH + outH + (itemsN ? 0.10 + itemsN * itemRowH : 0);
  const y0 = band0 + Math.max(0, (bandBot - band0 - blockH) * 0.35);

  const metaY = y0;
  const nameY = y0 + metaH;
  const trackY = nameY + nameH + gapNT;
  const outTop = trackY + gapTO;
  const itemsTop = outTop + outH + 0.10;
  const outFs = itemsN ? 11.5 : 13;

  // — the track: hairline for the whole span (what remains), solid ink over the elapsed head
  const pct = Number.isFinite(Number(c.pct)) ? Math.max(0, Math.min(100, Number(c.pct))) : null;
  const doneW = pct == null ? trackW : trackW * (pct / 100);
  s.addShape("line", { x: trackX0, y: trackY, w: trackW, h: 0, line: { color: T.hair, width: 1 } });
  if (doneW > 0.01) {
    s.addShape("line", { x: trackX0, y: trackY, w: doneW, h: 0, line: { color: T.ink, width: 2.5 } });
  }
  if (hotIdx >= 0) {
    s.addShape("line", { x: segX(hotIdx), y: trackY, w: segW, h: 0, line: { color: T.accent, width: 3.25 } });
  }

  // — hollow gate diamonds close their phase, label tucked under the track
  phases.forEach((p, i) => {
    if (!p.gate) return;
    const gx = Math.min(trackX0 + trackW, segX(i) + segW);
    s.addShape("diamond", {
      x: gx - 0.11, y: trackY - 0.11, w: 0.22, h: 0.22,
      fill: { color: T.paper }, line: { color: T.ink, width: 1.25 },
    });
    const lw = Math.min(1.9, Math.max(0.8, segW - 0.30));
    s.addText(String(p.gate).toUpperCase(), {
      x: capX(gx, lw), y: trackY + 0.14, w: lw, h: 0.24, align: "center", fontFace: T.body,
      bold: true, fontSize: 7.5, color: T.sec, charSpacing: 1.5, margin: 0, valign: "top",
    });
  });

  // — per-segment column: meta, name, outcome, optional parallel item rows
  phases.forEach((p, i) => {
    const x = segX(i) + 0.02, hot = i === hotIdx;
    if (p.meta) {
      s.addText(String(p.meta).toUpperCase(), {
        x, y: metaY, w: colW, h: 0.22, fontFace: T.body, fontSize: 8,
        color: T.muted, charSpacing: 1.5, margin: 0, valign: "bottom",
      });
    }
    s.addText(String(p.name || ""), {
      x, y: nameY, w: colW, h: nameH,
      fontFace: hot ? T.display : T.displayMedium, bold: hot, fontSize: 14,
      color: hot ? T.accentText : T.ink, margin: 0, valign: "bottom",
    });
    s.addText(String(p.outcome || ""), {
      x, y: outTop, w: colW, h: outH, fontFace: T.bodyMedium, fontSize: outFs,
      color: hot ? T.ink : T.sec, margin: 0, lineSpacingMultiple: 1.32, valign: "top",
    });
    if (!itemsN) return;
    const its = clamp(p.items, 3);
    for (let r = 0; r < itemsN; r++) {
      const iy = itemsTop + r * itemRowH;
      s.addText(String(its[r] || ""), {
        x, y: iy, w: colW, h: itemRowH - 0.08, fontFace: T.body, fontSize: 9.5,
        color: T.sec, margin: 0, lineSpacingMultiple: 1.2, valign: "middle",
      });
      if (r < itemsN - 1) {
        s.addShape("line", { x, y: iy + itemRowH - 0.06, w: colW, h: 0, line: { color: T.hair, width: 0.75 } });
      }
    }
  });

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 12 · MANIFESTO — one oversized serif statement + accent stop; a breath slide, once/deck, early.
// content: { kicker, statement, accentStop=true, body }
function manifesto(pres, T, ctx, c) {
  const s = slide(pres, T, ctx, { topBar: false });
  if (c.kicker) {
    s.addText(String(c.kicker).toUpperCase(), {
      x: M, y: 0.95, w: 11.6, h: 0.35, fontFace: T.body, bold: true, fontSize: 11,
      color: T.accentText, charSpacing: 4, margin: 0,
    });
  }
  const stmt = String(c.statement || "");
  const fs = stmt.length > 130 ? 36 : stmt.length > 80 ? 40 : 44;
  const runs = c.accentStop === false
    ? [{ text: stmt, options: { color: T.ink } }]
    : [{ text: stmt, options: { color: T.ink } }, { text: ".", options: { color: T.accentText } }];
  s.addText(runs, {
    x: M, y: 1.6, w: 11.6, h: 3.4, fontFace: T.serif, fontSize: fs,
    margin: 0, lineSpacingMultiple: 1.14, valign: "middle",
  });
  if (c.body) {
    s.addText(c.body, {
      x: M, y: 5.0, w: 7.4, h: 1.2, fontFace: T.body, fontSize: 13, color: T.sec,
      margin: 0, lineSpacingMultiple: 1.45, valign: "top",
    });
  }
  s.addNotes(c.notes || "");
  return s;
}

// 13 · QUOTE — full-bleed tint field, serif italic pull-quote, tracked accent attribution. Once/deck.
// content: { quote, attribution }
function quote(pres, T, ctx, c) {
  const s = slide(pres, T, ctx, { topBar: false, footer: false });
  // quoteField is paper on casper (kills the purple-on-purple field) and the calm navy tint
  // on sphera. An oversized neutral quotation mark carries the rhythm break instead of a fill.
  s.background = { color: T.quoteField };
  s.addText("“", { x: 1.15, y: 0.85, w: 2.4, h: 1.9, fontFace: T.serif, fontSize: 150, color: T.hair, margin: 0, valign: "top" });
  const q = String(c.quote || "");
  const fs = q.length > 160 ? 28 : q.length > 100 ? 32 : 37;
  s.addText(q, {
    // No `italic: true` here: T.serifItalic is ALREADY an italic face (subfamily = "Italic"), so
    // the flag asked the renderer to slant an italic a second time — a synthesized oblique on top
    // of a real one.
    x: 1.5, y: 2.35, w: 10.33, h: 2.9, fontFace: T.serifItalic, fontSize: fs,
    color: T.ink, margin: 0, lineSpacingMultiple: 1.2, valign: "top",
  });
  if (c.attribution) {
    s.addText(String(c.attribution).toUpperCase(), {
      x: 1.5, y: 5.35, w: 10, h: 0.35, fontFace: T.body, bold: true, fontSize: 10.5,
      color: T.accentText, charSpacing: 3, margin: 0,
    });
  }
  s.addNotes(c.notes || "");
  return s;
}

// 14 · SOURCES — numbered bibliography in two columns (the terminal provenance slide).
// content: { header, sources:[..] } (clamp 16, 8/col)
function sources(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, { header: c.header || "Sources & methodology", sub: c.sub }, { hs: 22, hh: 0.75 });
  const list = clamp(c.sources, 16);
  // Single-column case (≤8) spreads to fill the frame instead of huddling top-left.
  const perCol = 8, colW = 5.4, y0 = 2.55, rowH = list.length <= 8 ? 0.56 : 0.42;
  const sourceSize = list.length <= 4 ? 11 : 10.25;
  list.forEach((src, i) => {
    const col = Math.floor(i / perCol), row = i % perCol;
    const x = M + col * (colW + 0.8), y = y0 + row * rowH;
    // Index numerals sit at 13pt — at 9.5 they read as footnote marks rather than as the
    // structural index the other layouts use (v1.9b: numerals scaled up deck-wide).
    s.addText(String(i + 1).padStart(2, "0"), {
      x, y: y - 0.03, w: 0.5, h: rowH, fontFace: T.body, bold: true, fontSize: 13, color: T.accentText, margin: 0, valign: "top",
    });
    s.addText(String(src), {
      x: x + 0.62, y, w: colW - 0.62, h: rowH, fontFace: T.body, fontSize: sourceSize, color: T.sec, margin: 0, lineSpacingMultiple: 1.2, valign: "top",
    });
  });
  s.addNotes(c.notes || "");
  return s;
}

// 15 · CLOSING — bold statement on a solid brand-color field, white text, accent contact.
// content: { title, accentStop=true, sub, contact }
function closing(pres, T, ctx, c) {
  const s = slide(pres, T, ctx, { footer: false, topBar: false });
  s.background = { color: T.band };
  const stop = T.cover ? (T.cover.eyebrow || "FFFFFF") : "FFFFFF";
  const title = c.accentStop === false
    ? [{ text: c.title || "Thank you", options: { color: "FFFFFF" } }]
    : [{ text: c.title || "Thank you", options: { color: "FFFFFF" } }, { text: ".", options: { color: stop } }];
  const clen = (c.title || "Thank you").length;
  const cSize = clen > 42 ? 42 : 50;
  s.addText(title, { x: M, y: 2.45, w: 11.6, h: 1.9, fontFace: T.serif, fontSize: cSize, margin: 0, lineSpacingMultiple: 1.1, valign: "top" });
  // thin accent rule (Sphera closing signature)
  s.addShape("rect", { x: 0, y: H - 0.06, w: W, h: 0.06, fill: { color: stop }, line: { type: "none" } });
  if (c.sub) s.addText(c.sub, { x: M, y: 4.35, w: 10.5, h: 0.4, fontFace: T.body, fontSize: 13, color: "FFFFFF", margin: 0 });
  if (c.contact) s.addText(c.contact, { x: M, y: 4.85, w: 8, h: 0.4, fontFace: T.body, bold: true, fontSize: 12.5, color: stop, margin: 0 });
  s.addNotes(c.notes || "");
  return s;
}

// 16 · AGENDA — numbered agenda rows (serif numeral, title, right-aligned owner/time). Its
// own geometry (holds 6–7 rows, unlike challenges' 3). content: { kicker, header, sub,
// items:[{title,owner?,desc?}], source } (clamp 7)
function agenda(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  const items = clamp(c.items, 7);
  const n = items.length;
  const showDesc = n <= 5;
  // v1.9 sleek pass: more air per row, half-weight row hairlines, and the owner column demoted
  // to small-caps metadata — it was reading as a second text column.
  //
  // v1.12: row pitch now DERIVES from the available band instead of a fixed ladder. A 4-item
  // agenda at the old fixed 0.70 ended at y5.65 and left ~1.4in dead at the bottom, so the list
  // floated mid-canvas and read unfinished — the single loudest "template-y" tell in a review of
  // a real client deck. The fix is capacity-matching, NOT padding words in: fewer items simply
  // breathe into the frame. Capped so 2-3 items don't stretch into absurdly tall rows, and the
  // 6-7 item pitches land within a hair of their previous values, so dense agendas are unchanged.
  const y0 = 2.85, BAND = 3.95;                    // y0 -> ~6.80, clear of the 7.08 footer
  const rowH = Math.min(0.95, BAND / Math.max(n, 1));
  items.forEach((it, i) => {
    const y = y0 + i * rowH;
    s.addText(String(i + 1).padStart(2, "0"), {
      x: M, y, w: 1.0, h: rowH, fontFace: T.serif, fontSize: 26, color: T.accentText, margin: 0, valign: "middle",
    });
    s.addText(it.title || "", {
      x: 1.8, y, w: 8.5, h: showDesc && it.desc ? rowH * 0.6 : rowH, fontFace: T.bodyMedium, fontSize: 13.5,
      color: T.ink, margin: 0, valign: showDesc && it.desc ? "top" : "middle", lineSpacingMultiple: 1.15,
    });
    if (showDesc && it.desc) {
      s.addText(it.desc, {
        x: 1.8, y: y + rowH * 0.52, w: 8.5, h: rowH * 0.45, fontFace: T.body, fontSize: 10.5, color: T.sec, margin: 0, valign: "top",
      });
    }
    if (it.owner) s.addText(String(it.owner).toUpperCase(), {
      x: 10.7, y, w: 1.8, h: rowH, align: "right", fontFace: T.body, bold: true, fontSize: 9.5,
      color: T.muted, charSpacing: 1.5, margin: 0, valign: "middle",
    });
    if (i < n - 1) s.addShape("line", { x: M, y: y + rowH, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.5 } });
  });
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 17 · WATERFALL — the bridge PLUS the narrative that explains it. Start total, floating
// deltas (one may be hot), end total, hairline step connectors — and, when any delta
// carries a `note`, a numbered commentary rail on the right keyed to the columns by the
// same 01/02/03 numerals printed under the axis. A bare bridge is an analyst artifact;
// the rail is what makes it a partner-ready exhibit.
// Geometry is opt-in: with no note, no takeaway and no footnote the plot renders at the
// ORIGINAL full-width 5.75/2.70 geometry. Each piece of prose furniture shrinks it.
// Emphasis budget: the ONE accent is the hot delta, expressed on its bar, its value label
// and its rail numeral (the same datum, house precedent — cf. slopeChart).
// Totals and the takeaway band use T.band, a separate role.
// content: { kicker, header, sub, start:{label,value},
//            deltas:[{label,value,hot?, note?}],   // note = optional keyed rail line (≤14 words)
//            end:{label,value}, commentaryTitle,   // optional rail micro-label
//            takeaway,                             // optional — chartTakeaway band treatment
//            footnote,                             // optional assumptions line above the source
//            source }                              (deltas clamp 5)
function waterfall(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  const start = c.start || { label: "Start", value: 0 };
  const deltas = clamp(c.deltas || [], 5);
  const cols = [];
  let running = Number(start.value) || 0;
  cols.push({ label: start.label, kind: "total", base: 0, top: running, value: running, cumAfter: running });
  deltas.forEach((d, di) => {
    const v = Number(d.value) || 0, from = running; running += v;
    cols.push({
      label: d.label, kind: "delta", base: Math.min(from, running), top: Math.max(from, running),
      value: v, hot: !!d.hot, cumAfter: running,
      key: String(di + 1).padStart(2, "0"), note: d.note,
    });
  });
  if (c.end) { const ev = Number(c.end.value); const val = Number.isFinite(ev) ? ev : running; cols.push({ label: c.end.label, kind: "total", base: 0, top: val, value: val, cumAfter: val }); }

  const rail = cols.filter((cc) => cc.kind === "delta" && cc.note);
  const hasRail = rail.length > 0;
  const bandTop = c.footnote ? 6.02 : 6.16;

  // Explicit baselines per furniture combination — the bare bridge keeps its original
  // 5.75 / 2.70 so existing decks render unchanged.
  const baseY = c.takeaway ? (c.footnote ? 5.18 : 5.32) : (c.footnote ? 5.60 : 5.75);
  const plotH = baseY - 3.05;

  const maxTop = Math.max(1, ...cols.map((cc) => cc.top));
  const gx = M + 0.2, gw = (hasRail ? 8.15 : W - M) - gx, scale = plotH / maxTop;
  const n = cols.length, slot = gw / n, bw = Math.min(1.25, slot * 0.6);
  const barX = (i) => gx + i * slot + (slot - bw) / 2;
  // Labels must never exceed their slot once the rail narrows the plot.
  const labSize = hasRail ? 9.5 : 11, valSize = hasRail ? 11.5 : 13;
  const keyY = baseY + 0.08;                          // the 01/02/03 key, on the axis
  const labelY = hasRail ? baseY + 0.32 : baseY + 0.12;
  const labelH = hasRail ? 0.46 : 0.55;

  cols.forEach((col, i) => {
    const x = barX(i);
    const topY = baseY - col.top * scale, botY = baseY - col.base * scale;
    // Totals use INK, not band. On casper band === accent === purple, so a band total and an
    // accent delta rendered identically and the single emphasis collapsed — the argued bar
    // was indistinguishable from the two structural totals. Ink is dark on both themes.
    const fill = col.kind === "total" ? T.ink : (col.hot ? T.accent : T.bar);
    s.addShape("rect", { x, y: topY, w: bw, h: Math.max(0.02, botY - topY), fill: { color: fill }, line: { type: "none" } });
    if (i > 0) {
      const yLevel = baseY - cols[i - 1].cumAfter * scale, prevRight = barX(i - 1) + bw;
      s.addShape("line", { x: prevRight, y: yLevel, w: x - prevRight, h: 0, line: { color: T.hair, width: 0.75 } });
    }
    const vLabel = col.kind === "delta" && col.value >= 0 ? "+" + col.value : String(col.value);
    const vw = Math.min(bw + 0.5, slot - 0.04);
    s.addText(vLabel, { x: x + bw / 2 - vw / 2, y: topY - 0.32, w: vw, h: 0.3, align: "center", fontFace: T.body, fontSize: valSize, color: col.hot ? T.accentText : T.sec, margin: 0 });
    // The key numeral only renders when a rail exists — otherwise it decodes nothing
    // (same principle as architecture's opt-in legend).
    if (hasRail && col.note) {
      s.addText(col.key, { x: x + bw / 2 - vw / 2, y: keyY, w: vw, h: 0.22, align: "center", fontFace: T.body, bold: true, fontSize: 8.5, color: col.hot ? T.accentText : T.muted, charSpacing: 1.5, margin: 0 });
    }
    const lw = Math.min(bw + 0.8, slot - 0.04);
    s.addText(String(col.label || ""), { x: x + bw / 2 - lw / 2, y: labelY, w: lw, h: labelH, align: "center", fontFace: T.body, fontSize: labSize, color: T.sec, margin: 0, lineSpacingMultiple: 1.12 });
  });
  s.addShape("line", { x: gx, y: baseY, w: gw, h: 0, line: { color: T.hair, width: 1 } });

  // ---- commentary rail: one annotated line per delta, keyed by numeral ---------------
  if (hasRail) {
    const rx = 8.62, rw = W - M - rx, railTop = 2.80;
    const railBottom = c.takeaway ? bandTop - 0.16 : (c.footnote ? 6.60 : 6.80);
    s.addShape("line", { x: rx - 0.30, y: railTop, w: 0, h: railBottom - railTop, line: { color: T.hair, width: 1 } });
    s.addText(String(c.commentaryTitle || "What moved it").toUpperCase(), {
      x: rx, y: railTop, w: rw, h: 0.26, fontFace: T.body, bold: true, fontSize: 8.5,
      color: T.muted, charSpacing: 2, margin: 0,
    });
    const ry0 = railTop + 0.34;
    const rowH = Math.min(1.0, (railBottom - ry0) / rail.length);
    rail.forEach((it, i) => {
      const y = ry0 + i * rowH;
      s.addText(it.key, { x: rx, y: y + 0.01, w: 0.34, h: 0.24, fontFace: T.body, bold: true, fontSize: 8.5, color: it.hot ? T.accentText : T.muted, charSpacing: 1.5, margin: 0 });
      s.addText(String(it.label || ""), { x: rx + 0.40, y, w: rw - 0.40, h: 0.24, fontFace: T.bodyMedium, fontSize: 10.5, color: T.ink, margin: 0, valign: "top" });
      // Note sits at 9pt/1.14: at 9.5pt/1.2 a two-line note overran the row rule below it.
      s.addText(String(it.note), { x: rx + 0.40, y: y + 0.24, w: rw - 0.40, h: rowH - 0.30, fontFace: T.body, fontSize: 9, color: T.sec, margin: 0, lineSpacingMultiple: 1.14, valign: "top" });
      if (i < rail.length - 1) s.addShape("line", { x: rx, y: y + rowH - 0.04, w: rw, h: 0, line: { color: T.hair, width: 0.75 } });
    });
  }

  if (c.takeaway) {
    // Same band treatment as chartTakeaway (label and sentence in SEPARATE boxes so a
    // wrapped sentence keeps one left margin). Rides 0.14 higher when a footnote follows.
    const th = 0.7, white = onFill(T.band, T);
    s.addShape("rect", { x: M, y: bandTop, w: W - 2 * M, h: th, fill: { color: T.band }, line: { type: "none" } });
    s.addText("TAKEAWAY", { x: M + 0.45, y: bandTop, w: 1.3, h: th, fontFace: T.body, bold: true, fontSize: 10, color: white, charSpacing: 3, margin: 0, valign: "middle" });
    s.addText(c.takeaway, { x: M + 1.95, y: bandTop, w: W - M - 1.95 - 0.45, h: th, fontFace: T.serif, fontSize: 14.5, color: white, margin: 0, valign: "middle", lineSpacingMultiple: 1.05 });
  }
  if (c.footnote) {
    s.addText(`Note: ${c.footnote}`, {
      x: M, y: c.takeaway ? bandTop + 0.72 : 6.74, w: 10.6, h: 0.24,
      fontFace: T.body, italic: true, fontSize: 8.5, color: T.muted, margin: 0,
    });
  }
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 18 · MATRIX 2×2 — quadrant frame (hairlines), small-caps axis labels, plotted dots at
// normalized 0..1 coords, ONE hot accent dot. content: { kicker, header, sub, xAxis:{low,high},
// yAxis:{low,high}, quadrants:[TL,TR,BL,BR], points:[{label,x,y,hot?}], source } (clamp 8)
function matrix2x2(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });
  const px = 3.4, py = 2.95, pw = 5.6, ph = 3.55;
  s.addShape("rect", { x: px, y: py, w: pw, h: ph, fill: { type: "none" }, line: { color: T.hair, width: 1 } });
  s.addShape("line", { x: px + pw / 2, y: py, w: 0, h: ph, line: { color: T.hair, width: 1 } });
  s.addShape("line", { x: px, y: py + ph / 2, w: pw, h: 0, line: { color: T.hair, width: 1 } });
  const xa = c.xAxis || {}, ya = c.yAxis || {};
  const cap = (txt, x, y, w, align) => s.addText(String(txt).toUpperCase(), { x, y, w, h: 0.3, align, fontFace: T.body, bold: true, fontSize: 8.5, color: T.muted, charSpacing: 2, margin: 0 });
  if (xa.low) cap(xa.low, px, py + ph + 0.12, pw / 2, "left");
  if (xa.high) cap(xa.high, px + pw / 2, py + ph + 0.12, pw / 2, "right");
  if (ya.high) cap(ya.high, px - 2.45, py, 2.35, "right");
  if (ya.low) cap(ya.low, px - 2.45, py + ph - 0.3, 2.35, "right");
  const quads = c.quadrants || [];
  const qpos = [[px + 0.15, py + 0.12, "left"], [px + pw - 2.15, py + 0.12, "right"], [px + 0.15, py + ph - 0.4, "left"], [px + pw - 2.15, py + ph - 0.4, "right"]];
  quads.forEach((q, i) => { if (q && qpos[i]) s.addText(String(q), { x: qpos[i][0], y: qpos[i][1], w: 2.0, h: 0.3, align: qpos[i][2], fontFace: T.body, italic: true, fontSize: 9, color: T.muted, margin: 0 }); });
  const points = clamp(c.points, 8);
  points.forEach((p) => {
    const hot = !!p.hot;
    const nx = Number(p.x) || 0.5;
    const cxp = px + nx * pw, cyp = py + (1 - (Number(p.y) || 0.5)) * ph, r = hot ? 0.12 : 0.085;
    s.addShape("ellipse", { x: cxp - r, y: cyp - r, w: r * 2, h: r * 2, fill: { color: hot ? T.accent : T.bar }, line: { type: "none" } });
    // Keep every label inside its point's OWN quadrant. A fixed 2.3in box hung to the right of
    // the dot ran straight across the centre divider whenever the point sat just left of it,
    // making the label read as belonging to the neighbouring quadrant. Measure the label, and
    // flip it to the left of the dot when it will not fit on the right.
    const qL = nx < 0.5 ? px : px + pw / 2, qR = nx < 0.5 ? px + pw / 2 : px + pw;
    const lw = 0.14 + String(p.label || "").length * 0.083;
    const fitsRight = cxp + 0.16 + lw <= qR;
    s.addText(String(p.label || ""), {
      x: fitsRight ? cxp + 0.16 : Math.max(qL, cxp - 0.16 - lw), y: cyp - 0.14, w: lw, h: 0.3,
      align: fitsRight ? "left" : "right",
      fontFace: hot ? T.bodyMedium : T.body, fontSize: 10, color: hot ? T.accentText : T.ink, margin: 0, valign: "middle",
    });
  });
  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// Vertical de-collision for endpoint labels. The MARKS stay at their true data positions;
// only the LABEL centers are nudged apart, so two items three units apart no longer
// overprint each other. Down-pass, shift-and-up-pass if the stack ran past the floor,
// then clamp the ceiling. This is the fix for the slope chart's one real bug.
function declutter(ys, minGap, lo, hi) {
  const n = ys.length;
  if (n < 2) return ys.slice();
  const ord = ys.map((y, i) => ({ y, i })).sort((a, b) => a.y - b.y);
  let prev = -Infinity;
  ord.forEach((o) => { o.ny = Math.max(o.y, prev + minGap); prev = o.ny; });
  const over = ord[n - 1].ny - hi;
  if (over > 0) {
    let next = Infinity;
    for (let k = n - 1; k >= 0; k--) { ord[k].ny = Math.min(ord[k].ny - over, next - minGap); next = ord[k].ny; }
  }
  const under = lo - ord[0].ny;
  if (under > 0) ord.forEach((o) => { o.ny += under; });
  const out = new Array(n);
  ord.forEach((o) => { out[o.i] = o.ny; });
  return out;
}

// 19 · SLOPE / BUMP CHART — 2–4 hairline value axes, one line per item, and a set of derived
// columns the reader would otherwise have to compute: aligned label + value gutters, an
// optional RANK column at each end (so rank CHANGE is legible, usually the real story), an
// optional CHANGE column of deltas, and an optional mean/median reference rule. When one item
// is hot, every other line drops back hard (thin T.bar, T.sec labels) so the argued line is
// the only thing the eye lands on. Endpoint labels run through a de-collision pass, so items
// with near-identical values no longer overprint. Depth here is layering + derived values,
// not color: the hot item is still the single accent.
// content: { kicker, header, sub,
//            leftLabel, rightLabel,            // 2-point form (unchanged, still works)
//            columns?:[..],                    // 2–4 point form (clamp 4); wins over left/rightLabel
//            items:[{ label, left, right, values?:[..], hot? }],   // (clamp 6); values[] wins over left/right
//            showRank?=false, showDelta?=true, deltaMode?:"abs"|"pct", deltaLabel?,
//            reference?:{ value?, mode?:"mean"|"median", label? },
//            valueSuffix?, zeroBase?, source }
function slopeChart(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const items = clamp(c.items, 6);
  if (!items.length) { sourceNote(s, T, c.source); s.addNotes(c.notes || ""); return s; }

  // ---- columns: legacy two-point (left/right) OR an N-point series (values[]) ----
  const colLabels = (Array.isArray(c.columns) && c.columns.length >= 2)
    ? clamp(c.columns, 4)
    : [c.leftLabel || "Before", c.rightLabel || "After"];
  const nc = colLabels.length;
  const series = items.map((it) => {
    const raw = (Array.isArray(it.values) && it.values.length >= 2) ? it.values : [it.left, it.right];
    const v = raw.slice(0, nc).map((x) => Number(x) || 0);
    while (v.length < nc) v.push(v[v.length - 1]); // pad a short row rather than dropping the line
    return v;
  });

  const showRank = !!c.showRank;
  const showDelta = c.showDelta !== false;
  const anyHot = items.some((it) => it.hot);
  const suffix = c.valueSuffix || "";
  const fmtV = (v) => `${Math.round(v * 10) / 10}${suffix}`;

  // ---- reference rule: an explicit target, or the mean/median of the FINAL column ----
  let ref = null;
  if (c.reference) {
    const last = series.map((v) => v[nc - 1]);
    let rv = Number(c.reference.value);
    if (!Number.isFinite(rv)) {
      const so = last.slice().sort((a, b) => a - b);
      rv = c.reference.mode === "median"
        ? (so.length % 2 ? so[(so.length - 1) / 2] : (so[so.length / 2 - 1] + so[so.length / 2]) / 2)
        : last.reduce((a, b) => a + b, 0) / last.length;
    }
    ref = { v: rv, label: String(c.reference.label || (c.reference.mode === "median" ? "Median" : "Average")) };
  }

  // ---- horizontal geometry: a gutter is only reserved when its column is actually shown,
  // so turning rank/change off widens the plot instead of leaving a hole ----
  const rankW = showRank ? 0.42 : 0, deltaW = showDelta ? 1.25 : 0;
  const labX = M, labW = 2.30;
  const lvX = labX + labW + 0.08, lvW = 0.62;
  const lrX = lvX + lvW + 0.10;
  const xL = lrX + rankW + (showRank ? 0.22 : 0.30);
  const dX = W - M - deltaW, rvW = 0.66;
  const rvX = dX - (showDelta ? 0.18 : 0) - rvW;
  const rrX = rvX - rankW - (showRank ? 0.10 : 0);
  const xR = rrX - (showRank ? 0.18 : 0.22);
  const plotY = 3.15, plotH = 2.95, headY = plotY - 0.43;
  const colX = (i) => xL + (i / (nc - 1)) * (xR - xL);

  // ---- vertical scale: a slope chart reads CHANGE, so the frame is the data range with 10%
  // padding. Zero-anchoring flattens every line into the top third; zeroBase restores it. ----
  const all = series.reduce((a, v) => a.concat(v), []).concat(ref ? [ref.v] : []);
  let maxV = Math.max.apply(null, all);
  let minV = c.zeroBase ? Math.min(0, Math.min.apply(null, all)) : Math.min.apply(null, all);
  if (maxV - minV <= 0) { maxV += 1; minV -= 1; }
  const pad = c.zeroBase ? 0 : (maxV - minV) * 0.10;
  const lo = minV - pad, hi = maxV + pad, range = hi - lo;
  const yFor = (v) => plotY + plotH - ((v - lo) / range) * plotH;

  // ---- axes + column heads ----
  const spacing = (xR - xL) / Math.max(1, nc - 1);
  const headW = Math.min(2.0, spacing * 0.95);
  colLabels.forEach((lab, i) => {
    const x = colX(i);
    s.addShape("line", { x, y: plotY - 0.15, w: 0, h: plotH + 0.3, line: { color: T.hair, width: 1 } });
    s.addText(String(lab).toUpperCase(), {
      x: x - headW / 2, y: headY, w: headW, h: 0.28, align: "center",
      fontFace: T.body, bold: true, fontSize: 9, color: T.muted, charSpacing: 2, margin: 0,
    });
  });
  if (showDelta) s.addText(String(c.deltaLabel || "Change").toUpperCase(), {
    x: dX, y: headY, w: deltaW, h: 0.28, align: "center",
    fontFace: T.body, bold: true, fontSize: 9, color: T.muted, charSpacing: 2, margin: 0,
  });

  // ---- reference rule, drawn under the item lines ----
  if (ref) {
    const ry = yFor(ref.v);
    s.addShape("line", { x: xL, y: ry, w: xR - xL, h: 0, line: { color: T.hair, width: 1, dashType: "dash" } });
    s.addText(`${ref.label} ${fmtV(ref.v)}`.toUpperCase(), {
      x: xL + 0.08, y: ry + 0.03, w: 2.6, h: 0.24,
      fontFace: T.body, bold: true, fontSize: 7.5, color: T.muted, charSpacing: 1.5, margin: 0,
    });
  }

  // ---- lines + marks ----
  items.forEach((it, i) => {
    const hot = !!it.hot, v = series[i];
    const col = hot ? T.accent : T.bar;
    const lw = hot ? 2.5 : (anyHot ? 0.9 : 1.5);   // non-hot lines drop back hard when one is argued
    for (let k = 0; k < nc - 1; k++) {
      seg(s, colX(k), yFor(v[k]), colX(k + 1), yFor(v[k + 1]), { color: col, width: lw });
    }
    const r = hot ? 0.07 : 0.05;
    for (let k = 0; k < nc; k++) {
      const x = colX(k), y = yFor(v[k]);
      s.addShape("ellipse", { x: x - r, y: y - r, w: r * 2, h: r * 2, fill: { color: col }, line: { type: "none" } });
      // Only the argued line carries its interior values; the rest stay endpoint-only.
      if (hot && nc > 2 && k > 0 && k < nc - 1) {
        s.addText(fmtV(v[k]), {
          x: x - 0.6, y: y - 0.38, w: 1.2, h: 0.24, align: "center",
          fontFace: T.bodyMedium, fontSize: 9, color: T.accentText, margin: 0,
        });
      }
    }
  });

  // ---- ranks (1 = highest at that column) ----
  const rankAt = (ci) => {
    const ord = series.map((v, i) => ({ i, v: v[ci] })).sort((a, b) => b.v - a.v);
    const out = new Array(series.length);
    ord.forEach((o, k) => { out[o.i] = k + 1; });
    return out;
  };
  const rankL = showRank ? rankAt(0) : null, rankR = showRank ? rankAt(nc - 1) : null;

  // ---- labels, de-collided ----
  const gapY = 0.28, floorLo = plotY - 0.14, floorHi = plotY + plotH + 0.14;
  const yL = declutter(series.map((v) => yFor(v[0])), gapY, floorLo, floorHi);
  const yR = declutter(series.map((v) => yFor(v[nc - 1])), gapY, floorLo, floorHi);

  items.forEach((it, i) => {
    const hot = !!it.hot, v = series[i];
    const tc = hot ? T.accentText : (anyHot ? T.sec : T.ink);
    const face = hot ? T.bodyMedium : T.body;
    s.addText(String(it.label || ""), {
      x: labX, y: yL[i] - 0.14, w: labW, h: 0.28, align: "right",
      fontFace: face, fontSize: 10.5, color: tc, margin: 0, valign: "middle",
    });
    s.addText(fmtV(v[0]), {
      x: lvX, y: yL[i] - 0.14, w: lvW, h: 0.28, align: "right",
      fontFace: face, fontSize: 10.5, color: tc, margin: 0, valign: "middle",
    });
    if (showRank) s.addText(`#${rankL[i]}`, {
      x: lrX, y: yL[i] - 0.14, w: rankW, h: 0.28, align: "center",
      fontFace: T.body, fontSize: 8.5, color: hot ? T.accentText : T.muted, margin: 0, valign: "middle",
    });
    if (showRank) s.addText(`#${rankR[i]}`, {
      x: rrX, y: yR[i] - 0.14, w: rankW, h: 0.28, align: "center",
      fontFace: T.body, fontSize: 8.5, color: hot ? T.accentText : T.muted, margin: 0, valign: "middle",
    });
    s.addText(fmtV(v[nc - 1]), {
      x: rvX, y: yR[i] - 0.14, w: rvW, h: 0.28, align: "left",
      fontFace: face, fontSize: 10.5, color: tc, margin: 0, valign: "middle",
    });
    if (showDelta) {
      const d = v[nc - 1] - v[0];
      const usePct = c.deltaMode === "pct" && v[0] !== 0;
      const dv = usePct ? Math.round((d / Math.abs(v[0])) * 100) : Math.round(d * 10) / 10;
      const txt = (dv > 0 ? "+" : "") + dv + (usePct ? "%" : suffix);
      s.addShape("rect", { x: dX, y: yR[i] - 0.145, w: deltaW, h: 0.29, fill: { color: T.surface }, line: { type: "none" } });
      s.addText(txt, {
        x: dX, y: yR[i] - 0.145, w: deltaW, h: 0.29, align: "center",
        fontFace: hot ? T.bodyMedium : T.body, fontSize: 10.5, color: hot ? T.accentText : T.sec,
        margin: 0, valign: "middle",
      });
    }
  });

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 20 · COUNT CHART — a ranked count / distribution exhibit. Descending horizontal bars, rank
// numeral + category in the left gutter, the exact count floating at each bar end, and a
// DERIVED share-of-total column (plus optional running cumulative) so the reader never has to
// do the arithmetic. Holds 8–10 rows — the job chartTakeaway's 6-bar vertical cap cannot take.
// Counting/ranking is a different analytical question from change-over-time (see trendLine);
// this layout answers "how is the total distributed", so it always states its denominator.
// The layout SORTS rows descending itself and rounds the axis to a clean max, so the four
// vertical hairlines are readable values, not decoration. Exactly one row may be `hot`.
// content: { kicker, header, sub, categoryLabel, unit, rows:[{label,value,hot?}] (clamp 10),
//            total?, cumColumn?, topNote?, annotation?, source, notes }
function countChart(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const rows = clamp(c.rows, 10)
    .map((r) => ({ label: String(r.label || ""), value: Number(r.value) || 0, hot: !!r.hot }))
    .sort((a, b) => b.value - a.value);
  const n = rows.length;
  if (!n) { sourceNote(s, T, c.source); s.addNotes(c.notes || ""); return s; }

  const sum = rows.reduce((t, r) => t + r.value, 0);
  // `total` may exceed the summed rows when the tail is intentionally not charted — shares
  // then read against the true population, not against the visible subset.
  const total = Number(c.total) > 0 ? Number(c.total) : sum;
  const unit = c.unit || "items";
  const axisMax = niceCeil(Math.max(1, ...rows.map((r) => r.value)));

  const labelX = 1.35, labelW = 2.45;
  const tx = 3.95, trackW = 5.55, scale = trackW / axisMax;
  const cum = !!c.cumColumn;
  const shareX = cum ? 10.75 : 11.63, shareW = 0.85, cumX = 11.63, cumW = 0.85;
  const headY = 2.72, ruleY = 3.06, y0 = 3.2, bandBottom = 6.3;
  const rowH = Math.min(0.55, (bandBottom - y0) / n);
  const barH = Math.min(0.26, rowH * 0.55);
  const fsLabel = rowH < 0.36 ? 9.5 : 10.5;
  const gridBottom = y0 + n * rowH;

  const cap = (txt, x, y, w, align, color) => s.addText(String(txt).toUpperCase(), {
    x, y, w, h: 0.28, align, fontFace: T.body, bold: true, fontSize: 8.5,
    color: color || T.muted, charSpacing: 2, margin: 0,
  });

  // Column heads: category on the left, axis ticks across the track, derived columns right.
  // The category head is narrowed by 0.5 so it cannot run into the "0" tick, which sits at
  // tx-0.3 — at full labelW the two overlapped and read as one word.
  cap(c.categoryLabel || "Category", labelX, headY, labelW - 0.5, "right");
  cap("Share", shareX, headY, shareW, "right");
  if (cum) cap("Cum.", cumX, headY, cumW, "right");
  cap("0", tx - 0.3, headY, 0.6, "center");
  for (let k = 1; k <= 4; k++) {
    cap(String(Math.round((axisMax / 4) * k * 100) / 100), tx + (trackW / 4) * k - 0.45, headY, 0.9, "center");
  }
  s.addShape("line", { x: M, y: ruleY, w: W - 2 * M, h: 0, line: { color: T.ink, width: 1.25 } });

  // Grid BEFORE bars so the bars sit on top of it (z-order is insertion order).
  s.addShape("line", { x: tx, y: y0 - 0.02, w: 0, h: gridBottom - y0 + 0.04, line: { color: T.hair, width: 1 } });
  for (let k = 1; k <= 4; k++) {
    s.addShape("line", { x: tx + (trackW / 4) * k, y: y0 - 0.02, w: 0, h: gridBottom - y0 + 0.04, line: { color: T.hair, width: 0.75 } });
  }

  let running = 0;
  rows.forEach((r, i) => {
    const y = y0 + i * rowH, bw = Math.max(0.02, r.value * scale), hot = r.hot;
    running += r.value;
    // Rank numeral stays muted even on the hot row: the emphasis is the bar + its value,
    // not the whole line. A hot rank would read as a second mark.
    s.addText(String(i + 1).padStart(2, "0"), {
      x: M, y, w: 0.42, h: rowH, fontFace: T.body, fontSize: 9, color: T.muted, margin: 0, valign: "middle",
    });
    s.addText(r.label, {
      x: labelX, y, w: labelW, h: rowH, align: "right", fontFace: hot ? T.bodyMedium : T.body,
      fontSize: fsLabel, color: hot ? T.accentText : T.ink, margin: 0, valign: "middle",
    });
    s.addShape("rect", {
      x: tx, y: y + (rowH - barH) / 2, w: bw, h: barH,
      fill: { color: hot ? T.accent : T.bar }, line: { type: "none" },
    });
    s.addText(String(r.value), {
      x: tx + bw + 0.12, y, w: 0.9, h: rowH, fontFace: hot ? T.bodyMedium : T.body,
      fontSize: fsLabel + 0.5, color: hot ? T.accentText : T.ink, margin: 0, valign: "middle",
    });
    s.addText(`${Math.round((r.value / total) * 100)}%`, {
      x: shareX, y, w: shareW, h: rowH, align: "right", fontFace: T.bodyMedium,
      fontSize: fsLabel, color: T.sec, margin: 0, valign: "middle",
    });
    if (cum) s.addText(`${Math.round((running / total) * 100)}%`, {
      x: cumX, y, w: cumW, h: rowH, align: "right", fontFace: T.body,
      fontSize: fsLabel - 0.5, color: T.muted, margin: 0, valign: "middle",
    });
  });
  s.addShape("line", { x: tx, y: gridBottom, w: trackW, h: 0, line: { color: T.hair, width: 0.75 } });

  // Denominator line, always rendered — a distribution without its n is not evidence.
  // The concentration sentence is DERIVED from topNote so the number cannot drift from the data.
  const aY = 6.52;
  s.addShape("line", { x: M, y: aY - 0.1, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } });
  cap(`n = ${total} ${unit}`, M, aY, 2.4, "left", T.ink);
  const k = Math.min(Number(c.topNote) || 0, n);
  const note = c.annotation || (k > 0
    ? `Top ${k} of ${n} account for ${Math.round((rows.slice(0, k).reduce((t, r) => t + r.value, 0) / total) * 100)}% of all ${unit}.`
    : "");
  if (note) s.addText(note, {
    x: M + 2.55, y: aY - 0.03, w: W - M - (M + 2.55), h: 0.34,
    fontFace: T.body, fontSize: 11, color: T.sec, margin: 0, valign: "middle",
  });

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 21 · TREND LINE — a time-series exhibit built from shape segments (a polyline of `line`
// shapes between computed points), so every vertex stays draggable in PowerPoint / Slides.
// Change over time is a different analytical job from counting (see countChart): this layout
// answers "which way is it going, and since when". 1–3 series, END-OF-LINE LABELS instead of
// a legend (a legend is a tax the reader pays on every glance), optional event marker and
// optional projection tail. Baseline defaults to ZERO — a truncated y-axis exaggerates slope,
// so `yMin` is opt-in and deliberate, never automatic.
// Value labels are rationed to first + peak (hot series only); the last value rides its end label.
// NOTE: the projection tail sets `dashType: "dash"` on the line — a line PROPERTY, not a new
// shape type. If a renderer drops dashes, the tail is still marked by its boundary hairline +
// "PROJECTED" label, and `projectionStyle: "solid"` disables the dash entirely.
// content: { kicker, header, sub, xLabels:[..] (clamp 12), unit,
//            series:[{name, values:[..], hot?, color?:"secondary"}] (clamp 3),
//            yMin?, yMax?, event:{at,label}?, projectFrom?, projectionLabel?, projectionStyle?,
//            source, notes }
function trendLine(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const xs = clamp(c.xLabels, 12);
  const np = xs.length;
  const series = clamp(c.series, 3).map((sr) => ({
    name: String(sr.name || ""),
    values: (sr.values || []).slice(0, np).map((v) => Number(v) || 0),
    hot: !!sr.hot,
    color: sr.color,
  })).filter((sr) => sr.values.length >= 2);
  if (np < 2 || !series.length) { sourceNote(s, T, c.source); s.addNotes(c.notes || ""); return s; }

  // Non-hot series get a NEUTRAL TINT RAMP rather than a second hue. Muted-then-light (v1.9:
  // was sec-then-light, but the dark slate line read as a second emphasis next to the accent).
  // T.secondary is available per-series via color:"secondary" when two series genuinely need
  // separate identities — it is a second series, never a second emphasis.
  const neutrals = [T.muted, T.bar];
  let ni = 0;
  series.forEach((sr) => {
    sr.stroke = sr.hot ? T.accent
      : sr.color === "secondary" ? T.secondary
      : neutrals[Math.min(ni++, neutrals.length - 1)];
  });

  const allV = series.flatMap((sr) => sr.values);
  const dataMax = Math.max(...allV), dataMin = Math.min(...allV);
  const yMax = c.yMax != null ? Number(c.yMax) : niceCeil(dataMax);
  const yMin = c.yMin != null ? Number(c.yMin) : (dataMin < 0 ? -niceCeil(-dataMin) : 0);
  const range = Math.max(1e-6, yMax - yMin);
  const suffix = c.unit || "";

  const px = 1.7, pw = 8.15, py = 3.05, ph = 3.25;
  const yAt = (v) => py + ph - ((v - yMin) / range) * ph;
  const xAt = (i) => px + (i / (np - 1)) * pw;

  // Gridlines + y values first (behind everything), then the left axis.
  for (let k = 0; k <= 4; k++) {
    const v = yMin + (range * k) / 4, gy = yAt(v);
    s.addShape("line", { x: px, y: gy, w: pw, h: 0, line: { color: T.hair, width: k === 0 ? 1 : 0.75 } });
    s.addText(`${Math.round(v * 10) / 10}${suffix}`, {
      x: M, y: gy - 0.14, w: 0.72, h: 0.28, align: "right",
      fontFace: T.body, fontSize: 8.5, color: T.muted, margin: 0, valign: "middle",
    });
  }
  s.addShape("line", { x: px, y: py, w: 0, h: ph, line: { color: T.hair, width: 1 } });

  // X ticks: thinned to ~5 so labels never collide, and never printing the penultimate tick
  // next to the terminal one.
  const every = np <= 8 ? 1 : Math.ceil((np - 1) / 4);
  xs.forEach((lab, i) => {
    if (every > 1 && i === np - 2) return;
    if (i % every !== 0 && i !== np - 1) return;
    s.addText(String(lab).toUpperCase(), {
      x: xAt(i) - 0.55, y: py + ph + 0.1, w: 1.1, h: 0.26, align: "center",
      fontFace: T.body, bold: true, fontSize: 8.5, color: T.muted, charSpacing: 1.5, margin: 0,
    });
  });

  // Vertical markers, drawn before the series so the lines cross over them. Hairline weight
  // (v1.9: was muted — two mid-gray rules competed with the data lines for attention).
  const vRule = (idx) => {
    const mx = xAt(Math.max(0, Math.min(np - 1, Number(idx))));
    s.addShape("line", { x: mx, y: py - 0.06, w: 0, h: ph + 0.06, line: { color: T.hair, width: 1 } });
    return mx;
  };
  if (c.event && c.event.at != null) {
    const mx = vRule(c.event.at);
    if (c.event.label) s.addText(String(c.event.label).toUpperCase(), {
      x: Math.min(Math.max(mx - 1.0, M), W - M - 2.0), y: py - 0.36, w: 2.0, h: 0.26, align: "center",
      fontFace: T.body, bold: true, fontSize: 8.5, color: T.muted, charSpacing: 2, margin: 0,
    });
  }
  const pf = c.projectFrom != null ? Number(c.projectFrom) : null;
  if (pf != null) {
    const mx = vRule(pf);
    // Centred on its own rule, matching how the event marker is labelled. Right-anchoring it to
    // the plot edge drifted the caption more than an inch off the rule it names, so it read as
    // labelling the final gridline instead. Two markers of one kind get one anchoring rule.
    s.addText(String(c.projectionLabel || "Projected").toUpperCase(), {
      x: Math.min(Math.max(mx - 1.0, M), W - M - 2.0), y: py - 0.36, w: 2.0, h: 0.26, align: "center",
      fontFace: T.body, bold: true, fontSize: 8.5, color: T.muted, charSpacing: 2, margin: 0,
    });
  }

  series.forEach((sr) => {
    const vs = sr.values, m = vs.length;
    for (let i = 0; i < m - 1; i++) {
      const projected = pf != null && i >= pf;
      const ln = {
        color: projected && !sr.hot ? T.bar : sr.stroke,
        width: sr.hot ? (projected ? 1.5 : 2.25) : (projected ? 1 : 1.25),
      };
      if (projected && c.projectionStyle !== "solid") ln.dashType = "dash";
      seg(s, xAt(i), yAt(vs[i]), xAt(i + 1), yAt(vs[i + 1]), ln);
    }
    // Dots ride the HOT series only (v1.9: was every series when short — three dotted lines
    // read as three emphases; context lines now stay bare and quiet).
    if (sr.hot) vs.forEach((v, i) => {
      const r = 0.055;
      s.addShape("ellipse", { x: xAt(i) - r, y: yAt(v) - r, w: r * 2, h: r * 2, fill: { color: sr.stroke }, line: { type: "none" } });
    });
  });

  // End-of-line labels, de-collided by pushing overlapping terminals apart.
  const ends = series.map((sr) => ({ sr, y: yAt(sr.values[sr.values.length - 1]), v: sr.values[sr.values.length - 1] }))
    .sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) {
    if (ends[i].y - ends[i - 1].y < 0.3) ends[i].y = ends[i - 1].y + 0.3;
  }
  const lx = px + pw + 0.16;
  ends.forEach((e) => {
    s.addText(`${e.sr.name}  ${e.v}${suffix}`, {
      x: lx, y: e.y - 0.15, w: W - M - lx, h: 0.3,
      fontFace: e.sr.hot ? T.bodyMedium : T.body, fontSize: e.sr.hot ? 11.5 : 10.5,
      color: e.sr.hot ? T.accentText : (e.sr.stroke === T.bar ? T.sec : e.sr.stroke),
      margin: 0, valign: "middle",
    });
  });

  // Hot series only: label the start and an INTERIOR peak. The terminal value already rides
  // its end label, so printing every point would just restate the line.
  const hotS = series.find((sr) => sr.hot);
  if (hotS && hotS.values.length >= 3) {
    const vs = hotS.values, last = vs.length - 1, peak = vs.indexOf(Math.max(...vs));
    s.addText(`${vs[0]}${suffix}`, {
      x: xAt(0) - 0.08, y: yAt(vs[0]) - 0.36, w: 1.0, h: 0.28,
      fontFace: T.body, fontSize: 10, color: T.accentText, margin: 0,
    });
    if (peak !== 0 && peak !== last) s.addText(`${vs[peak]}${suffix}`, {
      x: xAt(peak) - 0.5, y: Math.max(py - 0.34, yAt(vs[peak]) - 0.36), w: 1.0, h: 0.28, align: "center",
      fontFace: T.body, fontSize: 10, color: T.accentText, margin: 0,
    });
  }

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

// 22 · WORKFLOW MAP (Mode 2, swimlane) — players are lanes, stages are columns, steps sit in the
// cells, and the signature mark is the HANDOFF: an arrow that crosses lanes where work changes
// hands. A flat left-to-right chain belongs in `stepLine`; this layout only earns its place when
// work changes owner. Each step declares who does it — human / hybrid / ai — as a three-step tint
// ramp (paper → surface → house tint) PLUS a left-edge tick, so the "here is what the agent takes
// over" read survives greyscale printing and the legend decodes it. Arrow weight carries the
// second hierarchy: within-lane flow is light T.muted, a cross-lane handoff is heavier T.sec.
// Accent is spent on exactly one `hot` step (solid fill + onFill text, same treatment as
// timelineGantt's hot lane).
//
// ELBOW connectors, not diagonals — justified: pptxgenjs CAN draw a true diagonal (slopeChart
// does), but a diagonal across a dense swimlane slices through intermediate lanes and unrelated
// boxes. Routed elbows keep every segment axis-aligned, so each arrow is the exact `line` +
// endArrowType shape `architecture` already ships and LibreOffice already exports. The vertical
// leg deliberately runs down the column separator (the gutter midpoint): a reader already expects
// a stage transition there, so the handoff reads as orderly routing rather than a stray crossing.
//
// content: { kicker, header, sub,
//            lanes:[{ name, role? }]                                   (≤ 5, top to bottom)
//            stages:[{ name, dur? }]                                   (≤ 6, left to right)
//            steps:[{ lane, stage, span?=1, label, note?,
//                     mode?("human"|"hybrid"|"ai"), hot? }]            (≤ 14)
//            handoffs:[{ from, to, label? }]                           (≤ 9; from/to = steps[] idx)
//            zebra?, cycleLabel?, legendLabels?, source }
function workflowMap(pres, T, ctx, c) {
  const s = slide(pres, T, ctx);
  headerBlock(s, T, c, { hs: 22, hh: 1.1, sh: 0.55 });

  const lanes  = clamp(c.lanes, 5);
  const stages = clamp(c.stages, 6);
  const steps  = clamp(c.steps, 14);
  const hands  = clamp(c.handoffs, 9);
  if (!lanes.length || !stages.length) {
    console.warn("layouts WARNING: workflowMap needs both `lanes` and `stages`; rendered empty.");
    sourceNote(s, T, c.source); s.addNotes(c.notes || ""); return s;
  }

  // ---- geometry: rail | stage grid. The lane block grows down from gy, the cycle-time row
  // tucks under whatever height it lands at, and the legend is pinned to the bottom.
  const railW = 1.60, gx = M + railW, gw = W - M - gx, colW = gw / stages.length;
  const hdrY = 2.72, ruleY = 3.04, gy = 3.12;
  const hasDur = stages.some((st) => st.dur);
  const rowH = Math.min(0.92, ((hasDur ? 6.06 : 6.38) - gy) / lanes.length);
  const blockH = rowH * lanes.length, laneBot = gy + blockH;
  const stepH = Math.max(0.34, rowH - 0.20), pad = (rowH - stepH) / 2, inset = 0.16;
  const showNote = stepH >= 0.50;

  const sx = (st) => gx + st.stage * colW + inset;
  const sw = (st) => Math.max(0.5, (st.span || 1) * colW - inset * 2);
  const sy = (st) => gy + st.lane * rowH + pad;

  // ---- optional zebra, drawn first so every rule sits on top ----
  if (c.zebra) lanes.forEach((_, i) => {
    if (i % 2 === 1) s.addShape("rect", { x: M, y: gy + i * rowH, w: W - 2 * M, h: rowH, fill: { color: T.surface }, line: { type: "none" } });
  });

  // ---- stage headers, ink header rule, column separators ----
  stages.forEach((st, i) => {
    s.addText(String(st.name || "").toUpperCase(), {
      x: gx + i * colW, y: hdrY, w: colW, h: 0.28, align: "center",
      fontFace: T.body, bold: true, fontSize: 9, color: T.muted, charSpacing: 2, margin: 0,
    });
    if (i > 0) s.addShape("line", { x: gx + i * colW, y: gy, w: 0, h: blockH, line: { color: T.hair, width: 0.75 } });
  });
  s.addShape("line", { x: M, y: ruleY, w: W - 2 * M, h: 0, line: { color: T.ink, width: 1.25 } });
  s.addShape("line", { x: gx, y: gy, w: 0, h: blockH, line: { color: T.hair, width: 1 } });

  // ---- lane rail (player, optional role) + row separators ----
  lanes.forEach((ln, i) => {
    const y = gy + i * rowH, two = !!ln.role && rowH >= 0.62;
    // 8.5pt / 1.2 tracking: at 9pt / 2 a two-word player name ("LEAD CONSULTANT") exceeded the
    // 1.42in rail, wrapped to a second line, and overprinted its own role caption.
    s.addText(String(ln.name || "").toUpperCase(), {
      x: M, y: two ? y + pad : y, w: railW - 0.18, h: two ? 0.26 : rowH,
      fontFace: T.body, bold: true, fontSize: 8.5, color: T.ink, charSpacing: 1.2, margin: 0,
      valign: two ? "top" : "middle",
    });
    if (two) s.addText(String(ln.role), {
      x: M, y: y + pad + 0.25, w: railW - 0.18, h: 0.24,
      fontFace: T.body, fontSize: 8, color: T.muted, margin: 0, valign: "top",
    });
    if (i < lanes.length - 1) s.addShape("line", { x: M, y: y + rowH, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } });
  });
  s.addShape("line", { x: M, y: laneBot, w: W - 2 * M, h: 0, line: { color: T.hair, width: 0.75 } });

  // ---- mode treatment: tint ramp + left-edge tick. `hot` spends the single accent, but keeps
  // a knocked-out tick so the most important step doesn't silently lose its human/AI encoding.
  const modeStyle = (mode, hot) => {
    // T.band, NOT T.accent: this fill carries white text. On casper the two tokens are the same
    // purple so accent looked fine; on sphera the accent is a light teal and white-on-teal fell
    // to 2.06:1. themes.js defines band as "dark fill that carries WHITE text" — use it.
    const on = onFill(T.band, T);
    if (hot) return { fill: T.band, line: { type: "none" }, text: on, note: on,
                      tick: (mode === "ai" || mode === "hybrid") ? on : null, face: T.body, bold: true };
    if (mode === "ai") return { fill: T.cat.data.b, line: { type: "none" }, text: T.cat.data.t,
                                note: T.sec, tick: T.cat.data.t, face: T.bodyMedium, bold: false };
    if (mode === "hybrid") return { fill: T.surface, line: { color: T.hair, width: 0.75 }, text: T.ink,
                                    note: T.sec, tick: T.bar, face: T.bodyMedium, bold: false };
    return { fill: T.paper, line: { color: T.hair, width: 0.75 }, text: T.ink,
             note: T.sec, tick: null, face: T.bodyMedium, bold: false };
  };

  // ---- steps ----
  steps.forEach((st) => {
    const m = modeStyle(st.mode, st.hot);
    const x = sx(st), y = sy(st), w = sw(st), h = stepH, tx = x + 0.16, tw = w - 0.30;
    s.addShape("rect", { x, y, w, h, fill: { color: m.fill }, line: m.line });
    if (m.tick) s.addShape("rect", { x, y, w: 0.055, h, fill: { color: m.tick }, line: { type: "none" } });
    if (showNote && st.note) {
      s.addText(st.label || "", {
        x: tx, y: y + 0.04, w: tw, h: h - 0.26, fontFace: m.face, bold: m.bold, fontSize: 9.5,
        color: m.text, margin: 0, lineSpacingMultiple: 1.1, valign: "top",
      });
      s.addText(String(st.note), {
        x: tx, y: y + h - 0.22, w: tw, h: 0.19, fontFace: T.body, fontSize: 7.5,
        color: m.note, margin: 0, valign: "top",
      });
    } else {
      s.addText(st.label || "", {
        x: tx, y, w: tw, h, fontFace: m.face, bold: m.bold, fontSize: 9.5,
        color: m.text, margin: 0, lineSpacingMultiple: 1.1, valign: "middle",
      });
    }
  });

  // ---- handoffs: the whole reason this layout exists ----
  hands.forEach((h) => {
    const a = steps[h.from], b = steps[h.to];
    if (!a || !b) {
      console.warn(`layouts WARNING: workflowMap handoff ${h.from} → ${h.to} points at a missing step index; DROPPED. Check steps[] indices in content.js.`);
      return;
    }
    const cross = a.lane !== b.lane;
    const col = cross ? T.sec : T.muted, wt = cross ? 1.75 : 1.25;
    const aR = sx(a) + sw(a), bL = sx(b), aY = sy(a) + stepH / 2, bY = sy(b) + stepH / 2;
    let lx, ly, leftOfLeg = false;

    if (!cross) {
      // same lane: one horizontal segment, light weight — flow, not a handoff.
      s.addShape("line", { x: aR, y: aY, w: Math.max(0.08, bL - aR), h: 0, line: { color: col, width: wt, endArrowType: "triangle" } });
      lx = (aR + bL) / 2; ly = aY - 0.28;
    } else if (bL - aR >= 0.24) {
      // H → V → H elbow. Vertical leg rides the column separator (the gutter midpoint).
      const mx = (aR + bL) / 2;
      s.addShape("line", { x: aR, y: aY, w: mx - aR, h: 0, line: { color: col, width: wt } });
      seg(s, mx, aY, mx, bY, { color: col, width: wt });
      s.addShape("line", { x: mx, y: bY, w: bL - mx, h: 0, line: { color: col, width: wt, endArrowType: "triangle" } });
      // Label hangs to the LEFT of the vertical leg. Centred on the leg, the plate reached
      // 0.37in into the destination column and covered the first step box there.
      lx = mx; ly = (aY + bY) / 2 - 0.13; leftOfLeg = true;
    } else {
      // Boxes stack in the same column: a straight vertical drop between the facing edges.
      const o0 = Math.max(sx(a), sx(b)), o1 = Math.min(aR, bL + sw(b));
      const vx = o1 > o0 ? (o0 + o1) / 2 : sx(b) + sw(b) / 2;
      const down = bY > aY;
      const y0 = down ? sy(a) + stepH : sy(a), y1 = down ? sy(b) : sy(b) + stepH;
      // Draw from the MIN corner with a positive extent and carry direction on the arrow head.
      // An upward handoff previously emitted a negative `h`, which does not export reliably —
      // it rendered short of its target box and read as a broken connector. Same fix the
      // architecture layout already carries for its `up`/`left` arrows.
      const ln = { color: col, width: wt };
      ln[down ? "endArrowType" : "beginArrowType"] = "triangle";
      s.addShape("line", { x: vx, y: Math.min(y0, y1), w: 0, h: Math.abs(y1 - y0), line: ln });
      lx = vx; ly = (y0 + y1) / 2 - 0.13;
    }

    if (h.label) {
      // Paper knockout so the label stays legible where it crosses a row hairline or a separator.
      const txt = String(h.label).toUpperCase(), lw = Math.max(0.5, 0.18 + txt.length * 0.062);
      const kl = Math.max(0, Math.min(lanes.length - 1, Math.floor((ly + 0.13 - gy) / rowH)));
      const knock = c.zebra && kl % 2 === 1 ? T.surface : T.paper;
      const px2 = leftOfLeg ? lx - lw - 0.05 : lx - lw / 2;
      s.addShape("rect", { x: px2, y: ly, w: lw, h: 0.26, fill: { color: knock }, line: { type: "none" } });
      s.addText(txt, {
        x: px2, y: ly, w: lw, h: 0.26, align: leftOfLeg ? "right" : "center", fontFace: T.body, bold: true,
        fontSize: 7.5, color: col, charSpacing: 1.5, margin: 0, valign: "middle",
      });
    }
  });

  // ---- per-stage cycle time, tucked under the lane block (opt-in via stage.dur) ----
  if (hasDur) {
    const dy = laneBot + 0.10;
    s.addText(String(c.cycleLabel || "Cycle time").toUpperCase(), {
      x: M, y: dy, w: railW - 0.18, h: 0.24, fontFace: T.body, bold: true, fontSize: 8,
      color: T.muted, charSpacing: 2, margin: 0, valign: "middle",
    });
    stages.forEach((st, i) => {
      if (!st.dur) return;
      s.addText(String(st.dur).toUpperCase(), {
        x: gx + i * colW, y: dy, w: colW, h: 0.24, align: "center", fontFace: T.body,
        fontSize: 8.5, color: T.sec, charSpacing: 1, margin: 0, valign: "middle",
      });
    });
  }

  // ---- legend: only decodes modes the steps actually use, and only when ≥2 differ
  // (same principle as architecture's category legend — a legend that decodes nothing is noise).
  const used = [];
  steps.forEach((st) => { const m = st.mode || "human"; if (!used.includes(m)) used.push(m); });
  if (used.length > 1) {
    const names = Object.assign({ human: "Human", hybrid: "Human + AI", ai: "AI-assisted" }, c.legendLabels || {});
    let lx2 = M;
    ["human", "hybrid", "ai"].filter((m) => used.includes(m)).forEach((m) => {
      const ms = modeStyle(m, false), label = String(names[m] || m).toUpperCase();
      // Advance is measured off the ACTUAL label width. The old fixed 1.9in text box with a
      // short advance let the next (opaque) swatch print over the previous label's tail.
      const tw2 = 0.08 + label.length * 0.095;
      s.addShape("rect", { x: lx2, y: 6.55, w: 0.30, h: 0.22, fill: { color: ms.fill }, line: ms.line });
      if (ms.tick) s.addShape("rect", { x: lx2, y: 6.55, w: 0.05, h: 0.22, fill: { color: ms.tick }, line: { type: "none" } });
      s.addText(label, {
        x: lx2 + 0.38, y: 6.53, w: tw2, h: 0.26, fontFace: T.body, bold: true, fontSize: 8,
        color: T.muted, charSpacing: 1.5, margin: 0, valign: "middle",
      });
      lx2 += 0.38 + tw2 + 0.34;
    });
  }

  sourceNote(s, T, c.source);
  s.addNotes(c.notes || "");
  return s;
}

const layouts = {
  cover, sectionDivider, contentColumns, comparison, numberedChallenges, agenda,
  chartTakeaway, countChart, waterfall, matrix2x2, slopeChart,
  trendLine, timelineGantt, stepLine, workflowMap, architecture, roadmap, roadmapTrack, manifesto,
  quote, sources, closing,
};

module.exports = { layouts, helpers: { slide, headerBlock, sourceNote, clamp, luminance, onFill }, W, H, M };
