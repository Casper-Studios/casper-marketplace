---
name: casper-design-system
description: >
  Casper Studios internal design system for generating consistent, production-grade SaaS UI.
  Use this skill whenever generating UI code for internal tools, client apps, dashboards,
  POCs, prototypes, or any visual interface — even quick mockups or artifacts. Apply it
  any time the output is a React component, page, or layout. If the user mentions "our
  design system", "Casper style", "match our look", or asks you to build any kind of app
  or interface, use this skill. Also trigger when restyling or theming existing UI to match
  Casper's visual language. This skill takes priority over generic frontend-design guidance.
---

# Casper Studios Design System

A clean, elevated SaaS design system built on **shadcn/ui**, **Tailwind CSS v4**, and **React (Vite)**. Every interface generated for Casper Studios — whether a client demo, internal tool, or quick prototype — must follow these rules to maintain a consistent, professional visual identity across the team.

Before generating any UI code, read this file completely. Reference files are split by concern — load only what you need:

- **`references/layouts.md`** — Page scaffolding: app shell, sidebar nav, dashboard grid, data table page, page header. Read when building a new page or restructuring layout.
- **`references/components.md`** — Reusable pieces: stat cards, list items, filter bars, kanban boards, profile cards, product cards, activity feeds. Read when implementing specific UI elements inside a layout.
- **`references/theme.css`** — Tailwind CSS v4 theme tokens. Copy this file into your project as-is.

---

## Summary

The Casper aesthetic is **clean authority** — a professional SaaS style that feels premium without trying too hard. It uses generous whitespace, a restrained purple accent, and soft rounded surfaces to create interfaces that feel trustworthy and modern. Think Linear meets Notion: structured, breathable, quietly confident.

---

## Core Principles

1. **Whitespace is a feature.** Generous padding, breathing room between sections. Never cram.
2. **One accent, used sparingly.** Brand purple (`#5900FF`) appears on active states, primary buttons, and key CTAs — nowhere else. If everything is purple, nothing is.
3. **Rounded but not bubbly.** 16px default radius. Feels modern without feeling like a toy.
4. **Flat with depth hints.** No heavy shadows. Use `shadow-sm` for cards, `shadow-md` for popovers. Never use `shadow-lg` on in-page elements.
5. **Content over chrome.** The UI should disappear. Users notice the data, not the design.

---

## Tech Stack

- **React** (Vite) with TypeScript
- **Tailwind CSS v4** — Use the theme file at `references/theme.css` as-is
- **shadcn/ui** — Use components from the library directly. Do NOT create custom base components that duplicate shadcn functionality
- **Lucide React** — Icon library. Always use Lucide, never Heroicons or FontAwesome
- **Fonts** — `Public Sans` for all UI text. Load via Google Fonts or bundle

---

## Color System

The palette is intentionally restrained. Most of the UI is neutral gray + white, with purple as a sharp accent.

### Usage Rules

| Role | Token | Hex | When to use |
|---|---|---|---|
| **Brand accent** | `brand-500` | `#5900FF` | Active nav items, primary buttons, links, focus rings |
| **Brand subtle** | `brand-50` | `#EEE5FF` | Active nav background, selected row highlight, hover tints |
| **Brand light** | `brand-100` | `#DECCFF` | Icon circle backgrounds, soft tag fills |
| **Default text** | `neutral-950` | `#0A0A0A` | Page titles, headings |
| **Body text** | `neutral-900` | `#171717` | Primary body text |
| **Subtext** | `neutral-500` | `#737373` | Metadata, timestamps, secondary labels |
| **Borders** | `neutral-200` | `#E5E5E5` | Card borders, dividers, table lines |
| **Surface** | `neutral-50` | `#FAFAFA` | Page background behind cards |
| **Card surface** | `white` | `#FFFFFF` | Card backgrounds, panels |

### Semantic Colors

Use these ONLY for status indicators, badges, and contextual feedback — never as decorative accents.

- **Success** — `success-500` (`#22C55E`) for badges/icons, `success-50` for pill backgrounds
- **Error** — `error-500` (`#EF4444`) for badges/icons, `error-50` for pill backgrounds
- **Warning** — `warning-500` (`#F59E0B`) for badges/icons, `warning-50` for pill backgrounds

### What NOT to do

- Do NOT use brand purple for backgrounds on large surfaces
- Do NOT use semantic colors decoratively
- Do NOT introduce new colors. If you need a new shade, use the neutral scale
- Do NOT use opacity-based colors when a token exists (e.g., don't do `text-black/50`, use `neutral-500`)

---

## Typography

All text is set in **Public Sans**. No other font family. Monospace (`font-mono`) is acceptable for code blocks, data labels, and IDs only.

### Scale

| Style | Size | Weight | Line Height | Use |
|---|---|---|---|---|
| **Heading 1** | 30px | 500 | 36px | Page titles only. One per view. |
| **Heading 2** | 20px | 500 | 24px | Section titles within a page |
| **Heading 3** | 16px | 500 | 20px | Card titles, subsection labels |
| **Body** | 14px | 400 | 20px | Default paragraph and UI text |
| **Body Bold** | 14px | 500 | 20px | Emphasis within body text, table headers |
| **Caption** | 12px | 400 | 16px | Timestamps, helper text, metadata |
| **Caption Bold** | 12px | 500 | 16px | Badge labels, small category tags |

### Rules

- Headings are always `medium` weight (500), never bold (700)
- NEVER use all-caps except for tiny metadata labels (e.g., "STATUS", "OWNER" in table column headers) set at caption size
- Links use `brand-500` color with no underline by default, underline on hover
- Do NOT vary font size beyond this scale. If something feels wrong, adjust spacing not font size

---

## Spacing & Layout

### Spacing Scale

Use Tailwind's default spacing scale. Key values:

- `4px` (p-1) — icon padding, tight gaps
- `8px` (p-2) — badge padding, small gaps
- `12px` (p-3) — input padding, card internal gaps
- `16px` (p-4) — card padding, section gaps
- `24px` (p-6) — between cards, content sections
- `32px` (p-8) — major section separation
- `48px` (p-12) — page-level padding on large screens

### Layout Rules

- Page background: `neutral-50` (`#FAFAFA`)
- Content is always organized inside **Cards** (white background, border, rounded)
- Maximum content width: `1280px` centered
- On pages with a sidebar, sidebar is `240px` fixed width
- Main content area uses remaining space with `24px` padding

---

## Shadows & Elevation

The design is predominantly flat. Shadows are used to indicate layers, not to add decoration.

| Token | Use |
|---|---|
| `shadow-sm` | Cards, inputs at rest |
| `shadow-default` | Same as sm — default for most elements |
| `shadow-md` | Dropdown menus, popovers, tooltips |
| `shadow-lg` | Modals, command palettes, overlays ONLY |

NEVER apply `shadow-lg` or `shadow-overlay` to cards or in-page elements.

---

## Border Radius

| Token | Value | Use |
|---|---|---|
| `radius-sm` | 8px | Inputs, small buttons, inner elements |
| `radius-md` / `radius-DEFAULT` | 16px | Cards, panels, large containers |
| `radius-lg` | 24px | Modal containers, hero cards |
| `radius-full` | 9999px | Badges, pills, avatars, icon circles |

Cards always use `radius-md` (16px). Nested elements inside cards should use `radius-sm` (8px) to maintain visual hierarchy — the inner radius should always be smaller than the outer.

---

## Iconography

- Use **Lucide React** exclusively. Import as: `import { IconName } from "lucide-react"`
- Default icon size: `16px` for inline, `20px` for standalone
- Icon color follows its text context (e.g., `neutral-500` for subtext, `brand-500` for active)
- For icons inside circular backgrounds (common in lists and dashboards):
  - Circle: `40px` diameter, `brand-50` or `brand-100` background, `rounded-full`
  - Icon: `20px`, `brand-500` color
  - For semantic contexts, swap to the matching semantic color pair (e.g., `error-50` bg + `error-500` icon)

---

## shadcn/ui Component Theming

Use shadcn/ui components as your base layer. Theme them using the CSS variables in `references/theme.css`. Here is how specific components should be configured:

### Button

- **Primary**: `brand-500` bg, white text, `radius-sm`. Hover: `brand-600`.
- **Secondary**: White bg, `neutral-200` border, `neutral-900` text. Hover: `neutral-50` bg.
- **Ghost**: No bg, no border. `neutral-600` text. Hover: `neutral-100` bg.
- **Destructive**: `error-500` bg, white text.
- All buttons: `radius-sm` (8px), height `36px` (default), `14px` font.

### Badge

- `radius-full` (pill shape). Height `22px`. Caption-bold text (12px, 500 weight).
- **Semantic badges**: Use pastel bg + darker text. E.g., success badge = `success-50` bg, `success-700` text.
- **Neutral badge**: `neutral-100` bg, `neutral-700` text.
- **Brand badge**: `brand-50` bg, `brand-700` text.
- Always include a small dot or icon before the label when indicating status.

### Card

- White background. `1px` `neutral-200` border. `radius-md` (16px). `shadow-sm`.
- Internal padding: `16px` minimum, `24px` for spacious cards.
- Card headers: `Heading 3` (16px/500) with optional "View all" link aligned right.
- Separate header from content with a `1px` `neutral-200` divider.

### Table

- Use shadcn `<Table>`. No outer border on the table itself — let the parent Card provide the container.
- Column headers: Caption-bold (12px/500), `neutral-500` color, uppercase.
- Row height: `48-56px`. Rows separated by `1px` `neutral-200` bottom border.
- Row hover: `neutral-50` background.
- No alternating row colors.

### Input / Textarea

- `radius-sm` (8px). `1px` `neutral-200` border. `neutral-50` bg or white bg.
- Focus: `2px` `brand-500` ring (use Tailwind `ring-2 ring-brand-500`).
- Placeholder text: `neutral-400`.
- Height: `36px` for default inputs.

### Sidebar (App Shell)

- Width: `240px`. White background. Right border: `1px` `neutral-200`.
- Logo/icon area at top: `48px` height, `16px` horizontal padding.
- Nav items: `36px` height, `8px` radius (radius-sm), `12px` left padding.
  - Default: `neutral-600` text, Lucide icon + label.
  - Active: `brand-50` bg, `brand-500` text, `font-weight: 500`.
  - Hover: `neutral-100` bg.
- Group labels: Caption (12px/400), `neutral-400` color, `24px` top margin between groups.
- Groups: Main navigation, Analytics, Settings (or contextual groupings).
- On mobile: Sidebar collapses to a `Sheet` (slide-in from left).

### Tabs

- Use shadcn `<Tabs>`. Underline variant.
- Active tab: `brand-500` bottom border (2px), `neutral-900` text.
- Inactive tab: no border, `neutral-500` text. Hover: `neutral-900` text.

### Dialog / Sheet

- Overlay: `black/50` opacity.
- Container: white bg, `radius-lg` (24px), `shadow-overlay`.
- Always include a close button (X icon) top-right.

---

## Composite Patterns

For detailed code examples and composite definitions, read the appropriate reference file:

- **`references/layouts.md`** — App Shell, Sidebar Navigation, Dashboard Grid, Data Table Page, Page Header
- **`references/components.md`** — Stat Card, List Item Row, Filter Bar, Kanban Board, Profile/Discovery Card, Product Card, Activity Feed Item

---

## Responsive Behavior

- **Desktop** (≥1024px): Sidebar visible, content in multi-column grid
- **Tablet** (768–1023px): Sidebar collapsed to icons or hidden, content adjusts to fewer columns
- **Mobile** (<768px): Sidebar hidden (accessible via hamburger → Sheet), single-column layout, cards stack vertically

Key rules:
- Cards go full-width on mobile
- Filter pills scroll horizontally on mobile
- Tables become scrollable horizontally or switch to a card/list view
- Reduce padding from `24px` to `16px` on mobile

---

## Image Placeholders

When no real image is available, use **soft gradient mesh backgrounds** — NOT gray boxes. These should feel like abstract art, not loading states.

Gradient recipes (CSS `linear-gradient` or `radial-gradient` combos):

- **Mint/Teal**: `linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #a8edea 100%)`
- **Peach/Coral**: `linear-gradient(135deg, #f6d5c5 0%, #e8b4b8 50%, #d4a0a0 100%)`
- **Purple/Pink**: `linear-gradient(135deg, #c3b1e1 0%, #f0c4d0 50%, #e0aed0 100%)`
- **Teal/Emerald**: `linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)`

Apply `radius-md` to image containers. These are placeholders — they should look intentional and beautiful.

---

## Anti-Patterns (Do NOT)

- **No gradients on buttons.** Flat solid colors only.
- **No colored page backgrounds.** Background is always `neutral-50` or `white`.
- **No heavy borders.** Max `1px` for structural borders. Never 2px+.
- **No rounded-full on cards.** Cards are `radius-md` (16px), never circles.
- **No custom fonts.** Public Sans only. Monospace for code.
- **No icon-only navigation** on desktop. Always show icon + label in the sidebar.
- **No dark mode** unless explicitly requested. Default is always light.
- **No animated skeletons or shimmer effects** in static mockups.
- **No drop shadows on text.** Ever.
- **No border-radius mixing.** Don't put `rounded-lg` next to `rounded-sm` at the same hierarchy level.

---

## File Structure Convention

When generating a new page or component:

```
src/
├── components/
│   ├── ui/              ← shadcn components (do not modify)
│   ├── layout/          ← App shell, sidebar, top bar
│   └── [feature]/       ← Feature-specific composites
├── pages/               ← Full page compositions
├── lib/
│   └── utils.ts         ← cn() helper and utilities
└── styles/
    └── theme.css        ← Casper theme tokens (from references/theme.css)
```

Always use the `cn()` utility from shadcn for conditional class merging.

---

## Checklist Before Output

Before delivering any UI code, verify:

- [ ] Uses `Public Sans` font family
- [ ] Brand purple only on interactive/active elements
- [ ] Cards have white bg + `neutral-200` border + `radius-md` + `shadow-sm`
- [ ] Sidebar follows the 240px / grouped nav / active state pattern
- [ ] No unauthorized colors, fonts, or shadows
- [ ] Responsive: works at 1280px, 768px, and 375px
- [ ] All icons from Lucide React
- [ ] shadcn components used where available (not custom recreations)
- [ ] Spacing feels generous — nothing cramped
- [ ] Page background is `neutral-50`, not white
