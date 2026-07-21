---
description: Initialize a new repository from the cf-saas starter template with a title and description
argument-hint: <project title> [--description "project description"]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Initialize New cf-saas Project

Create a new GitHub repository from the [cf-saas-starter-react-router](https://github.com/Casper-Studios/cf-saas-starter-react-router) template.

Project details: $ARGUMENTS

## Workflow

### Step 1: Parse Arguments

Extract the following from the user's input:

- **Title** (required): The name of the new repository (e.g., `my-saas-app`)
- **Description** (optional): A short description of the project

If the title is missing, ask the user to provide one.

Normalize the title to a valid GitHub repository name:
- Lowercase
- Replace spaces with hyphens
- Remove special characters

### Step 2: Verify Prerequisites

Run the following checks:

```bash
gh auth status
```

If the user is not authenticated, instruct them to run `gh auth login` first.

### Step 3: Create Repository from Template

Create the new repository under the **Casper-Studios** organization using the starter template:

```bash
gh repo create Casper-Studios/<repo-name> \
  --template Casper-Studios/cf-saas-starter-react-router \
  --description "<description>" \
  --private \
  --clone
```

- Always create the repo under the `Casper-Studios` org
- Default to **private** visibility
- Clone the repo locally after creation

### Step 4: Post-Setup

After cloning, navigate into the new project directory and:

1. **Update `package.json`** — Set the `name` field to the repo name
2. **Update `wrangler.jsonc`** (if it exists) — Set the `name` field to the repo name
3. **Install dependencies**:
   ```bash
   bun install
   ```
   If `bun` is not available, fall back to `npm install`.

### Step 5: Summary

Present the user with:

- Repository URL: `https://github.com/Casper-Studios/<repo-name>`
- Local path where the project was cloned
- Next steps: remind them to configure environment variables, set up D1 database, and run `bun run dev` to start developing
