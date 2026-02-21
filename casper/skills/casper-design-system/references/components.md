# Component Patterns

Reusable composite components built from shadcn/ui primitives. These are the building blocks that live inside layout structures.

---

## Table of Contents

1. [Stat Card](#stat-card)
2. [List Item Row](#list-item-row)
3. [Filter Bar](#filter-bar)
4. [Kanban Board](#kanban-board)
5. [Profile / Discovery Card](#profile--discovery-card)
6. [Product Card](#product-card)
7. [Activity Feed Item](#activity-feed-item)
8. [Toast Notification](#toast-notification)
9. [Form Validation States](#form-validation-states)

---

## Stat Card

A card showing a key metric with an optional semantic accent.

### Variants

**Pastel accent background:**
```jsx
<Card className="bg-success-50 border-success-200">
  <CardContent className="p-4 flex items-center gap-3">
    <div className="w-10 h-10 rounded-full bg-success-100 flex items-center justify-center">
      <Users className="w-5 h-5 text-success-600" />
    </div>
    <div>
      <p className="text-sm font-medium text-neutral-900">5 new members</p>
      <p className="text-xs text-neutral-500">1 onboarding now</p>
    </div>
  </CardContent>
</Card>
```

**Neutral with colored number:**
```jsx
<Card>
  <CardContent className="p-4 flex items-center gap-3">
    <span className="text-2xl font-medium text-brand-500">3</span>
    <div className="flex items-center gap-2">
      <CheckCircle className="w-4 h-4 text-success-500" />
      <span className="text-sm text-neutral-700">Verified</span>
    </div>
  </CardContent>
</Card>
```

Stat cards commonly appear in a horizontal row (scrollable on mobile):
```jsx
<div className="flex gap-4 overflow-x-auto pb-2">
  <StatCard />
  <StatCard />
  <StatCard />
</div>
```

---

## List Item Row

A horizontal row used in to-do lists, event lists, activity feeds, and file lists.

### Anatomy

```
┌─────────────────────────────────────────────────────┐
│ [Icon Circle]  Title                        Today   │
│                Description / subtitle               │
└─────────────────────────────────────────────────────┘
```

### Code

```jsx
<div className="flex items-center gap-3 py-3 px-4 hover:bg-neutral-50 transition-colors">
  {/* Icon in circle */}
  <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
    <ClipboardCheck className="w-5 h-5 text-brand-500" />
  </div>

  {/* Content */}
  <div className="flex-1 min-w-0">
    <p className="text-sm font-medium text-neutral-900 truncate">{title}</p>
    <p className="text-xs text-neutral-500 truncate">{subtitle}</p>
  </div>

  {/* Metadata */}
  <span className="text-xs text-neutral-400 shrink-0">{timestamp}</span>
</div>
```

Separate rows with `divide-y divide-neutral-200` on the parent container.

---

## Filter Bar

A horizontal bar of pill-shaped filter chips, commonly used above tables and list views.

### Chip Variants

**With count badge:**
```jsx
<button className={cn(
  "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm border transition-colors",
  isActive
    ? "bg-brand-50 border-brand-200 text-brand-700"
    : "bg-white border-neutral-200 text-neutral-700 hover:bg-neutral-50"
)}>
  <span>{label}</span>
  <span className={cn(
    "text-xs font-medium rounded-full px-1.5 py-0.5",
    isActive ? "bg-brand-100 text-brand-600" : "bg-neutral-100 text-neutral-500"
  )}>
    {count}
  </span>
</button>
```

### Layout

```jsx
<div className="flex gap-2 overflow-x-auto pb-2">
  {filters.map(f => <FilterChip key={f.id} {...f} />)}
</div>
```

On mobile, this scrolls horizontally with `-mx-4 px-4` to extend past container padding.

---

## Kanban Board

A column-based layout for pipelines, lead tracking, project stages.

### Structure

```
┌─────────────┬─────────────┬─────────────┐
│ New      [+]│ Qualified[+]│ Meeting  [+]│
├─────────────┼─────────────┼─────────────┤
│ ┌─────────┐ │ ┌─────────┐ │ ┌─────────┐ │
│ │ Card 1  │ │ │ Card 4  │ │ │ Card 7  │ │
│ └─────────┘ │ └─────────┘ │ └─────────┘ │
│ ┌─────────┐ │ ┌─────────┐ │             │
│ │ Card 2  │ │ │ Card 5  │ │             │
│ └─────────┘ │ └─────────┘ │             │
└─────────────┴─────────────┴─────────────┘
```

### Column

```jsx
<div className="flex-1 min-w-[280px]">
  {/* Column header */}
  <div className="flex items-center justify-between mb-3">
    <h3 className="text-sm font-medium text-neutral-900">{title}</h3>
    <button className="text-neutral-400 hover:text-neutral-600">
      <Plus className="w-4 h-4" />
    </button>
  </div>

  {/* Cards */}
  <div className="flex flex-col gap-3">
    {items.map(item => <KanbanCard key={item.id} {...item} />)}
  </div>
</div>
```

### Kanban Card

```jsx
<Card className="p-4">
  <div className="flex items-center gap-3 mb-3">
    <Avatar className="w-8 h-8"><AvatarImage src={item.avatar} /></Avatar>
    <div>
      <p className="text-sm font-medium text-neutral-900">{item.name}</p>
      <p className="text-xs text-neutral-500">{item.company}</p>
    </div>
  </div>
  <div className="flex items-center gap-2">
    <Badge variant="outline" className="text-xs bg-success-50 text-success-700 border-success-200">
      {item.date}
    </Badge>
    <span className="text-xs text-neutral-500">{item.value}</span>
  </div>
</Card>
```

### Container

```jsx
<div className="flex gap-6 overflow-x-auto">
  {columns.map(col => <KanbanColumn key={col.id} {...col} />)}
</div>
```

---

## Profile / Discovery Card

Used for freelancer profiles, team members, or user listings.

### Anatomy

```
┌───────────────────────────────────┐
│ [Gradient image placeholder]      │
│                    ┌──────┐       │
│                    │Avatar│       │
│                    └──────┘       │
│ [star] 4.8 (20)  New York, NY    │
│ Laura Adams                       │
│ [Available] [bolt]                │
│ UI/UX Design Expert               │
│                                   │
│ [$80-$120/hr]                     │
│ [UI/UX Designer] [Graphic Design] │
│ [+5 Specializations]             │
└───────────────────────────────────┘
```

### Key Details

- Top section: Gradient placeholder image (see Image Placeholders in SKILL.md)
- Avatar overlaps the image bottom edge by ~50%
- Name in Body Bold, role in Body/neutral-500
- Availability badge: success-50 bg, success-700 text
- Price range in a standalone pill: brand-50 bg, brand-700 text
- Skill tags: neutral-100 bg, neutral-700 text, rounded-full
- Overflow tag: "+N Specializations" in same pill style

---

## Product Card

For e-commerce or marketplace item displays.

### Anatomy

```
┌───────────────────────┬──────────────────────┐
│                       │ Brand Name           │
│ [Product image /      │ Product Title        │
│  gradient placeholder]│ [stars] (146)        │
│                       │ $18.00               │
│                       │                      │
│                       │ [Type: Whole ▾]      │
│                       │ [Size: 12oz  ▾]      │
│                       │ Qty: [- 1 +]         │
│                       │                      │
│                       │ [Add to cart] ← primary │
│                       │ [Buy now]     ← secondary │
└───────────────────────┴──────────────────────┘
```

### Key Details

- Image takes up ~50% width on desktop, full width on mobile (stacked)
- Price in Heading 2 weight
- Selectors use shadcn `Select` component
- Quantity uses a custom stepper (secondary button styles)
- Primary CTA: brand-500 button, full width
- Secondary CTA: brand-50 bg, brand-700 text, full width

---

## Activity Feed Item

A compact row for event feeds, notification lists, or changelog entries.

```jsx
<div className="flex items-start gap-3 py-3">
  <div className="w-8 h-8 rounded-full bg-error-50 flex items-center justify-center shrink-0">
    <Calendar className="w-4 h-4 text-error-500" />
  </div>
  <div className="flex-1">
    <p className="text-sm text-neutral-900">
      <span className="font-medium">Department Offsite</span>
    </p>
    <p className="text-xs text-neutral-500">Monday, Nov 13, 2023</p>
  </div>
  <span className="text-xs text-neutral-400 shrink-0">All-day</span>
</div>
```

---

## Toast Notification

Transient feedback using shadcn's `Sonner` toast. Confirms actions, surfaces errors, or provides info.

### Success Toast

```jsx
<div className="flex items-center gap-3 p-4 bg-white border border-neutral-200 border-l-4 border-l-success-200 rounded-sm shadow-md">
  <CheckCircle className="w-5 h-5 text-success-500 shrink-0" />
  <div className="flex-1 min-w-0">
    <p className="text-sm text-neutral-900">Project created successfully</p>
  </div>
  <a href="#" className="text-sm text-brand-500 shrink-0">View</a>
  <button className="text-neutral-400 hover:text-neutral-600 shrink-0">
    <X className="w-4 h-4" />
  </button>
</div>
```

### Error Toast

```jsx
<div className="flex items-center gap-3 p-4 bg-white border border-neutral-200 border-l-4 border-l-error-200 rounded-sm shadow-md">
  <XCircle className="w-5 h-5 text-error-500 shrink-0" />
  <div className="flex-1 min-w-0">
    <p className="text-sm text-neutral-900">Couldn't save changes — try again</p>
  </div>
  <button className="text-sm text-brand-500 shrink-0">Retry</button>
  <button className="text-neutral-400 hover:text-neutral-600 shrink-0">
    <X className="w-4 h-4" />
  </button>
</div>
```

### Variants

| Variant | Icon | Left Border | Use |
|---|---|---|---|
| **Success** | `CheckCircle` / `success-500` | `success-200` | Action completed |
| **Error** | `XCircle` / `error-500` | `error-200` | Action failed |
| **Info** | `Info` / `brand-500` | `brand-200` | Neutral updates |
| **Warning** | `AlertTriangle` / `warning-500` | `warning-200` | Non-blocking caution |

### Rules

- Body text: `14px`, `neutral-900`. One sentence max
- Optional action link: `brand-500`, inline ("Undo", "View", "Retry")
- Close button: `X` icon, `neutral-400`
- Positioning: bottom-right on web, top-center on mobile
- Duration: `4000ms` default, `6000ms` with action link. Error toasts persist until dismissed

---

## Form Validation States

Inline error and success feedback for form inputs.

### Input with Error

```jsx
<div className="space-y-1.5">
  <label className="text-sm text-neutral-900">Email address</label>
  <input
    type="email"
    value="not-an-email"
    className="w-full h-9 px-3 rounded-sm border border-error-500 bg-white text-sm text-neutral-900 focus:outline-none focus:ring-2 focus:ring-error-500"
  />
  <div className="flex items-center gap-1">
    <AlertCircle className="w-3.5 h-3.5 text-error-500 shrink-0" />
    <p className="text-xs text-error-500">Please enter a valid email address</p>
  </div>
</div>
```

### Rules

- **Error border**: Swap `neutral-200` → `error-500`
- **Error ring**: Swap `brand-500` → `error-500`
- **Error message**: Caption size (12px), `error-500`, below the input with `space-y-1`
- **Label stays neutral**: Don't color the label red — the border and message are enough signal
- **Validate on blur**, not on keystroke. Remove error on change when corrected
- **On submit with errors**: Scroll to and focus the first invalid field
