---
name: emails
description: Email template patterns using Resend with type-safe generator functions
user-invocable: false
---

# Email Templates

## Overview
Email templates are stored in `app/lib/constants/emails.ts` with type-safe generator functions. Emails are sent via Resend.

## File Structure
```
app/lib/
  constants/
    index.ts        # Re-exports all constants including emails
    emails.ts       # Email templates and generator functions
  email.ts          # sendEmail utility function
```

## Generator Function Rules
- **ALWAYS** store email generators in `app/lib/constants/emails.ts`
- **ALWAYS** define a TypeScript interface for each email's parameters (e.g., `PasswordResetEmailParams`)
- **ALWAYS** name generator functions as `generateXxxEmail(params: XxxEmailParams): string`
- **ALWAYS** destructure params at the start of the function
- **ALWAYS** use template literals with `${variable}` syntax (not `{{placeholder}}` replacement)
- **ALWAYS** return a complete HTML string from each generator
- **ALWAYS** re-export generators from `app/lib/constants/index.ts`
- **ALWAYS** import generators from `@/lib/constants` when using them

## Shared Wrapper Pattern
- Create a private `EMAIL_WRAPPER(content: string, title: string)` function for consistent styling
- The wrapper should include: DOCTYPE, html/head/body tags, max-width container, footer
- Individual generators build the `content` and pass it to the wrapper

## Sending Function (`app/lib/email.ts`)
- Use Resend SDK to send emails
- Throw `EmailError` from `@/models/errors` on failure
- Function signature: `sendEmail(apiKey, from, to, subject, html)`

## HTML Styling Rules
- Use inline CSS only (email clients don't support external stylesheets)
- Max width: 600px for content container
- Use web-safe fonts with fallbacks: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif`
- Primary button color: `#003362`
- Keep important content above the fold

## Usage Pattern
```typescript
import { generateXxxEmail } from "@/lib/constants";

const html = generateXxxEmail({ name: "User", resetUrl: "https://..." });
await sendEmail(apiKey, from, to, "Subject", html);
```
