SKILLS = [
    dict(
        dir="40-frontend", slug="accessibility-wcag", category="frontend",
        tags=["accessibility", "wcag", "a11y"],
        desc="Use when building or reviewing UI components and pages to ensure they meet WCAG 2.1 AA accessibility requirements for keyboard, screen reader, and visual users.",
        purpose=[
            "Inaccessible UI excludes users with disabilities and, in many jurisdictions, creates legal "
            "compliance risk. This skill establishes practical, testable accessibility practices — semantic "
            "HTML, keyboard operability, focus management, and sufficient color contrast — targeting WCAG 2.1 "
            "Level AA as the baseline for all shared and feature components.",
            "It treats accessibility as a build-time and test-time concern (linting, automated checks, manual "
            "keyboard/screen-reader passes) rather than a final audit bolted on before release.",
        ],
        when_use=[
            "You are building any new interactive UI component or page.",
            "You are reviewing a PR that adds or changes UI markup.",
            "An accessibility audit or user report has flagged an issue that needs remediation.",
        ],
        when_not=[
            "Never — accessibility is a baseline requirement for user-facing UI, not an optional add-on to skip for any feature.",
            "For purely internal/non-UI backend services with no rendered interface, this skill doesn't apply directly.",
        ],
        prereqs=[
            "skills/40-frontend/component-and-design-system/SKILL.md, since baking accessibility into shared components benefits every consumer.",
            "A screen reader available for manual testing (VoiceOver, NVDA, or JAWS) and a keyboard-only testing habit.",
        ],
        workflow=[
            ("Use semantic HTML elements first", "Prefer <button>, <nav>, <label> over generic <div>s with click handlers and ARIA roles bolted on."),
            ("Ensure full keyboard operability", "Every interactive element must be reachable and operable via Tab/Shift+Tab/Enter/Space/Arrow keys alone."),
            ("Manage focus explicitly for dynamic UI", "Move focus to a newly opened modal's first focusable element and return it to the trigger on close."),
            ("Provide accessible names for all controls", "Every input, button, and icon-only control has a label, aria-label, or aria-labelledby with a meaningful name."),
            ("Verify color contrast meets AA thresholds", "Text has at least a 4.5:1 contrast ratio (3:1 for large text) against its background."),
            ("Announce dynamic content changes", "Use aria-live regions for status messages, errors, and async content updates that sighted users would notice visually."),
            ("Automate what can be automated", "Run axe-core (or equivalent) in CI and Storybook to catch a baseline of issues automatically."),
            ("Manually test with keyboard and a screen reader", "Automated tools catch roughly a third of issues; a manual pass is required before shipping significant new UI."),
        ],
        decision=[
            ("Building a custom dropdown/menu component", "Follow the WAI-ARIA Authoring Practices pattern for that widget exactly, including keyboard interaction and roles."),
            ("A modal dialog is opened", "Trap focus within it, move focus to it on open, and restore focus to the trigger on close."),
            ("An icon-only button has no visible text", "Add aria-label with a clear description of the action, not just the icon name."),
            ("A form field fails validation", "Associate the error message with the input via aria-describedby and announce it via aria-live, not color alone."),
            ("Contrast fails for a brand color on a given background", "Adjust the color or use a darker/lighter shade meeting AA, rather than shipping non-compliant contrast."),
        ],
        code_lang="typescript",
        code_intro="A focus-trapped modal moving focus on open and restoring it on close:",
        code=(
            "function Modal({ isOpen, onClose, children, triggerRef }: ModalProps) {\n"
            "  const dialogRef = useRef<HTMLDivElement>(null);\n"
            "\n"
            "  useEffect(() => {\n"
            "    if (!isOpen) return;\n"
            "    const firstFocusable = dialogRef.current?.querySelector<HTMLElement>(\n"
            "      'button, [href], input, select, textarea, [tabindex]:not([tabindex=\"-1\"])'\n"
            "    );\n"
            "    firstFocusable?.focus();\n"
            "    return () => triggerRef.current?.focus();\n"
            "  }, [isOpen]);\n"
            "\n"
            "  if (!isOpen) return null;\n"
            "  return (\n"
            "    <div role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"modal-title\" ref={dialogRef}>\n"
            "      <h2 id=\"modal-title\">Confirm action</h2>\n"
            "      {children}\n"
            "      <button onClick={onClose} aria-label=\"Close dialog\">\u00d7</button>\n"
            "    </div>\n"
            "  );\n"
        ),
        code_notes=[
            "aria-modal='true' plus role='dialog' tells assistive technology to treat background content as inert while the modal is open.",
            "Focus returning to triggerRef on close prevents keyboard users from losing their place in the page.",
        ],
        code2_heading="An accessible, announced form error (TypeScript/JSX)",
        code2=("typescript",
            "Linking an error message to its field and announcing it to screen readers:",
            "<label htmlFor=\"email\">Email</label>\n"
            "<input\n"
            "  id=\"email\"\n"
            "  aria-invalid={!!error}\n"
            "  aria-describedby={error ? 'email-error' : undefined}\n"
            "/>\n"
            "{error && (\n"
            "  <p id=\"email-error\" role=\"alert\">\n"
            "    {error}\n"
            "  </p>\n"
            ")}\n"
        ),
        checklist=[
            "Every interactive control is operable via keyboard alone (Tab, Enter, Space, Arrow keys as appropriate).",
            "Every control has an accessible name (label, aria-label, or aria-labelledby).",
            "Modals and popovers trap and restore focus correctly on open/close.",
            "Text and UI elements meet WCAG AA color contrast ratios.",
            "Dynamic status/error updates are announced via aria-live or role='alert'.",
            "axe-core (or equivalent) runs automatically in CI/Storybook, and a manual keyboard/screen-reader pass is done for significant new UI.",
        ],
        antipatterns=[
            ("Div soup with click handlers", "Using <div onClick={...}> for a button instead of a real <button>, losing keyboard operability and semantics for free."),
            ("Icon-only controls with no label", "Shipping a trash-can icon button with no aria-label, leaving screen reader users with an unnamed 'button' announcement."),
            ("Focus lost on modal open/close", "Opening a modal without moving focus into it, leaving keyboard users stranded on background content."),
            ("Color-only error indication", "Marking an invalid field only with a red border and no text/ARIA association, invisible to screen reader and colorblind users."),
            ("Accessibility as a pre-launch audit only", "Deferring all accessibility checks to a one-time audit right before release instead of continuous automated and manual checks."),
        ],
        verification=[
            "axe-core (or equivalent) reports zero critical/serious violations in CI for new/changed components.",
            "A manual keyboard-only pass can complete every core user flow without a mouse.",
            "A screen reader (VoiceOver/NVDA) announces meaningful names and state for every interactive element in the flow.",
            "Automated contrast checking confirms all text meets WCAG AA thresholds.",
        ],
        references=[
            "WCAG 2.1 Level AA success criteria (W3C).",
            "WAI-ARIA Authoring Practices Guide.",
            "skills/40-frontend/component-and-design-system/SKILL.md",
        ],
    ),
    dict(
        dir="40-frontend", slug="frontend-performance", category="frontend",
        tags=["performance", "core-web-vitals", "bundling"],
        desc="Use when a frontend application's load time or interaction responsiveness needs to be diagnosed and improved against Core Web Vitals targets.",
        purpose=[
            "Slow-loading or janky frontends directly hurt conversion, SEO, and user satisfaction, yet "
            "performance problems are often invisible in local development on fast machines and networks. "
            "This skill covers measuring against Core Web Vitals (LCP, INP, CLS), diagnosing common causes "
            "(oversized bundles, render-blocking resources, layout shifts), and applying targeted fixes.",
            "It emphasizes measuring in production-like conditions before optimizing, since intuition about "
            "what's slow is frequently wrong without real data.",
        ],
        when_use=[
            "Core Web Vitals or user reports indicate slow load or laggy interactions.",
            "A bundle analysis shows unexpectedly large JavaScript payloads.",
            "You are reviewing a new feature that adds significant new dependencies or assets.",
        ],
        when_not=[
            "The application is an internal admin tool with a handful of known users and no measured performance complaints — don't over-invest without evidence of a problem.",
            "You're chasing a micro-optimization with no measurable user impact instead of a proven bottleneck.",
        ],
        prereqs=[
            "A real-user-monitoring (RUM) or synthetic Lighthouse/WebPageTest setup to measure Core Web Vitals.",
            "skills/40-frontend/frontend-architecture/SKILL.md for where code-splitting boundaries naturally fall (feature folders).",
        ],
        workflow=[
            ("Measure current Core Web Vitals in production-like conditions", "Use Lighthouse, WebPageTest, or field RUM data — not just a fast dev machine on localhost."),
            ("Identify the largest contributor to LCP", "Usually the largest above-the-fold image or a render-blocking script/font; profile before guessing."),
            ("Code-split by route and by feature", "Load only the JavaScript needed for the current page; lazy-load rarely used features."),
            ("Optimize images and fonts", "Serve responsive, modern-format images (WebP/AVIF) and use font-display: swap to avoid invisible-text flashes."),
            ("Reserve layout space for async content", "Set explicit width/height or aspect-ratio for images and ads to prevent Cumulative Layout Shift."),
            ("Defer non-critical JavaScript", "Analytics, chat widgets, and other non-essential scripts load after the main content, not blocking it."),
            ("Reduce main-thread work for interaction responsiveness", "Break up long tasks and avoid heavy synchronous computation on user input handlers to improve INP."),
            ("Re-measure after each change", "Confirm each optimization actually moved the metric in production-like conditions before moving to the next one."),
        ],
        decision=[
            ("Bundle analysis shows one large third-party library", "Lazy-load it behind the feature that needs it, or evaluate a lighter alternative."),
            ("LCP element is a hero image", "Preload it with <link rel='preload'> and serve a properly sized, modern-format version."),
            ("CLS spikes when an ad or embed loads", "Reserve its layout space up front with explicit dimensions or a skeleton placeholder."),
            ("INP is poor on a search-as-you-type input", "Debounce the input handler and move heavy filtering off the main thread or into smaller chunks."),
            ("A performance fix has no measurable effect on real metrics", "Revert or deprioritize it; don't keep complexity for a change that didn't help."),
        ],
        code_lang="typescript",
        code_intro="Route-based code splitting to reduce the initial JavaScript payload:",
        code=(
            "import { lazy, Suspense } from 'react';\n"
            "\n"
            "const OrdersPage = lazy(() => import('./features/orders/OrdersPage'));\n"
            "const ReportsPage = lazy(() => import('./features/reports/ReportsPage'));\n"
            "\n"
            "function AppRoutes() {\n"
            "  return (\n"
            "    <Suspense fallback={<PageSkeleton />}>\n"
            "      <Routes>\n"
            "        <Route path=\"/orders\" element={<OrdersPage />} />\n"
            "        <Route path=\"/reports\" element={<ReportsPage />} />\n"
            "      </Routes>\n"
            "    </Suspense>\n"
            "  );\n"
            "}\n"
        ),
        code_notes=[
            "Each route's bundle downloads only when that route is visited, shrinking the initial load for users who only visit one section.",
            "PageSkeleton reserves layout space during the async load, helping avoid a CLS spike when content arrives.",
        ],
        code2_heading="Preloading the LCP image and reserving its layout space (HTML)",
        code2=("html",
            "Reducing LCP time and preventing layout shift for the hero image:",
            "<link rel=\"preload\" as=\"image\" href=\"/hero.webp\" fetchpriority=\"high\">\n"
            "\n"
            "<img\n"
            "  src=\"/hero.webp\"\n"
            "  width=\"1200\"\n"
            "  height=\"600\"\n"
            "  fetchpriority=\"high\"\n"
            "  alt=\"Dashboard overview\"\n"
            "/>\n"
        ),
        checklist=[
            "Core Web Vitals (LCP, INP, CLS) are measured in production-like conditions, not just local dev.",
            "JavaScript is code-split by route/feature so users download only what the current page needs.",
            "Images use modern formats, correct sizing, and explicit width/height to prevent layout shift.",
            "The LCP element (usually a hero image) is preloaded and prioritized.",
            "Non-critical third-party scripts are deferred and don't block the main content.",
            "Each performance change is re-measured to confirm it actually improved the target metric.",
        ],
        antipatterns=[
            ("Optimizing on intuition alone", "Making performance changes without measuring first, potentially fixing a non-bottleneck while ignoring the real one."),
            ("One giant bundle", "Shipping the entire application's JavaScript on every route instead of code-splitting by feature."),
            ("Unsized images causing layout shift", "Omitting width/height on images, causing the page to jump as they load and hurting CLS."),
            ("Blocking scripts before content", "Loading analytics or chat widget scripts synchronously in the <head>, delaying the main content's render."),
            ("Chasing Lighthouse score over real user metrics", "Optimizing purely for a synthetic lab score without confirming it improves real-user (field) Core Web Vitals."),
        ],
        verification=[
            "Lighthouse or field RUM data shows LCP, INP, and CLS within 'Good' thresholds for key pages.",
            "A bundle analyzer report confirms route-level code splitting is producing separate chunks per feature.",
            "No above-the-fold image or embed lacks explicit dimensions, confirmed by a CLS audit.",
            "A before/after measurement accompanies any change made specifically for performance.",
        ],
        references=[
            "web.dev — Core Web Vitals.",
            "skills/40-frontend/frontend-architecture/SKILL.md",
            "Lighthouse and WebPageTest documentation.",
        ],
    ),
]
