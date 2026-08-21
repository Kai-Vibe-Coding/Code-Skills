---
name: accessibility-wcag
description: Use when building or reviewing UI components and pages to ensure they meet WCAG 2.1 AA accessibility requirements for keyboard, screen reader, and visual users.
category: frontend
tags: [accessibility, wcag, a11y]
maturity: stable
updated: 2026-08-21
---

## Purpose

Inaccessible UI excludes users with disabilities and, in many jurisdictions, creates legal compliance risk. This skill establishes practical, testable accessibility practices — semantic HTML, keyboard operability, focus management, and sufficient color contrast — targeting WCAG 2.1 Level AA as the baseline for all shared and feature components.

It treats accessibility as a build-time and test-time concern (linting, automated checks, manual keyboard/screen-reader passes) rather than a final audit bolted on before release.

## When to use / When NOT to use

**Use this skill when:**

- You are building any new interactive UI component or page.
- You are reviewing a PR that adds or changes UI markup.
- An accessibility audit or user report has flagged an issue that needs remediation.

**Do NOT use this skill when:**

- Never — accessibility is a baseline requirement for user-facing UI, not an optional add-on to skip for any feature.
- For purely internal/non-UI backend services with no rendered interface, this skill doesn't apply directly.

## Prerequisites

- skills/40-frontend/component-and-design-system/SKILL.md, since baking accessibility into shared components benefits every consumer.
- A screen reader available for manual testing (VoiceOver, NVDA, or JAWS) and a keyboard-only testing habit.

## Workflow

1. **Use semantic HTML elements first** - Prefer <button>, <nav>, <label> over generic <div>s with click handlers and ARIA roles bolted on.
2. **Ensure full keyboard operability** - Every interactive element must be reachable and operable via Tab/Shift+Tab/Enter/Space/Arrow keys alone.
3. **Manage focus explicitly for dynamic UI** - Move focus to a newly opened modal's first focusable element and return it to the trigger on close.
4. **Provide accessible names for all controls** - Every input, button, and icon-only control has a label, aria-label, or aria-labelledby with a meaningful name.
5. **Verify color contrast meets AA thresholds** - Text has at least a 4.5:1 contrast ratio (3:1 for large text) against its background.
6. **Announce dynamic content changes** - Use aria-live regions for status messages, errors, and async content updates that sighted users would notice visually.
7. **Automate what can be automated** - Run axe-core (or equivalent) in CI and Storybook to catch a baseline of issues automatically.
8. **Manually test with keyboard and a screen reader** - Automated tools catch roughly a third of issues; a manual pass is required before shipping significant new UI.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Building a custom dropdown/menu component | Follow the WAI-ARIA Authoring Practices pattern for that widget exactly, including keyboard interaction and roles. |
| A modal dialog is opened | Trap focus within it, move focus to it on open, and restore focus to the trigger on close. |
| An icon-only button has no visible text | Add aria-label with a clear description of the action, not just the icon name. |
| A form field fails validation | Associate the error message with the input via aria-describedby and announce it via aria-live, not color alone. |
| Contrast fails for a brand color on a given background | Adjust the color or use a darker/lighter shade meeting AA, rather than shipping non-compliant contrast. |

## Reference implementation

A focus-trapped modal moving focus on open and restoring it on close:

```typescript
function Modal({ isOpen, onClose, children, triggerRef }: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const firstFocusable = dialogRef.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();
    return () => triggerRef.current?.focus();
  }, [isOpen]);

  if (!isOpen) return null;
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="modal-title" ref={dialogRef}>
      <h2 id="modal-title">Confirm action</h2>
      {children}
      <button onClick={onClose} aria-label="Close dialog">×</button>
    </div>
  );
```

- aria-modal='true' plus role='dialog' tells assistive technology to treat background content as inert while the modal is open.
- Focus returning to triggerRef on close prevents keyboard users from losing their place in the page.

### An accessible, announced form error (TypeScript/JSX)

Linking an error message to its field and announcing it to screen readers:

```typescript
<label htmlFor="email">Email</label>
<input
  id="email"
  aria-invalid={!!error}
  aria-describedby={error ? 'email-error' : undefined}
/>
{error && (
  <p id="email-error" role="alert">
    {error}
  </p>
)}
```

## Checklist

- [ ] Every interactive control is operable via keyboard alone (Tab, Enter, Space, Arrow keys as appropriate).
- [ ] Every control has an accessible name (label, aria-label, or aria-labelledby).
- [ ] Modals and popovers trap and restore focus correctly on open/close.
- [ ] Text and UI elements meet WCAG AA color contrast ratios.
- [ ] Dynamic status/error updates are announced via aria-live or role='alert'.
- [ ] axe-core (or equivalent) runs automatically in CI/Storybook, and a manual keyboard/screen-reader pass is done for significant new UI.

## Anti-patterns

- **Div soup with click handlers** - Using <div onClick={...}> for a button instead of a real <button>, losing keyboard operability and semantics for free.
- **Icon-only controls with no label** - Shipping a trash-can icon button with no aria-label, leaving screen reader users with an unnamed 'button' announcement.
- **Focus lost on modal open/close** - Opening a modal without moving focus into it, leaving keyboard users stranded on background content.
- **Color-only error indication** - Marking an invalid field only with a red border and no text/ARIA association, invisible to screen reader and colorblind users.
- **Accessibility as a pre-launch audit only** - Deferring all accessibility checks to a one-time audit right before release instead of continuous automated and manual checks.

## Verification

- axe-core (or equivalent) reports zero critical/serious violations in CI for new/changed components.
- A manual keyboard-only pass can complete every core user flow without a mouse.
- A screen reader (VoiceOver/NVDA) announces meaningful names and state for every interactive element in the flow.
- Automated contrast checking confirms all text meets WCAG AA thresholds.

## References

- WCAG 2.1 Level AA success criteria (W3C).
- WAI-ARIA Authoring Practices Guide.
- skills/40-frontend/component-and-design-system/SKILL.md
