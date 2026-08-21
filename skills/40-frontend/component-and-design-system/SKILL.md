---
name: component-and-design-system
description: Use when building or consuming a shared component library and you need consistent, reusable, well-documented UI building blocks across an application or organization.
category: frontend
tags: [design-system, components, storybook]
maturity: stable
updated: 2026-08-21
---

## Purpose

Without a shared design system, every team reinvents buttons, inputs, and layout primitives slightly differently, producing visual and behavioral inconsistency and duplicated accessibility bugs. This skill covers structuring a component library with clear composition patterns, documented variants, and a workflow (Storybook) for developing and reviewing components in isolation.

It also addresses the boundary between 'dumb' presentational components and feature-specific components that consume them, so the design system stays generic and reusable.

## When to use / When NOT to use

**Use this skill when:**

- You are building a new shared UI component intended for reuse across features or teams.
- Visual or behavioral inconsistency is appearing across similar UI elements in different parts of the app.
- You need a workflow to develop and visually review components independent of a full app build.

**Do NOT use this skill when:**

- The component is genuinely one-off and specific to a single feature screen with no reuse potential.
- The organization already has an adopted third-party design system that fully covers the need — extend it rather than building a parallel one.

## Prerequisites

- skills/40-frontend/accessibility-wcag/SKILL.md, since every shared component must meet baseline accessibility requirements.
- skills/40-frontend/frontend-architecture/SKILL.md for where shared components live (shared/ui/).

## Workflow

1. **Identify genuinely reusable UI patterns** - Extract a component into the design system only after it (or something very similar) is needed in 2+ places.
2. **Design components as composable primitives** - Prefer small composable pieces (Button, Stack, Card) over large monolithic components with many boolean props.
3. **Define variants via a constrained prop API** - Use a fixed set of variant values (e.g. variant='primary' | 'secondary' | 'danger') rather than open-ended style props.
4. **Document each component in Storybook** - Every variant and state (loading, disabled, error) gets its own story for visual review and manual QA.
5. **Bake accessibility in by default** - Correct semantic HTML, ARIA attributes, and keyboard behavior are the component's responsibility, not each consumer's.
6. **Version and changelog the design system** - Treat it as a versioned package; breaking changes to shared components go through a deliberate migration path.
7. **Test components in isolation** - Unit/interaction tests run against the component alone, not requiring a full feature page to render it.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A UI pattern is used in exactly one feature so far | Keep it local to that feature; don't prematurely generalize into the design system. |
| A UI pattern is needed in a second, unrelated feature | Extract it into shared/ui with a documented, constrained prop API. |
| A component needs many visual variations | Use a small, fixed variant enum plus composition, not an ever-growing list of boolean flags. |
| A component's behavior differs subtly per consuming team | Support it via slots/children composition rather than an escape-hatch style override prop that undermines consistency. |
| A breaking change is needed to a widely used component | Version it and provide a migration guide/codemod rather than changing behavior silently under consumers' feet. |

## Reference implementation

A composable, accessible Button primitive with a constrained variant API:

```typescript
type ButtonVariant = 'primary' | 'secondary' | 'danger';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  isLoading?: boolean;
}

export function Button({
  variant = 'primary',
  isLoading = false,
  disabled,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`btn btn--${variant}`}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...rest}
    >
      {isLoading ? <Spinner aria-hidden="true" /> : children}
    </button>
  );
}
```

- aria-busy communicates loading state to assistive technology, not just visually via the spinner.
- The variant prop is a closed union type, preventing arbitrary ad hoc style strings from being passed in.

### A Storybook story documenting every Button state (TypeScript)

Enabling visual review and manual QA of every variant and state in isolation:

```typescript
const meta: Meta<typeof Button> = { component: Button, title: 'Design System/Button' };
export default meta;

export const Primary: StoryObj<typeof Button> = { args: { variant: 'primary', children: 'Save' } };
export const Danger: StoryObj<typeof Button> = { args: { variant: 'danger', children: 'Delete' } };
export const Loading: StoryObj<typeof Button> = { args: { isLoading: true, children: 'Saving...' } };
```

## Checklist

- [ ] A component is promoted to the design system only after being needed in two or more places.
- [ ] Component variant APIs are closed/constrained, not open-ended style props.
- [ ] Every component's variants and states are documented as Storybook stories.
- [ ] Accessibility (semantics, ARIA, keyboard) is built into the component, not left to consumers.
- [ ] Breaking changes to shared components go through versioning and a migration path.
- [ ] Components are tested in isolation, without requiring a full page render.

## Anti-patterns

- **Premature abstraction** - Building a 'flexible' shared component for a UI pattern used in only one place, guessing at future needs.
- **Prop explosion** - A Button component with a dozen boolean props (isRounded, isWide, isCompact...) instead of a small, composable variant system.
- **Style override escape hatches** - Allowing arbitrary className/style overrides that let every consumer bypass the design system's consistency.
- **Accessibility left to consumers** - Shipping a shared component with no ARIA attributes or keyboard support, expecting each consuming team to patch it individually.
- **Silent breaking changes** - Changing a shared component's behavior in place without versioning, breaking every consumer without warning.

## Verification

- Every shared component has Storybook stories covering its documented variants and states.
- An automated accessibility check (e.g. axe) passes for each component's stories.
- No shared component accepts an arbitrary style/className override that bypasses its variant system.
- A breaking change to a shared component is accompanied by a version bump and migration notes.

## References

- skills/40-frontend/accessibility-wcag/SKILL.md
- skills/40-frontend/frontend-architecture/SKILL.md
- Storybook documentation.
