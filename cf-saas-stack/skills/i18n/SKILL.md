---
name: i18n
description: Internationalization patterns using remix-i18next and react-i18next
user-invocable: false
---

# i18n (Internationalization) Guidelines

## Overview
This project uses **remix-i18next** with **i18next** and **react-i18next** for internationalization. Translations are bundled (not loaded from filesystem) for Cloudflare Workers compatibility.

## Core Rules

### Never hardcode user-facing strings
- All user-facing text must use `t()` from `useTranslation()`
- Use semantic dot-notation keys: `t("dashboard.total_users")` not `t("totalUsers")`
- Group keys by namespace: `common`, `auth`, `admin`, `home`, `validation`

### Always export `handle` with i18n namespaces on route files
```typescript
export const handle = { i18n: ["admin"] };
```

### Translation file organization
- Files live in `app/locales/{lng}/{namespace}.json`
- Each namespace maps to a JSON file
- Keys use snake_case with dot notation for nesting

### Using translations in components
```typescript
import { useTranslation } from "react-i18next";

function MyComponent() {
  const { t } = useTranslation("namespace");
  return <h1>{t("section.key")}</h1>;
}
```

### Using translations in loaders/meta
```typescript
import { i18nServer } from "@/i18n/i18n.server";

export async function loader({ request }: Route.LoaderArgs) {
  const t = await i18nServer.getFixedT(request, "namespace");
  return { title: t("page.title") };
}
```

### Interpolation
```json
{ "greeting": "Hello, {{name}}!" }
```
```typescript
t("greeting", { name: user.name })
```

### Pluralization
```json
{ "items": "{{count}} item", "items_other": "{{count}} items" }
```

### Zod validation errors
- Use the custom error map from `app/lib/zod-i18n.ts`
- Validation keys live in `app/locales/en/validation.json`

## How to Add a New Language

1. Create translation files: `app/locales/{lng}/common.json`, `auth.json`, etc.
2. Add the locale code to `supportedLngs` in `app/i18n/i18n.ts`
3. Add the language label to `languageLabels` in `app/components/language-switcher.tsx`
4. Add the date-fns locale mapping in `app/lib/date-utils.ts`
5. Test with `bun run dev` and navigate to `/{lng}/` prefix routes

## Key Files
- `app/i18n/i18n.ts` — Shared config (supported languages, namespaces)
- `app/i18n/i18n.server.ts` — Server-side RemixI18Next instance
- `app/i18n/i18n.client.ts` — Client-side i18next initialization
- `app/i18n/i18n.d.ts` — TypeScript type augmentation for translation keys
- `app/locales/en/*.json` — English translation files
- `app/components/language-switcher.tsx` — Language switcher component
- `app/lib/zod-i18n.ts` — Zod error map for translated validation
- `app/lib/date-utils.ts` — date-fns locale helper
