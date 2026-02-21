# Web Layout Patterns

Structural patterns, responsive rules, and code examples for web application interfaces. This file is self-contained — read it whenever the project is a **web application** (not a mobile app).

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

## Table of Contents — Code Examples

1. [App Shell](#app-shell)
2. [Sidebar Navigation](#sidebar-navigation)
3. [Dashboard Grid](#dashboard-grid)
4. [Data Table Page](#data-table-page)
5. [Page Header](#page-header)

---

## App Shell

The foundational layout for all app-style interfaces. Sidebar on the left, content area filling the rest.

```
┌──────────┬─────────────────────────────────────────┐
│          │  Page Header (title + actions)           │
│ Sidebar  ├─────────────────────────────────────────┤
│ (240px)  │                                         │
│          │  Content Area                            │
│          │  (cards, tables, etc.)                   │
│          │                                         │
│          │                                         │
└──────────┴─────────────────────────────────────────┘
```

### Structure

```jsx
<div className="flex h-screen bg-neutral-50">
  {/* Sidebar */}
  <aside className="w-60 border-r border-neutral-200 bg-white flex flex-col">
    <SidebarContent />
  </aside>

  {/* Main */}
  <main className="flex-1 overflow-auto">
    <div className="p-6 max-w-screen-xl mx-auto">
      <PageHeader />
      <ContentArea />
    </div>
  </main>
</div>
```

### Mobile Variant

On screens below 768px, the sidebar becomes a `Sheet` triggered by a hamburger icon in a sticky top bar.

```jsx
{/* Mobile top bar */}
<header className="md:hidden flex items-center h-12 px-4 border-b border-neutral-200 bg-white sticky top-0 z-40">
  <Sheet>
    <SheetTrigger><Menu className="w-5 h-5" /></SheetTrigger>
    <SheetContent side="left" className="w-60 p-0">
      <SidebarContent />
    </SheetContent>
  </Sheet>
  <span className="ml-3 text-sm font-medium">Page Title</span>
</header>
```

---

## Sidebar Navigation

The vertical nav bar lives inside the App Shell sidebar.

### Anatomy

```
┌────────────────────┐
│ [icon] Logo          │  ← 48px height, 16px horizontal padding
├────────────────────┤
│ [icon] Home    ◀──── │  Active (brand-50 bg, brand-500 text)
│ [icon] Inbox         │  Default (neutral-600 text)
│ [icon] Reports       │
│                      │
│ Analytics            │  ← Group label (caption, neutral-400)
│ [icon] Dashboard     │
│ [icon] Trends        │
│ [icon] Campaigns     │
│                      │
│ Settings             │  ← Group label
│ [icon] Company       │
│ [icon] Payments      │
│ [icon] Integrations  │
├────────────────────┤
│ [avatar] User Name   │  ← Bottom-pinned user section
│          Role        │
└────────────────────┘
```

### Nav Item Spec

```jsx
<button className={cn(
  "flex items-center gap-3 w-full px-3 h-9 rounded-lg text-sm transition-colors",
  isActive
    ? "bg-brand-50 text-brand-500 font-medium"
    : "text-neutral-600 hover:bg-neutral-100"
)}>
  <Icon className="w-4 h-4" />
  <span>{label}</span>
</button>
```

### Group Label

```jsx
<span className="px-3 pt-6 pb-2 block text-xs text-neutral-400">
  {groupName}
</span>
```

### User Section (bottom-pinned)

```jsx
<div className="mt-auto border-t border-neutral-200 p-4 flex items-center gap-3">
  <Avatar className="w-8 h-8">
    <AvatarImage src={user.avatar} />
    <AvatarFallback>{user.initials}</AvatarFallback>
  </Avatar>
  <div>
    <p className="text-sm font-medium text-neutral-900">{user.name}</p>
    <p className="text-xs text-neutral-500">{user.role}</p>
  </div>
</div>
```

---

## Dashboard Grid

A responsive grid of cards. Typically used as the main content area of a dashboard page.

### Layout

- Desktop: 2-column or 3-column grid depending on content
- Tablet: 2-column
- Mobile: Single column stack

```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card className="col-span-1 md:col-span-2"> {/* Wide card spans 2 cols */}
    <CardContent>...</CardContent>
  </Card>
  <Card>
    <CardContent>...</CardContent>
  </Card>
</div>
```

### Common Dashboard Layouts

**Two-column with sidebar panel:**
```
┌───────────────────────┬──────────────┐
│ Primary content       │ Side panel   │
│ (to-do, feed, table)  │ (updates,    │
│                       │  stats)      │
└───────────────────────┴──────────────┘
```
Use `grid-cols-1 lg:grid-cols-[1fr_380px]` for this pattern.

---

## Data Table Page

A page pattern for displaying tabular data with filters.

### Structure

```
┌──────────────────────────────────────────────┐
│ Page Title                                    │
├──────────────────────────────────────────────┤
│ [Search input]         [Filter] [Sort] [+]   │
├──────────────────────────────────────────────┤
│ Card                                          │
│ ┌──────────────────────────────────────────┐ │
│ │ DOC    STATUS    OWNER    VIEWS   DATE   │ │
│ ├──────────────────────────────────────────┤ │
│ │ Row 1                                    │ │
│ │ Row 2                                    │ │
│ │ Row 3                                    │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### Key Details

- The table lives inside a Card (white bg, border, radius)
- Search bar: `Input` component with search icon, full-width or sized
- Action buttons: Secondary variant, right-aligned
- Table column headers: uppercase, caption-bold, neutral-500
- Status columns use Badge component with semantic colors
- Owner columns use Avatar + name
- Pagination below the card, not inside it

---

## Page Header

The top section of every page, below the app shell top edge.

### Standard Header

```jsx
<div className="mb-6">
  <h1 className="text-[30px] font-medium leading-9 text-neutral-950">{title}</h1>
  <p className="text-sm text-neutral-500 mt-1">{subtitle}</p>
</div>
```

### Header with Breadcrumb

```jsx
<div className="mb-6">
  <Breadcrumb className="mb-2">
    <BreadcrumbList>
      <BreadcrumbItem><BreadcrumbLink href="/">Home</BreadcrumbLink></BreadcrumbItem>
      <BreadcrumbSeparator />
      <BreadcrumbItem><BreadcrumbPage>{currentPage}</BreadcrumbPage></BreadcrumbItem>
    </BreadcrumbList>
  </Breadcrumb>
  <h1 className="text-[30px] font-medium leading-9 text-neutral-950">{title}</h1>
</div>
```

### Header with Actions

```jsx
<div className="flex items-center justify-between mb-6">
  <div>
    <h1 className="text-[30px] font-medium leading-9 text-neutral-950">{title}</h1>
    <p className="text-sm text-neutral-500 mt-1">{subtitle}</p>
  </div>
  <div className="flex items-center gap-3">
    <Button variant="secondary">Import</Button>
    <Button>Share</Button>
  </div>
</div>
```
