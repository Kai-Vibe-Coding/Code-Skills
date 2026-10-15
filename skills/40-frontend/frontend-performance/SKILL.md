---
name: frontend-performance
description: Use when a frontend application's load time or interaction responsiveness needs to be diagnosed and improved against Core Web Vitals targets.
category: frontend
tags: [performance, core-web-vitals, bundling]
maturity: stable
updated: 2026-08-21
---

## Purpose

Slow-loading or janky frontends directly hurt conversion, SEO, and user satisfaction, yet performance problems are often invisible in local development on fast machines and networks. This skill covers measuring against Core Web Vitals (LCP, INP, CLS), diagnosing common causes (oversized bundles, render-blocking resources, layout shifts), and applying targeted fixes.

It emphasizes measuring in production-like conditions before optimizing, since intuition about what's slow is frequently wrong without real data.

## When to use / When NOT to use

**Use this skill when:**

- Core Web Vitals or user reports indicate slow load or laggy interactions.
- A bundle analysis shows unexpectedly large JavaScript payloads.
- You are reviewing a new feature that adds significant new dependencies or assets.

**Do NOT use this skill when:**

- The application is an internal admin tool with a handful of known users and no measured performance complaints — don't over-invest without evidence of a problem.
- You're chasing a micro-optimization with no measurable user impact instead of a proven bottleneck.

## Prerequisites

- A real-user-monitoring (RUM) or synthetic Lighthouse/WebPageTest setup to measure Core Web Vitals.
- skills/40-frontend/frontend-architecture/SKILL.md for where code-splitting boundaries naturally fall (feature folders).

## Workflow

1. **Measure current Core Web Vitals in production-like conditions** - Use Lighthouse, WebPageTest, or field RUM data — not just a fast dev machine on localhost.
2. **Identify the largest contributor to LCP** - Usually the largest above-the-fold image or a render-blocking script/font; profile before guessing.
3. **Code-split by route and by feature** - Load only the JavaScript needed for the current page; lazy-load rarely used features.
4. **Optimize images and fonts** - Serve responsive, modern-format images (WebP/AVIF) and use font-display: swap to avoid invisible-text flashes.
5. **Reserve layout space for async content** - Set explicit width/height or aspect-ratio for images and ads to prevent Cumulative Layout Shift.
6. **Defer non-critical JavaScript** - Analytics, chat widgets, and other non-essential scripts load after the main content, not blocking it.
7. **Reduce main-thread work for interaction responsiveness** - Break up long tasks and avoid heavy synchronous computation on user input handlers to improve INP.
8. **Re-measure after each change** - Confirm each optimization actually moved the metric in production-like conditions before moving to the next one.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Bundle analysis shows one large third-party library | Lazy-load it behind the feature that needs it, or evaluate a lighter alternative. |
| LCP element is a hero image | Preload it with <link rel='preload'> and serve a properly sized, modern-format version. |
| CLS spikes when an ad or embed loads | Reserve its layout space up front with explicit dimensions or a skeleton placeholder. |
| INP is poor on a search-as-you-type input | Debounce the input handler and move heavy filtering off the main thread or into smaller chunks. |
| A performance fix has no measurable effect on real metrics | Revert or deprioritize it; don't keep complexity for a change that didn't help. |

## Reference implementation

Route-based code splitting to reduce the initial JavaScript payload:

```typescript
import { lazy, Suspense } from 'react';

const OrdersPage = lazy(() => import('./features/orders/OrdersPage'));
const ReportsPage = lazy(() => import('./features/reports/ReportsPage'));

function AppRoutes() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/reports" element={<ReportsPage />} />
      </Routes>
    </Suspense>
  );
}
```

- Each route's bundle downloads only when that route is visited, shrinking the initial load for users who only visit one section.
- PageSkeleton reserves layout space during the async load, helping avoid a CLS spike when content arrives.

### Preloading the LCP image and reserving its layout space (HTML)

Reducing LCP time and preventing layout shift for the hero image:

```html
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">

<img
  src="/hero.webp"
  width="1200"
  height="600"
  fetchpriority="high"
  alt="Dashboard overview"
/>
```

## Checklist

- [ ] Core Web Vitals (LCP, INP, CLS) are measured in production-like conditions, not just local dev.
- [ ] JavaScript is code-split by route/feature so users download only what the current page needs.
- [ ] Images use modern formats, correct sizing, and explicit width/height to prevent layout shift.
- [ ] The LCP element (usually a hero image) is preloaded and prioritized.
- [ ] Non-critical third-party scripts are deferred and don't block the main content.
- [ ] Each performance change is re-measured to confirm it actually improved the target metric.

## Anti-patterns

- **Optimizing on intuition alone** - Making performance changes without measuring first, potentially fixing a non-bottleneck while ignoring the real one.
- **One giant bundle** - Shipping the entire application's JavaScript on every route instead of code-splitting by feature.
- **Unsized images causing layout shift** - Omitting width/height on images, causing the page to jump as they load and hurting CLS.
- **Blocking scripts before content** - Loading analytics or chat widget scripts synchronously in the <head>, delaying the main content's render.
- **Chasing Lighthouse score over real user metrics** - Optimizing purely for a synthetic lab score without confirming it improves real-user (field) Core Web Vitals.

## Verification

- Lighthouse or field RUM data shows LCP, INP, and CLS within 'Good' thresholds for key pages.
- A bundle analyzer report confirms route-level code splitting is producing separate chunks per feature.
- No above-the-fold image or embed lacks explicit dimensions, confirmed by a CLS audit.
- A before/after measurement accompanies any change made specifically for performance.

## References

- web.dev — Core Web Vitals.
- skills/40-frontend/frontend-architecture/SKILL.md
- Lighthouse and WebPageTest documentation.
