---
name: frontend-architecture
description: Use when structuring a frontend application's folders, state boundaries, and module dependencies so it scales past a handful of components.
category: frontend
tags: [frontend, architecture, feature-folders]
maturity: stable
updated: 2026-08-21
---

## Purpose

Frontend codebases without a deliberate structure tend to accumulate tangled imports between unrelated features and shared 'god' utility folders that everyone is afraid to touch. This skill defines a feature-folder architecture with clear module boundaries, a layered approach to shared code, and rules for where state, API calls, and UI components live.

It applies regardless of framework (React, Angular, Vue) since the core idea — organize by feature, not by technical layer, and control cross-feature imports — is framework-agnostic.

## When to use / When NOT to use

**Use this skill when:**

- You are starting a new frontend application or a significant new area within one.
- The codebase has grown past a few dozen components and imports between features are becoming tangled.
- You need to onboard new engineers quickly and the current structure isn't self-explanatory.

**Do NOT use this skill when:**

- The application is a small, single-purpose tool with a handful of screens — a flat structure is simpler and sufficient.
- You're mid-sprint on a feature; a full restructuring is a separate, deliberate piece of work, not a side effect of a feature change.

## Prerequisites

- skills/40-frontend/frontend-state-and-forms/SKILL.md for how state fits within feature boundaries.
- skills/20-architecture/api-design-rest/SKILL.md (or GraphQL equivalent) for how features consume backend APIs.

## Workflow

1. **Organize top-level folders by feature, not by type** - features/orders, features/customers — not components/, hooks/, services/ folders spanning all features.
2. **Keep a feature's UI, state, and API calls colocated** - Everything needed to understand feature/orders lives inside that folder, minimizing cross-folder hunting.
3. **Expose a small public surface per feature** - Each feature folder has an index (barrel) file exporting only what other features are allowed to use.
4. **Put truly cross-cutting code in a shared/ layer** - Design system components, generic hooks, and API client setup that many features need live in shared/, not duplicated per feature.
5. **Forbid deep imports across feature boundaries** - Other features import only via a feature's public index, never reaching into its internal files directly.
6. **Keep routing as a thin composition layer** - The app shell/router composes features together; it shouldn't contain business logic itself.
7. **Enforce boundaries with lint rules** - Use an ESLint import-boundary plugin to fail CI if a feature imports another feature's internals.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Two features need to share a UI component | Promote it to the shared/ design-system layer, not duplicate it or import across feature boundaries. |
| A feature is growing very large with many sub-areas | Split it into sub-features with their own folders and public index files, keeping the pattern recursive. |
| State is needed by many unrelated features | Consider whether it truly is cross-cutting (e.g. current user) and belongs in a shared/app-level store, or whether features are too tightly coupled. |
| A small app has only 3-4 screens | A lighter, flatter structure is fine; don't over-engineer feature folders for trivial scope. |
| Import boundary violations keep slipping through review | Add an automated ESLint boundary rule rather than relying on manual review vigilance. |

## Reference implementation

A feature-folder layout with enforced public surfaces:

```text
src/
  app/                  # routing, app shell, composition root
  shared/
    ui/                 # design-system components
    api/                # base HTTP client, auth interceptor
    hooks/              # generic, feature-agnostic hooks
  features/
    orders/
      components/       # OrderList, OrderDetail (internal)
      api/              # ordersApi.ts (internal)
      state/            # ordersSlice.ts (internal)
      index.ts          # public surface: exports OrdersPage only
    customers/
      components/
      api/
      state/
      index.ts

// features/orders/index.ts
export { OrdersPage } from './components/OrdersPage';
// Nothing else from orders/ is importable from outside this folder.
```

- Only OrdersPage is exported; components/OrderList.tsx cannot be imported directly from customers/.
- This mirrors a module boundary similar to a bounded context (skills/20-architecture/domain-driven-design/SKILL.md) at the frontend layer.

### ESLint rule enforcing feature import boundaries (TypeScript config)

Failing the build if a feature reaches into another feature's internals:

```typescript
// .eslintrc.cjs
module.exports = {
  rules: {
    'import/no-restricted-paths': ['error', {
      zones: [{
        target: './src/features/*/!(index.ts)',
        from: './src/features/*',
        except: ['./index.ts'],
        message: 'Import only a feature\'s public index, not its internals.'
      }]
    }]
  }
};
```

## Checklist

- [ ] Top-level folders are organized by feature, not by technical type.
- [ ] Each feature exposes a small public surface via an index file; internals are never imported directly by other features.
- [ ] Truly cross-cutting UI/hooks/API code lives in a shared/ layer, not duplicated across features.
- [ ] The app/routing layer composes features but contains no business logic itself.
- [ ] An automated lint rule enforces import boundaries between features.
- [ ] New engineers can find everything relevant to a feature inside one folder.

## Anti-patterns

- **Organize-by-type folders** - components/, hooks/, services/ folders spanning every feature, forcing you to hunt across three folders to understand one feature.
- **Deep cross-feature imports** - import { OrderRow } from '../orders/components/OrderRow' from inside the customers feature, creating hidden coupling.
- **Shared folder as a dumping ground** - Putting feature-specific logic into shared/ because it's convenient, turning it into an unmaintainable catch-all.
- **Business logic in the router** - Embedding data-fetching and business rules directly in route definitions instead of within feature modules.
- **No enforced boundaries** - Relying purely on code review discipline to prevent boundary violations, which erodes over time without lint automation.

## Verification

- An ESLint boundary check fails CI when a feature imports another feature's internal file.
- A new engineer can implement a small change to one feature by only reading files inside that feature's folder.
- No feature-specific component or hook exists inside the shared/ folder.
- Removing a feature folder entirely does not break any other feature (verified by a dependency check or trial removal).

## References

- skills/40-frontend/frontend-state-and-forms/SKILL.md
- skills/20-architecture/domain-driven-design/SKILL.md
- Bulletproof React — feature-folder architecture guidance.
