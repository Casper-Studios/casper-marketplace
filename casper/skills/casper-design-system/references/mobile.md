# Mobile Application Patterns

Code examples, rules, and structural patterns for mobile app interfaces. This file is self-contained — read it whenever the project is a **mobile application**, **native app**, **iOS app**, **Android app**, or any variant that implies a phone-based experience.

**Why this file exists:** Most AI code-generation tools default to web layouts. When someone says "mobile app," they don't want a responsive webpage — they want something that looks like it's running on a phone. The device frame, the touch-sized inputs, the pinned bottom button — these details are what separate "shrunk-down website" from "this actually feels like an app."

> **Dark mode note:** The code examples below use `bg-white` for surfaces (top bars, tab bars, cards). This is correct for light mode (the default). If dark mode is requested, swap `bg-white` to `bg-neutral-0` on all surfaces so they invert correctly via the `.dark` class. See the Dark Mode section in SKILL.md for full guidance.

---

## Mobile Rules

These rules govern every mobile app output. The code examples in the sections below implement these rules — refer to them for copy-paste patterns.

### Device Frame (Non-Negotiable)

Every mobile app output MUST be rendered inside a device frame that simulates an **iPhone 16**:

- **Viewport size**: `393px` wide × `852px` tall — always, no exceptions
- **Outer frame**: `border-radius: 40px`, `border: 8px solid #1a1a1a` (simulates the phone bezel)
- **Inner content area**: `border-radius: 20px`, `overflow-y: auto`, `overflow-x: hidden`
- **Page behind the phone**: Use `neutral-100` or a subtle gradient so the device frame stands out as an object on the canvas
- Center the device frame horizontally on the page

### Mobile Form Inputs

All global form input rules from SKILL.md apply (visible external labels, de-emphasized placeholders, label-above pattern). The only mobile-specific override is height:

- **Input height**: `48px` (`h-12`) minimum for comfortable touch targets — larger than the web default (`36px`)

### Mobile Button Height

All buttons in mobile contexts use `48px` (`h-12`) — matching the input height. This is larger than the web default (`36px`) because fingers need bigger targets than cursors. This applies to all button variants: primary, secondary, ghost, and destructive.

### Primary Action Button (Pinned to Bottom)

The main CTA on every mobile screen MUST be pinned to the bottom of the viewport for ergonomic thumb reachability:

- **Position**: Place the button container as the last child in the flex column layout (after the `flex-1 overflow-y-auto` content area), with `shrink-0` so it never collapses. Use `16px` horizontal padding and `16px` bottom padding
- **Width**: Full width minus padding
- **Safe area**: Add `pb-6` (24px) below the button to account for the home indicator on modern iPhones
- **Keyboard behavior**: When a text input is focused, the button should remain visible above the keyboard. The `shrink-0` flex child approach inside a `flex flex-col` container achieves this naturally
- **Visual separation**: Add `border-t border-neutral-200` or a `shadow-md` on the pinned container so scrollable content doesn't visually bleed into the button area

### Mobile Navigation

Mobile apps do NOT use a persistent sidebar visible alongside content. The primary navigation pattern is a bottom tab bar:

- **Bottom tab bar**: 5 tabs max, icon + label, `56px` height, pinned to bottom above the safe area
- **Active tab**: `brand-500` icon + text. Inactive: `neutral-400`
- **Top bar**: Screen title, optional back arrow left, optional action icon right. Height: `44px`
- The tab bar sits below the primary action button's safe area — they should never overlap

**When there are more than 5 top-level destinations:** Use a slide-out navigation panel triggered by a hamburger icon in the top bar. This panel overlays the content as a modal-style `Sheet` (slides in from the left, `black/50` overlay behind it). It is not a persistent sidebar — it opens on demand and closes when the user taps away or selects a destination. The bottom tab bar can still hold the 4–5 most important items, with a "More" tab or the hamburger providing access to the rest.

### Mobile Typography

Phone screens are physically smaller — the web heading scale feels oversized:

- **Heading 1**: `24px` (instead of 30px)
- **Heading 2**: `18px` (instead of 20px)
- All other sizes remain unchanged

### Mobile Spacing

- Page padding: `16px` horizontal, `12px` top (below the top bar)
- Card internal padding: `16px`
- Between cards/sections: `12px`
- Density target: think iOS Settings app — snug but breathable

### Contextual Actions (Menus & Bottom Sheets)

When a button or trigger presents multiple options on mobile, use one of two patterns depending on the complexity:

**Contextual Menu** — for short, simple option lists (3–6 actions like "Edit", "Share", "Delete"). Use shadcn's `DropdownMenu` component. It appears adjacent to the trigger, floating above content. Keep it minimal — if the options need descriptions, icons with labels, or scrolling, use a bottom sheet instead.

**Bottom Sheet** — for richer option sets, confirmations, or any content that benefits from more space. The sheet slides up from the bottom of the device frame with these specs:

- **Scrim**: `black/50` overlay behind the sheet, with `backdrop-blur-sm` to blur the content underneath
- **Max height**: `85%` of the device frame height — the sheet should never cover the full screen
- **Content hugging**: If the sheet content is shorter than 85%, the sheet should only be as tall as its content (plus padding). Don't force it to 85% when it doesn't need to be
- **Border radius**: `24px` on the top-left and top-right corners (`rounded-t-[24px]`), square on the bottom
- **Drag indicator**: A small `40px × 4px` rounded pill centered at the top of the sheet (`neutral-300`) so users know they can swipe to dismiss
- **Animation**: Slides up from below with a `200–300ms` ease-out transition
- **Dismissal**: Tap the scrim or swipe down to close

### Mobile Anti-Patterns

- **No persistent sidebar navigation** — use bottom tabs as primary nav; a slide-out panel overlay is fine for overflow destinations
- **No horizontal scroll tables** — transform into card/list views
- **Prefer generous tap targets** — aim for `44px × 44px` or larger on interactive elements. Smaller targets are acceptable in dense UI (e.g., inline icons, compact lists) but should be the exception, not the default
- **No multi-column grids** — single column only

---

## Table of Contents — Code Examples

1. [Device Frame Shell](#device-frame-shell)
2. [Mobile Top Bar](#mobile-top-bar)
3. [Bottom Tab Navigation](#bottom-tab-navigation)
4. [Mobile Form Layout](#mobile-form-layout)
5. [Pinned Bottom Button](#pinned-bottom-button)
6. [Mobile List View](#mobile-list-view)
7. [Mobile Card Stack](#mobile-card-stack)
8. [Full Screen Composition](#full-screen-composition)
9. [Contextual Actions](#contextual-actions)

---

## Device Frame Shell

The outermost wrapper that makes the output look like an actual phone. This is the first thing you render — everything else goes inside it.

```jsx
{/* Page background — the "desk" the phone sits on */}
<div className="min-h-screen bg-neutral-100 flex items-center justify-center p-8">

  {/* Phone bezel */}
  <div className="relative w-[393px] h-[852px] rounded-[40px] border-[8px] border-[#1a1a1a] overflow-hidden shadow-xl">

    {/* Status bar notch area — visual only */}
    <div className="h-[54px] bg-white flex items-end justify-center pb-1">
      <div className="w-[126px] h-[34px] bg-[#1a1a1a] rounded-full" />
    </div>

    {/* Scrollable content area */}
    <div className="h-[calc(100%-54px)] overflow-y-auto overflow-x-hidden bg-neutral-50 flex flex-col">
      {/* App content goes here */}
    </div>

  </div>
</div>
```

### Key Details

- The `w-[393px] h-[852px]` is the iPhone 16 viewport — do not change these values
- The `rounded-[40px]` on the outer frame mimics the phone's physical corner radius
- The inner content gets `rounded-[20px]` where it meets the bezel at the top/bottom edges
- The Dynamic Island / notch is a decorative element — a `126×34px` black pill centered at the top
- The scrollable area is everything below the notch, using `flex flex-col` so sticky elements work correctly

---

## Mobile Top Bar

The navigation bar at the top of each screen. Sits just below the status bar / notch area.

### Standard Top Bar (Screen Title)

```jsx
<header className="h-11 px-4 flex items-center justify-between bg-white border-b border-neutral-200 shrink-0">
  <h1 className="text-lg font-medium text-neutral-950">Screen Title</h1>
  <button className="w-10 h-10 flex items-center justify-center">
    <Bell className="w-5 h-5 text-neutral-600" />
  </button>
</header>
```

### Top Bar with Back Navigation

```jsx
<header className="h-11 px-4 flex items-center gap-3 bg-white border-b border-neutral-200 shrink-0">
  <button className="w-10 h-10 flex items-center justify-center -ml-2">
    <ChevronLeft className="w-5 h-5 text-neutral-900" />
  </button>
  <h1 className="text-lg font-medium text-neutral-950 flex-1">Detail View</h1>
</header>
```

### Rules

- Height: `44px` (h-11)
- Always `shrink-0` so it doesn't collapse in flex layouts
- Background: white with bottom border
- Back button: `ChevronLeft` icon, not an arrow — follows iOS convention
- Title: `18px` font-medium (this is the mobile H2 scale)

---

## Bottom Tab Navigation

The primary navigation pattern for mobile apps. Pinned to the bottom of the device frame.

```jsx
<nav className="shrink-0 bg-white border-t border-neutral-200 px-2 pb-6 pt-2">
  <div className="flex items-center justify-around">
    {tabs.map(tab => (
      <button
        key={tab.id}
        className="flex flex-col items-center gap-1 py-1 px-3 min-w-[56px]"
      >
        <tab.icon className={cn(
          "w-5 h-5",
          tab.active ? "text-brand-500" : "text-neutral-400"
        )} />
        <span className={cn(
          "text-[10px]",
          tab.active ? "text-brand-500 font-medium" : "text-neutral-400"
        )}>
          {tab.label}
        </span>
      </button>
    ))}
  </div>
</nav>
```

### Rules

- Maximum 5 tabs
- `pb-6` on the nav provides the home indicator safe area (24px)
- Active state: `brand-500` icon + label, `font-medium` on label
- Inactive state: `neutral-400` icon + label
- Icon size: `20px`
- Label size: `10px` — smaller than the standard caption to avoid crowding
- Each tab target area should aim for at least `44×44px` for comfortable tapping
- Always use `shrink-0` so the tab bar doesn't get pushed out of view

### When More Than 5 Destinations Are Needed

If the app has more than 5 top-level sections, use a slide-out navigation panel alongside the bottom tabs. The bottom tabs hold the 4–5 most important destinations, and a hamburger icon in the top bar (or a "More" tab) opens a `Sheet` from the left that overlays the content:

```jsx
<Sheet>
  <SheetTrigger asChild>
    <button className="w-10 h-10 flex items-center justify-center">
      <Menu className="w-5 h-5 text-neutral-900" />
    </button>
  </SheetTrigger>
  <SheetContent side="left" className="w-72 p-0">
    <div className="pt-14 px-4 space-y-1">
      {allNavItems.map(item => (
        <button
          key={item.id}
          className={cn(
            "flex items-center gap-3 w-full px-3 h-11 rounded-sm text-sm",
            item.active
              ? "bg-brand-50 text-brand-500 font-medium"
              : "text-neutral-600 active:bg-neutral-100"
          )}
        >
          <item.icon className="w-5 h-5" />
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  </SheetContent>
</Sheet>
```

This panel is modal-style — it overlays the content with a `black/50` backdrop and closes when the user taps outside or selects a destination. It is not a persistent sidebar visible alongside content.

---

## Mobile Form Layout

Forms on mobile need extra care. Every field must be self-describing without interaction.

### Single Field

```jsx
<div className="space-y-1.5">
  <label className="text-sm font-normal text-neutral-900">
    Email address
  </label>
  <input
    type="email"
    placeholder="e.g. john@email.com"
    className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm text-neutral-900 placeholder:text-neutral-400 placeholder:font-normal focus:outline-none focus:ring-2 focus:ring-brand-500"
  />
</div>
```

### Select Field

```jsx
<div className="space-y-1.5">
  <label className="text-sm font-normal text-neutral-900">
    Country
  </label>
  <select className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm text-neutral-900 appearance-none focus:outline-none focus:ring-2 focus:ring-brand-500">
    <option value="" disabled selected className="text-neutral-400">Select a country</option>
    <option value="us">United States</option>
    <option value="co">Colombia</option>
  </select>
</div>
```

### Full Form Example

```jsx
<div className="flex-1 overflow-y-auto px-4 py-3">
  <div className="space-y-4">
    {/* Field 1 */}
    <div className="space-y-1.5">
      <label className="text-sm text-neutral-900">Full name</label>
      <input
        type="text"
        placeholder="e.g. Oscar Gonzalez"
        className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm placeholder:text-neutral-400 focus:ring-2 focus:ring-brand-500 focus:outline-none"
      />
    </div>

    {/* Field 2 */}
    <div className="space-y-1.5">
      <label className="text-sm text-neutral-900">Email</label>
      <input
        type="email"
        placeholder="e.g. oscar@casper.studio"
        className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm placeholder:text-neutral-400 focus:ring-2 focus:ring-brand-500 focus:outline-none"
      />
    </div>

    {/* Field 3 - Select */}
    <div className="space-y-1.5">
      <label className="text-sm text-neutral-900">Role</label>
      <select className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none">
        <option value="" disabled selected>Select role</option>
        <option>Designer</option>
        <option>Developer</option>
        <option>Product Manager</option>
      </select>
    </div>
  </div>
</div>
```

### Rules

- Label is always a separate element above the input — `space-y-1.5` (6px) gap between label and input
- Labels: `14px`, `font-normal` (400), `neutral-900`
- Placeholders: `neutral-400`, `font-normal` — must feel like a faint hint, not a label
- Input height: `48px` (h-12) minimum for comfortable touch targets
- Between fields: `16px` gap (`space-y-4`)
- Inputs use `rounded-sm` (6px / `radius-sm`)

---

## Pinned Bottom Button

The primary CTA that sticks to the bottom of the screen so the user's thumb can always reach it.

### Basic Pinned Button

```jsx
{/* This goes at the bottom of the flex column, after the scrollable content */}
<div className="shrink-0 px-4 pt-3 pb-6 bg-white border-t border-neutral-200">
  <button className="w-full h-12 bg-brand-500 text-white text-sm font-medium rounded-sm hover:bg-brand-600 active:bg-brand-700 transition-colors">
    Continue
  </button>
</div>
```

### With Secondary Action

```jsx
<div className="shrink-0 px-4 pt-3 pb-6 bg-white border-t border-neutral-200 space-y-2">
  <button className="w-full h-12 bg-brand-500 text-white text-sm font-medium rounded-sm hover:bg-brand-600 active:bg-brand-700 transition-colors">
    Submit
  </button>
  <button className="w-full h-12 bg-white border border-neutral-200 text-neutral-900 text-sm font-medium rounded-sm active:bg-neutral-50 transition-colors">
    Save as Draft
  </button>
</div>
```

### Rules

- Container: `shrink-0` so it never collapses, white background, top border for visual separation
- `pb-6` (24px) accounts for the home indicator safe area
- `pt-3` (12px) breathing room above the button
- Button: `h-12` (48px), full width, `brand-500` background, `rounded-sm`
- Use `active:` states for press feedback — darken the background slightly on press. `hover:` states also work (mice and styluses exist on mobile)
- If there's a secondary button, stack vertically with `space-y-2`

---

## Mobile List View

Tables don't work on mobile — transform them into tappable list rows.

### List Row

```jsx
<button className="w-full flex items-center gap-3 px-4 py-3 active:bg-neutral-50 transition-colors">
  {/* Leading element — icon or avatar */}
  <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
    <FileText className="w-5 h-5 text-brand-500" />
  </div>

  {/* Content */}
  <div className="flex-1 min-w-0 text-left">
    <p className="text-sm font-medium text-neutral-900 truncate">Document Title</p>
    <p className="text-xs text-neutral-500 truncate">Updated 2 hours ago</p>
  </div>

  {/* Trailing element — chevron or badge */}
  <ChevronRight className="w-4 h-4 text-neutral-400 shrink-0" />
</button>
```

### List Container

```jsx
<div className="bg-white rounded-lg border border-neutral-200 divide-y divide-neutral-200 overflow-hidden">
  <ListRow />
  <ListRow />
  <ListRow />
</div>
```

### Rules

- Rows are full-width `button` elements for tap handling
- Minimum row height: `56px` (from `py-3` + content)
- Use `active:bg-neutral-50` for press feedback
- Trailing chevron (`ChevronRight`) signals the row is tappable
- Wrap list in a Card-like container with `rounded-lg` and `divide-y`

---

## Mobile Card Stack

The default layout for dashboards and content pages on mobile — vertically stacked cards.

```jsx
<div className="px-4 py-3 space-y-3">
  {/* Stat row — horizontal scroll */}
  <div className="flex gap-3 overflow-x-auto -mx-4 px-4 pb-1">
    <div className="shrink-0 w-[140px] bg-white rounded-lg border border-neutral-200 p-3">
      <p className="text-xs text-neutral-500">Active Users</p>
      <p className="text-xl font-medium text-neutral-950 mt-1">2,847</p>
    </div>
    <div className="shrink-0 w-[140px] bg-white rounded-lg border border-neutral-200 p-3">
      <p className="text-xs text-neutral-500">Revenue</p>
      <p className="text-xl font-medium text-neutral-950 mt-1">$12.4k</p>
    </div>
    <div className="shrink-0 w-[140px] bg-white rounded-lg border border-neutral-200 p-3">
      <p className="text-xs text-neutral-500">Conversion</p>
      <p className="text-xl font-medium text-neutral-950 mt-1">3.2%</p>
    </div>
  </div>

  {/* Full-width content card */}
  <div className="bg-white rounded-lg border border-neutral-200 p-4">
    <h3 className="text-base font-medium text-neutral-950 mb-3">Recent Activity</h3>
    {/* Card content */}
  </div>
</div>
```

### Rules

- Cards stack vertically with `space-y-3` (12px gaps)
- Stat cards in a horizontal scroll row: fixed width, `overflow-x-auto`, negative margin trick for edge-to-edge scroll
- Full-width cards: `rounded-lg` (10px / `radius-lg`)
- No multi-column layouts — everything is single column

---

## Full Screen Composition

How all the pieces come together in a complete mobile app screen.

### Example: Form Screen

```jsx
<div className="min-h-screen bg-neutral-100 flex items-center justify-center p-8">
  <div className="relative w-[393px] h-[852px] rounded-[40px] border-[8px] border-[#1a1a1a] overflow-hidden shadow-xl">

    {/* Dynamic Island */}
    <div className="h-[54px] bg-white flex items-end justify-center pb-1">
      <div className="w-[126px] h-[34px] bg-[#1a1a1a] rounded-full" />
    </div>

    {/* App content */}
    <div className="h-[calc(100%-54px)] flex flex-col bg-neutral-50">

      {/* Top bar */}
      <header className="h-11 px-4 flex items-center gap-3 bg-white border-b border-neutral-200 shrink-0">
        <button className="w-10 h-10 flex items-center justify-center -ml-2">
          <ChevronLeft className="w-5 h-5 text-neutral-900" />
        </button>
        <h1 className="text-lg font-medium text-neutral-950">Create Account</h1>
      </header>

      {/* Scrollable form area */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm text-neutral-900">Full name</label>
            <input type="text" placeholder="e.g. Oscar Gonzalez" className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm placeholder:text-neutral-400 focus:ring-2 focus:ring-brand-500 focus:outline-none" />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-neutral-900">Email</label>
            <input type="email" placeholder="e.g. oscar@casper.studio" className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm placeholder:text-neutral-400 focus:ring-2 focus:ring-brand-500 focus:outline-none" />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-neutral-900">Password</label>
            <input type="password" placeholder="At least 8 characters" className="w-full h-12 px-3 rounded-sm border border-neutral-200 bg-white text-sm placeholder:text-neutral-400 focus:ring-2 focus:ring-brand-500 focus:outline-none" />
          </div>
        </div>
      </div>

      {/* Pinned bottom button */}
      <div className="shrink-0 px-4 pt-3 pb-6 bg-white border-t border-neutral-200">
        <button className="w-full h-12 bg-brand-500 text-white text-sm font-medium rounded-sm hover:bg-brand-600 active:bg-brand-700 transition-colors">
          Create Account
        </button>
      </div>

    </div>
  </div>
</div>
```

### Example: List Screen with Bottom Tabs

```jsx
<div className="min-h-screen bg-neutral-100 flex items-center justify-center p-8">
  <div className="relative w-[393px] h-[852px] rounded-[40px] border-[8px] border-[#1a1a1a] overflow-hidden shadow-xl">

    {/* Dynamic Island */}
    <div className="h-[54px] bg-white flex items-end justify-center pb-1">
      <div className="w-[126px] h-[34px] bg-[#1a1a1a] rounded-full" />
    </div>

    {/* App content */}
    <div className="h-[calc(100%-54px)] flex flex-col bg-neutral-50">

      {/* Top bar */}
      <header className="h-11 px-4 flex items-center justify-between bg-white border-b border-neutral-200 shrink-0">
        <h1 className="text-[24px] font-medium text-neutral-950">Projects</h1>
        <button className="w-10 h-10 flex items-center justify-center">
          <Plus className="w-5 h-5 text-brand-500" />
        </button>
      </header>

      {/* Scrollable list */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        <div className="bg-white rounded-lg border border-neutral-200 divide-y divide-neutral-200 overflow-hidden">
          {/* List rows */}
          <button className="w-full flex items-center gap-3 px-4 py-3 active:bg-neutral-50">
            <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
              <Folder className="w-5 h-5 text-brand-500" />
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-sm font-medium text-neutral-900 truncate">Client Portal Redesign</p>
              <p className="text-xs text-neutral-500">Updated 2h ago</p>
            </div>
            <ChevronRight className="w-4 h-4 text-neutral-400 shrink-0" />
          </button>
          {/* More rows... */}
        </div>
      </div>

      {/* Bottom tab bar */}
      <nav className="shrink-0 bg-white border-t border-neutral-200 px-2 pb-6 pt-2">
        <div className="flex items-center justify-around">
          <button className="flex flex-col items-center gap-1 py-1 px-3">
            <Home className="w-5 h-5 text-brand-500" />
            <span className="text-[10px] text-brand-500 font-medium">Home</span>
          </button>
          <button className="flex flex-col items-center gap-1 py-1 px-3">
            <Search className="w-5 h-5 text-neutral-400" />
            <span className="text-[10px] text-neutral-400">Search</span>
          </button>
          <button className="flex flex-col items-center gap-1 py-1 px-3">
            <Bell className="w-5 h-5 text-neutral-400" />
            <span className="text-[10px] text-neutral-400">Alerts</span>
          </button>
          <button className="flex flex-col items-center gap-1 py-1 px-3">
            <User className="w-5 h-5 text-neutral-400" />
            <span className="text-[10px] text-neutral-400">Profile</span>
          </button>
        </div>
      </nav>

    </div>
  </div>
</div>
```

### Composition Rules

The flex column layout (`flex flex-col`) is what makes everything work:
1. **Top bar** — `shrink-0`, stays at top
2. **Content area** — `flex-1 overflow-y-auto`, takes remaining space and scrolls
3. **Bottom element** (pinned button OR tab bar) — `shrink-0`, stays at bottom

This structure ensures the top and bottom elements are always visible while the middle content scrolls. When both a pinned button and tab bar are needed (rare), the button sits above the tab bar, both with `shrink-0`.

---

## Contextual Actions

When a trigger presents multiple options, choose between a contextual menu or a bottom sheet.

### Contextual Menu

For short option lists (3–6 simple actions). Uses shadcn's `DropdownMenu`:

```jsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <button className="w-10 h-10 flex items-center justify-center rounded-sm active:bg-neutral-100">
      <MoreVertical className="w-5 h-5 text-neutral-600" />
    </button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end" className="w-48 rounded-xl shadow-md border border-neutral-200">
    <DropdownMenuItem className="flex items-center gap-2 px-3 py-2.5 text-sm">
      <Edit className="w-4 h-4 text-neutral-500" />
      <span>Edit</span>
    </DropdownMenuItem>
    <DropdownMenuItem className="flex items-center gap-2 px-3 py-2.5 text-sm">
      <Share className="w-4 h-4 text-neutral-500" />
      <span>Share</span>
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="flex items-center gap-2 px-3 py-2.5 text-sm text-error-500">
      <Trash className="w-4 h-4" />
      <span>Delete</span>
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### Bottom Sheet

For richer content, longer option lists, or anything needing more space. Slides up from the bottom with a scrim + blur.

```jsx
{/* Scrim overlay — blurs and darkens the background */}
{isOpen && (
  <div
    className="absolute inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300"
    onClick={onClose}
  />
)}

{/* Bottom sheet */}
<div className={cn(
  "absolute bottom-0 left-0 right-0 z-50 bg-white rounded-t-[24px] transition-transform duration-300 ease-out",
  isOpen ? "translate-y-0" : "translate-y-full"
)}
  style={{ maxHeight: '85%' }}
>
  {/* Drag indicator */}
  <div className="flex justify-center pt-3 pb-2">
    <div className="w-10 h-1 rounded-full bg-neutral-300" />
  </div>

  {/* Sheet content — scrollable if needed */}
  <div className="overflow-y-auto px-4 pb-8" style={{ maxHeight: 'calc(85vh - 40px)' }}>
    <h3 className="text-lg font-medium text-neutral-950 mb-4">Select an option</h3>

    <div className="space-y-1">
      <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-neutral-900 active:bg-neutral-50">
        <Star className="w-5 h-5 text-neutral-500" />
        <span>Add to favorites</span>
      </button>
      <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-neutral-900 active:bg-neutral-50">
        <Copy className="w-5 h-5 text-neutral-500" />
        <span>Duplicate</span>
      </button>
      <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-neutral-900 active:bg-neutral-50">
        <Archive className="w-5 h-5 text-neutral-500" />
        <span>Archive</span>
      </button>
    </div>
  </div>
</div>
```

### Rules

- **Contextual menu**: Use for 3–6 simple, label-only actions. Appears next to the trigger.
- **Bottom sheet**: Use when options need icons + descriptions, when there are more than 6 options, or when the content is richer (forms, confirmations, previews).
- **Scrim**: `bg-black/50` with `backdrop-blur-sm` — both darkens and blurs the background.
- **Max height**: `85%` of the device frame. The sheet hugs its content if shorter — never force it taller than it needs to be.
- **Drag indicator**: `40px × 4px` pill in `neutral-300`, centered at the top.
- **Corner radius**: `rounded-t-[24px]` (24px) on top corners only.
- **Animation**: `translate-y` transition, `200–300ms`, `ease-out`.
- **Dismissal**: Tap scrim or swipe down.
