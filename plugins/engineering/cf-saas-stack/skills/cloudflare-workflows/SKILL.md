---
name: cloudflare-workflows
description: Cloudflare Workflows patterns for background tasks and async processing
user-invocable: false
---

# Cloudflare Workflows

Use Cloudflare Workflows for background tasks instead of running them in request handlers.

## When to Use Workflows
- AI/LLM API calls (Gemini, Anthropic, etc.)
- Long-running operations (> 1-2 seconds)
- Tasks that shouldn't block user actions
- Operations that need retry/resilience

## Workflow Structure
```typescript
// workflows/my-task.ts
import { WorkflowEntrypoint, type WorkflowEvent, type WorkflowStep, env } from "cloudflare:workers";
import { getDb } from "@/db";

export interface MyTaskWorkflowPayload {
  resourceId: string;
  userId: string;
}

export class MyTaskWorkflow extends WorkflowEntrypoint<Env, MyTaskWorkflowPayload> {
  async run(event: WorkflowEvent<MyTaskWorkflowPayload>, step: WorkflowStep) {
    const { resourceId, userId } = event.payload;

    // Step 1: Do work (each step is retried on failure)
    const result = await step.do("process-data", async () => {
      return { processed: true };
    });

    // Step 2: Update database
    await step.do("save-result", async () => {
      const db = await getDb(this.env.DATABASE);
      // Update record...
    });

    return { success: true };
  }
}
```

## Registration Checklist

1. **wrangler.jsonc** - Add workflow binding:
```json
{ "binding": "MY_TASK_WORKFLOW", "name": "landfall-my-task-workflow", "class_name": "MyTaskWorkflow" }
```

2. **workers/app.ts** - Export workflow:
```typescript
export { MyTaskWorkflow } from "../workflows/my-task";
```

3. **app/trpc/index.ts** - Add to context:
```typescript
workflows: {
  MyTaskWorkflow: opts.cfContext.MY_TASK_WORKFLOW,
}
```

4. **Regenerate types**: `bun run typegen`

## Triggering from tRPC
```typescript
try {
  await ctx.workflows.MyTaskWorkflow.create({
    params: { resourceId, userId: ctx.auth.user.id },
  });
} catch (error) {
  log.error({ err: error }, "Failed to start workflow");
  // Don't fail the request if workflow fails to start
}
```

## Key Patterns
- **Non-blocking**: User action completes immediately, workflow runs async
- **Idempotent steps**: Each `step.do()` may retry - ensure operations are safe to repeat
- **Error handling**: Catch workflow start errors, don't fail the user's request
