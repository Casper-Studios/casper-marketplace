# Agent-Ready Codebase Checklist

Detailed criteria for each principle. Use this as the basis for auditing a codebase or guiding improvements.

## 1. Test Coverage

### What to Check
- Measure current line coverage percentage
- Identify uncovered lines and files
- Check if coverage is enforced in CI (fail builds below threshold)
- Check if coverage is enforced via agent hooks or git hooks

### Stack-Specific Tooling
- **Go**: `go test -coverprofile=coverage.out ./...` then `go tool cover -func=coverage.out`
- **TypeScript/JavaScript**: `jest --coverage`, `vitest --coverage`, `c8`, `nyc`
- **Python**: `pytest --cov`, `coverage run`
- **Ruby**: `simplecov`
- **Rust**: `cargo tarpaulin`, `cargo llvm-cov`
- **Java/Kotlin**: JaCoCo
- **Swift**: Xcode code coverage, `xcresult`

### Key Indicators
- **Strong**: 100% line coverage, coverage enforced in CI, coverage report used as a todo list
- **Adequate**: >90% coverage with clear policy on what's excluded
- **Weak**: <80% coverage or no coverage measurement at all

### Guidance
- At 100% coverage, there is a phase change: uncovered lines are always from recent changes, removing ambiguity about what needs testing
- Coverage is not about proving "no bugs" -- it forces the author (or agent) to demonstrate how every line behaves with an executable example
- Unreachable code surfaces immediately and gets deleted
- Edge cases are made explicit
- Code reviews become easier because reviewers see concrete behavior examples

## 2. File Structure and Naming

### What to Check
- Average file length (lines of code per file)
- Whether filenames communicate purpose (e.g. `billing/invoices/compute.ts` vs `utils/helpers.ts`)
- Whether directories map to domain concepts
- Presence of catch-all files (`utils.ts`, `helpers.ts`, `misc.ts`, `common.ts`)
- Whether related code is co-located

### Key Indicators
- **Strong**: Files under ~300 lines, filenames describe domain purpose, directory tree reads like a table of contents
- **Adequate**: Most files are focused, a few large files exist but are well-organized internally
- **Weak**: Large monolithic files (500+ lines), generic names (`utils`, `helpers`), flat directory structure

### Guidance
- Agents navigate by listing directories, reading filenames, and searching for strings -- the filesystem is the primary interface
- Small files reduce context truncation risk -- if a file fits entirely in the context window, the model works with complete information
- Many small well-scoped files outperform fewer large files for agent workflows
- Naming should make "what is this?" and "where does it go?" answerable at a glance

## 3. Type System Usage

### What to Check
- Whether the project uses a statically typed language or typed superset
- Whether types flow end-to-end (API boundary through database)
- Whether type names carry semantic meaning (e.g. `UserId` vs `string`, `SignedWebhookPayload` vs `any`)
- Whether API contracts are typed (OpenAPI, GraphQL schema, protobuf)
- Whether database types are enforced (column constraints, enums, check constraints)

### Stack-Specific Patterns
- **TypeScript**: Strict mode enabled, no `any` proliferation, branded types for IDs
- **Go**: Strong stdlib types, custom types for domain concepts, interfaces for boundaries
- **Python**: Type hints with mypy/pyright enforcement, Pydantic models
- **Ruby**: Sorbet or RBS type annotations, strong ActiveRecord validations
- **Rust**: Native type system, newtypes for domain concepts

### Key Indicators
- **Strong**: Typed language in strict mode, semantic type names, API contracts generated from schemas, database constraints enforced
- **Adequate**: Typed language with some gaps, most core paths typed
- **Weak**: Untyped language, `any`/`object` used broadly, no API contract schema

### Guidance
- Types eliminate entire categories of illegal states and transitions
- Types shrink the search space of possible actions the model can take
- Types double as source-of-truth documentation describing data flow
- Semantic type names (e.g. `WorkspaceSlug`, `InvoiceLineItem`) help agents understand intent immediately and search for related code
- Generic names like `T` or `data` are acceptable in small self-contained generics but not in business logic

## 4. Dev Environment Speed and Isolation

### What to Check
- Time to create a fresh dev environment from scratch
- Time to run the full test suite
- Whether multiple dev environments can run concurrently without conflicts
- Whether environment setup is a single command
- Whether ports, database names, caches, and background jobs are configurable or isolated

### Key Indicators
- **Strong**: Single command to create environment (<5 seconds), full test suite under 2 minutes, multiple concurrent environments supported, no port/DB conflicts
- **Adequate**: Documented setup process, tests run in reasonable time, some manual steps
- **Weak**: Multi-step manual setup, slow tests (>10 minutes), environments conflict with each other

### Guidance
- Agents run guardrails (tests, lints, type checks) frequently -- these must be fast
- The goal is a short feedback loop: make a small change, check it, fix it, repeat
- If spinning up an environment takes minutes and manual configuration, agents (and developers) will avoid doing it
- Git worktrees with automated setup scripts enable concurrent agent workflows
- Docker provides isolation but the principle holds regardless: no cross-talk between environments
- Third-party API calls should be cached or mocked for test speed

## 5. Automated Enforcement

### What to Check
- Whether linters run automatically (on save, on commit, or via agent hooks)
- Whether formatters auto-fix on commit or task completion
- Whether CI enforces all quality checks (lint, format, type check, test, coverage)
- Whether agent hooks or git hooks enforce checks before commits

### Stack-Specific Tooling
- **Go**: `gofmt`, `golangci-lint`, `go vet`
- **TypeScript**: `eslint`, `prettier`, `tsc --noEmit`
- **Python**: `ruff`, `mypy`, `black`
- **Ruby**: `rubocop`, `sorbet`
- **Rust**: `clippy`, `rustfmt`

### Key Indicators
- **Strong**: Auto-formatting on save/commit, strict linter config, all checks in CI, agent hooks enforce checks
- **Adequate**: Linters configured, CI runs checks, some manual steps
- **Weak**: No linters, no formatting enforcement, CI only runs tests

### Guidance
- Every automated check removes a degree of freedom from the agent
- Fewer degrees of freedom means fewer opportunities for the agent to drift
- Checks should be cheap enough to run constantly without slowing the workflow
- Configure linters and formatters to be as strict as reasonable for the project
