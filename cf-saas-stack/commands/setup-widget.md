---
description: Sets up an embeddable widget system (like Intercom) that can be added to any website via a script tag
argument-hint: <widget purpose, e.g. "bug tracker" or "feedback widget" or "feature request collector">
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, WebSearch
---

# Setup Embeddable Widget

Set up an embeddable JavaScript widget that can be installed on any website via a `<script>` tag — similar to Intercom, Crisp, or Canny.

Widget purpose: $ARGUMENTS

## Architecture Overview

The widget system has 4 layers:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Embed Script (public/widget.js)                         │
│     Lightweight JS snippet that site owners paste into HTML │
│     Creates an iframe pointed at your app's /widget route   │
│     Handles postMessage communication with the iframe       │
├─────────────────────────────────────────────────────────────┤
│  2. Widget Routes (app/routes/widget/)                      │
│     Minimal-chrome pages rendered inside the iframe         │
│     No nav/sidebar — just the widget UI                     │
│     Uses a dedicated layout with postMessage bridge         │
├─────────────────────────────────────────────────────────────┤
│  3. Widget API (app/trpc/routes/widget.ts)                  │
│     Public procedures authenticated via project API key     │
│     CORS-enabled for cross-origin requests                  │
│     Rate-limited per project                                │
├─────────────────────────────────────────────────────────────┤
│  4. Data Layer (schema + repositories)                      │
│     Projects table (API keys, settings, allowed origins)    │
│     Submissions table (bugs, features, feedback, etc.)      │
│     Project-scoped queries                                  │
└─────────────────────────────────────────────────────────────┘
```

## Before You Start

**IMPORTANT: Read these files first to understand project conventions:**

| Area | File |
|------|------|
| Routes | `app/routes.ts` |
| Schema conventions | `app/db/schema.ts` |
| tRPC patterns | `app/trpc/index.ts` |
| Worker entry | `workers/app.ts` |
| Repository pattern | See CLAUDE.md |

## Implementation Checklist

```
Phase 1: Data Layer
- [ ] Add `widgetProject` table to `app/db/schema.ts`
- [ ] Add `widgetSubmission` table to `app/db/schema.ts`
- [ ] Generate migration: `bun run db:generate`
- [ ] Apply migration: `bun run db:migrate:local`

Phase 2: Repository
- [ ] Create `app/repositories/widget-project.ts`
- [ ] Create `app/repositories/widget-submission.ts`

Phase 3: API
- [ ] Create `app/trpc/routes/widget.ts` (public procedures with API key auth)
- [ ] Register widget router in `app/trpc/router.ts`
- [ ] Add CORS handling for widget API routes in `workers/app.ts`

Phase 4: Admin Dashboard
- [ ] Create project management page at `app/routes/admin/widget-projects.tsx`
- [ ] Create submissions viewer at `app/routes/admin/widget-submissions.tsx`
- [ ] Add routes to `app/routes.ts`

Phase 5: Widget UI (iframe content)
- [ ] Create `app/routes/widget/_layout.tsx` (minimal layout, postMessage bridge)
- [ ] Create `app/routes/widget/index.tsx` (widget home)
- [ ] Create submission form routes based on widget purpose
- [ ] Add widget routes to `app/routes.ts`

Phase 6: Embed Script
- [ ] Create `public/widget.js` (loader script)
- [ ] Create `public/widget.css` (optional external styles for the trigger button)

Phase 7: Integration
- [ ] Add embed code snippet generator to admin dashboard
- [ ] Test cross-origin embedding
- [ ] Verify postMessage communication
```

## Schema Design

### widgetProject table

```typescript
// app/db/schema.ts
export const widgetProject = sqliteTable("widget_project", {
  id: text("id").primaryKey(), // Use nanoid or cuid
  name: text("name").notNull(),
  // API key for authenticating widget requests
  apiKey: text("api_key").notNull().unique(),
  // Optional: restrict which domains can use this widget
  allowedOrigins: text("allowed_origins"), // JSON array of domains, null = allow all
  // Owner of this project
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  // Widget configuration (colors, position, default form, etc.)
  config: text("config"), // JSON object
  createdAt: integer("created_at", { mode: "timestamp_ms" })
    .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
    .notNull(),
  updatedAt: integer("updated_at", { mode: "timestamp_ms" })
    .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
    .$onUpdate(() => new Date())
    .notNull(),
});
```

### widgetSubmission table

```typescript
export const widgetSubmission = sqliteTable("widget_submission", {
  id: text("id").primaryKey(),
  projectId: text("project_id")
    .notNull()
    .references(() => widgetProject.id, { onDelete: "cascade" }),
  // Submission type — adapt these to the widget purpose
  type: text("type", { enum: ["bug", "feature", "feedback"] }).notNull(),
  title: text("title").notNull(),
  description: text("description"),
  // Metadata from the submitter's browser
  metadata: text("metadata"), // JSON: { url, userAgent, screen, etc. }
  // Optional: identify the submitter
  submitterEmail: text("submitter_email"),
  submitterName: text("submitter_name"),
  // Status tracking
  status: text("status", { enum: ["open", "in_progress", "closed"] })
    .notNull()
    .default("open"),
  createdAt: integer("created_at", { mode: "timestamp_ms" })
    .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
    .notNull(),
  updatedAt: integer("updated_at", { mode: "timestamp_ms" })
    .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
    .$onUpdate(() => new Date())
    .notNull(),
});
```

**Note**: Adapt the `type` enum and fields based on the widget purpose described in $ARGUMENTS.

## Repository Pattern

Follow the project's repository pattern — pure functions, first param is `db: Database`:

```typescript
// app/repositories/widget-project.ts
import type { Context } from "@/trpc";

type Database = Context["db"];

export async function getProjectByApiKey(db: Database, apiKey: string) {
  return db.query.widgetProject.findFirst({
    where: eq(widgetProject.apiKey, apiKey),
  });
}

export async function createProject(db: Database, input: CreateProjectInput) {
  // Generate API key (use crypto.randomUUID or nanoid)
  const apiKey = crypto.randomUUID();
  // ...
}
```

## Widget API (tRPC)

Create a dedicated router with API key authentication middleware:

```typescript
// app/trpc/routes/widget.ts
import { createTRPCRouter, publicProcedure } from "..";
import { z } from "zod/v4";
import { TRPCError } from "@trpc/server";
import * as widgetProjectRepo from "@/repositories/widget-project";
import * as widgetSubmissionRepo from "@/repositories/widget-submission";

// Middleware: validate API key from headers
const widgetAuthMiddleware = t.middleware(async ({ ctx, next }) => {
  const apiKey = ctx.headers.get("x-widget-api-key");
  if (!apiKey) {
    throw new TRPCError({ code: "UNAUTHORIZED", message: "Missing API key" });
  }

  const project = await widgetProjectRepo.getProjectByApiKey(ctx.db, apiKey);
  if (!project) {
    throw new TRPCError({ code: "UNAUTHORIZED", message: "Invalid API key" });
  }

  return next({ ctx: { ...ctx, widgetProject: project } });
});

const widgetProcedure = publicProcedure.use(widgetAuthMiddleware);

export const widgetRouter = createTRPCRouter({
  submit: widgetProcedure
    .input(z.object({
      type: z.enum(["bug", "feature", "feedback"]),
      title: z.string().min(1).max(500),
      description: z.string().max(5000).optional(),
      submitterEmail: z.string().email().optional(),
      submitterName: z.string().max(100).optional(),
      metadata: z.record(z.string(), z.any()).optional(),
    }))
    .mutation(({ ctx, input }) => {
      return widgetSubmissionRepo.createSubmission(ctx.db, {
        projectId: ctx.widgetProject.id,
        ...input,
      });
    }),
});
```

## CORS Handling

Add CORS headers in `workers/app.ts` for widget API routes:

```typescript
// workers/app.ts — inside the fetch handler, before requestHandler
const url = new URL(request.url);

// Handle CORS for widget API
if (url.pathname.startsWith("/api/trpc/widget.")) {
  if (request.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*", // Or validate against project's allowedOrigins
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, x-widget-api-key",
        "Access-Control-Max-Age": "86400",
      },
    });
  }

  // For actual requests, add CORS headers to the response
  const response = await requestHandler(request, loadContext);
  response.headers.set("Access-Control-Allow-Origin", "*");
  response.headers.set("Access-Control-Allow-Headers", "Content-Type, x-widget-api-key");
  return response;
}
```

## Embed Script (public/widget.js)

The script that site owners paste into their HTML:

```javascript
// public/widget.js
(function(window, document) {
  "use strict";

  var WIDGET_BASE_URL = "__WIDGET_BASE_URL__"; // Replaced at build time or configured

  // Process command queue
  var config = { projectId: null, apiKey: null, position: "bottom-right", user: null };
  var queue = window.__WIDGET_QUEUE__ || [];

  function processCommand(args) {
    var cmd = args[0], opts = args[1] || {};
    switch (cmd) {
      case "init":
        config.apiKey = opts.apiKey;
        config.position = opts.position || config.position;
        createWidget();
        break;
      case "identify":
        config.user = { email: opts.email, name: opts.name };
        if (iframe) {
          iframe.contentWindow.postMessage({ type: "identify", user: config.user }, WIDGET_BASE_URL);
        }
        break;
      case "open":
        toggleWidget(true);
        break;
      case "close":
        toggleWidget(false);
        break;
    }
  }

  var iframe, trigger, container, isOpen = false;

  function createWidget() {
    // Container
    container = document.createElement("div");
    container.id = "__widget-container";
    container.style.cssText = "position:fixed;bottom:20px;" +
      (config.position === "bottom-left" ? "left:20px;" : "right:20px;") +
      "z-index:2147483647;font-family:system-ui,sans-serif;";

    // Trigger button
    trigger = document.createElement("button");
    trigger.style.cssText = "width:56px;height:56px;border-radius:50%;border:none;cursor:pointer;" +
      "background:#6366f1;color:white;font-size:24px;box-shadow:0 4px 12px rgba(0,0,0,0.15);" +
      "display:flex;align-items:center;justify-content:center;transition:transform 0.2s;";
    trigger.innerHTML = "💬";
    trigger.onclick = function() { toggleWidget(!isOpen); };
    trigger.onmouseenter = function() { trigger.style.transform = "scale(1.1)"; };
    trigger.onmouseleave = function() { trigger.style.transform = "scale(1)"; };

    // Iframe
    iframe = document.createElement("iframe");
    iframe.src = WIDGET_BASE_URL + "/widget?apiKey=" + encodeURIComponent(config.apiKey);
    iframe.style.cssText = "width:380px;height:520px;border:none;border-radius:12px;" +
      "box-shadow:0 8px 32px rgba(0,0,0,0.12);display:none;margin-bottom:12px;" +
      "background:white;";
    iframe.allow = "clipboard-write";

    container.appendChild(iframe);
    container.appendChild(trigger);
    document.body.appendChild(container);

    // Listen for messages from iframe
    window.addEventListener("message", function(e) {
      if (e.origin !== new URL(WIDGET_BASE_URL).origin) return;
      var data = e.data;
      if (data.type === "widget:close") toggleWidget(false);
      if (data.type === "widget:resize") iframe.style.height = data.height + "px";
    });
  }

  function toggleWidget(open) {
    isOpen = open;
    if (iframe) iframe.style.display = open ? "block" : "none";
    if (trigger) trigger.innerHTML = open ? "✕" : "💬";
  }

  // Process any queued commands
  queue.forEach(processCommand);

  // Replace queue with direct execution
  window.YourWidget = function() { processCommand(Array.prototype.slice.call(arguments)); };
})(window, document);
```

### Embed Code (what users copy-paste)

```html
<script>
  (function(w,d,s,o){
    w.__WIDGET_QUEUE__=w.__WIDGET_QUEUE__||[];w[o]=function(){w.__WIDGET_QUEUE__.push(arguments)};
    var js=d.createElement(s);js.src="https://YOUR_APP_DOMAIN/widget.js";js.async=1;
    d.head.appendChild(js);
  })(window,document,"script","YourWidget");

  YourWidget("init", { apiKey: "YOUR_PROJECT_API_KEY" });

  // Optional: identify logged-in users
  // YourWidget("identify", { email: "user@example.com", name: "Jane" });
</script>
```

## Widget Routes (iframe content)

### Layout (`app/routes/widget/_layout.tsx`)

Minimal layout — no app nav, no sidebar. Just the widget content with a postMessage bridge:

```typescript
import { Outlet, useSearchParams } from "react-router";

export default function WidgetLayout() {
  return (
    <div className="h-screen w-screen overflow-hidden bg-background text-foreground">
      <Outlet />
    </div>
  );
}
```

Key considerations:
- **No app chrome** — this renders inside a small iframe
- **postMessage bridge** — communicate resize/close events to parent
- **API key from query param** — passed from the embed script
- The widget routes should be compact, mobile-first UI

### Route Registration

```typescript
// app/routes.ts — add these routes
...prefix("widget", [
  layout("routes/widget/_layout.tsx", [
    index("routes/widget/index.tsx"),
    route("/submit", "routes/widget/submit.tsx"),
    route("/success", "routes/widget/success.tsx"),
  ]),
]),
```

## Admin Dashboard Pages

Create pages under the admin layout for managing widget projects:

1. **Project List** (`/admin/widget-projects`) — list all projects, create new ones, copy embed code
2. **Project Detail** (`/admin/widget-projects/:id`) — edit settings, view API key, see submissions
3. **Submissions** (`/admin/widget-submissions`) — view/manage all submissions with filtering

## Identified User Flow

For sites that want to identify their logged-in users with the widget:

```
Site Owner's App                          Your Widget
─────────────────                         ───────────
1. User logs in
2. Call: YourWidget("identify", {
     email: user.email,
     name: user.name,
     hmac: generateHMAC(user.email)  // Server-generated
   })
                              ───────►
3.                                     Verify HMAC using
                                       project's secret key
4.                                     Associate submissions
                                       with identified user
```

The HMAC prevents spoofing — the site owner generates it server-side using a secret from their project settings.

## Security Considerations

- **CORS**: Only allow origins listed in the project's `allowedOrigins` (or `*` if null)
- **Rate limiting**: Implement per-API-key rate limits to prevent abuse
- **HMAC verification**: For identified users, verify the HMAC to prevent impersonation
- **Input sanitization**: Sanitize all submission content to prevent XSS
- **CSP headers**: Set appropriate Content-Security-Policy on widget routes
- **API key rotation**: Allow project owners to rotate their API keys

## Execution Order

1. **Schema + Migration** — add tables, generate and apply migration
2. **Repositories** — data access functions
3. **tRPC Routes** — widget API with API key auth + admin management routes
4. **CORS** — handle cross-origin in workers/app.ts
5. **Widget Routes** — iframe content pages
6. **Embed Script** — public/widget.js
7. **Admin Pages** — project management + submissions viewer
8. **Embed Code Generator** — UI to copy the snippet

Adapt the submission types, form fields, and widget UI based on: **$ARGUMENTS**
