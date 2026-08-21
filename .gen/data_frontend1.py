SKILLS = [
    dict(
        dir="40-frontend", slug="frontend-architecture", category="frontend",
        tags=["frontend", "architecture", "feature-folders"],
        desc="Use when structuring a frontend application's folders, state boundaries, and module dependencies so it scales past a handful of components.",
        purpose=[
            "Frontend codebases without a deliberate structure tend to accumulate tangled imports between "
            "unrelated features and shared 'god' utility folders that everyone is afraid to touch. This skill "
            "defines a feature-folder architecture with clear module boundaries, a layered approach to shared "
            "code, and rules for where state, API calls, and UI components live.",
            "It applies regardless of framework (React, Angular, Vue) since the core idea — organize by "
            "feature, not by technical layer, and control cross-feature imports — is framework-agnostic.",
        ],
        when_use=[
            "You are starting a new frontend application or a significant new area within one.",
            "The codebase has grown past a few dozen components and imports between features are becoming tangled.",
            "You need to onboard new engineers quickly and the current structure isn't self-explanatory.",
        ],
        when_not=[
            "The application is a small, single-purpose tool with a handful of screens — a flat structure is simpler and sufficient.",
            "You're mid-sprint on a feature; a full restructuring is a separate, deliberate piece of work, not a side effect of a feature change.",
        ],
        prereqs=[
            "skills/40-frontend/frontend-state-and-forms/SKILL.md for how state fits within feature boundaries.",
            "skills/20-architecture/api-design-rest/SKILL.md (or GraphQL equivalent) for how features consume backend APIs.",
        ],
        workflow=[
            ("Organize top-level folders by feature, not by type", "features/orders, features/customers — not components/, hooks/, services/ folders spanning all features."),
            ("Keep a feature's UI, state, and API calls colocated", "Everything needed to understand feature/orders lives inside that folder, minimizing cross-folder hunting."),
            ("Expose a small public surface per feature", "Each feature folder has an index (barrel) file exporting only what other features are allowed to use."),
            ("Put truly cross-cutting code in a shared/ layer", "Design system components, generic hooks, and API client setup that many features need live in shared/, not duplicated per feature."),
            ("Forbid deep imports across feature boundaries", "Other features import only via a feature's public index, never reaching into its internal files directly."),
            ("Keep routing as a thin composition layer", "The app shell/router composes features together; it shouldn't contain business logic itself."),
            ("Enforce boundaries with lint rules", "Use an ESLint import-boundary plugin to fail CI if a feature imports another feature's internals."),
        ],
        decision=[
            ("Two features need to share a UI component", "Promote it to the shared/ design-system layer, not duplicate it or import across feature boundaries."),
            ("A feature is growing very large with many sub-areas", "Split it into sub-features with their own folders and public index files, keeping the pattern recursive."),
            ("State is needed by many unrelated features", "Consider whether it truly is cross-cutting (e.g. current user) and belongs in a shared/app-level store, or whether features are too tightly coupled."),
            ("A small app has only 3-4 screens", "A lighter, flatter structure is fine; don't over-engineer feature folders for trivial scope."),
            ("Import boundary violations keep slipping through review", "Add an automated ESLint boundary rule rather than relying on manual review vigilance."),
        ],
        code_lang="text",
        code_intro="A feature-folder layout with enforced public surfaces:",
        code=(
            "src/\n"
            "  app/                  # routing, app shell, composition root\n"
            "  shared/\n"
            "    ui/                 # design-system components\n"
            "    api/                # base HTTP client, auth interceptor\n"
            "    hooks/              # generic, feature-agnostic hooks\n"
            "  features/\n"
            "    orders/\n"
            "      components/       # OrderList, OrderDetail (internal)\n"
            "      api/              # ordersApi.ts (internal)\n"
            "      state/            # ordersSlice.ts (internal)\n"
            "      index.ts          # public surface: exports OrdersPage only\n"
            "    customers/\n"
            "      components/\n"
            "      api/\n"
            "      state/\n"
            "      index.ts\n"
            "\n"
            "// features/orders/index.ts\n"
            "export { OrdersPage } from './components/OrdersPage';\n"
            "// Nothing else from orders/ is importable from outside this folder.\n"
        ),
        code_notes=[
            "Only OrdersPage is exported; components/OrderList.tsx cannot be imported directly from customers/.",
            "This mirrors a module boundary similar to a bounded context (skills/20-architecture/domain-driven-design/SKILL.md) at the frontend layer.",
        ],
        code2_heading="ESLint rule enforcing feature import boundaries (TypeScript config)",
        code2=("typescript",
            "Failing the build if a feature reaches into another feature's internals:",
            "// .eslintrc.cjs\n"
            "module.exports = {\n"
            "  rules: {\n"
            "    'import/no-restricted-paths': ['error', {\n"
            "      zones: [{\n"
            "        target: './src/features/*/!(index.ts)',\n"
            "        from: './src/features/*',\n"
            "        except: ['./index.ts'],\n"
            "        message: 'Import only a feature\\'s public index, not its internals.'\n"
            "      }]\n"
            "    }]\n"
            "  }\n"
            "};\n"
        ),
        checklist=[
            "Top-level folders are organized by feature, not by technical type.",
            "Each feature exposes a small public surface via an index file; internals are never imported directly by other features.",
            "Truly cross-cutting UI/hooks/API code lives in a shared/ layer, not duplicated across features.",
            "The app/routing layer composes features but contains no business logic itself.",
            "An automated lint rule enforces import boundaries between features.",
            "New engineers can find everything relevant to a feature inside one folder.",
        ],
        antipatterns=[
            ("Organize-by-type folders", "components/, hooks/, services/ folders spanning every feature, forcing you to hunt across three folders to understand one feature."),
            ("Deep cross-feature imports", "import { OrderRow } from '../orders/components/OrderRow' from inside the customers feature, creating hidden coupling."),
            ("Shared folder as a dumping ground", "Putting feature-specific logic into shared/ because it's convenient, turning it into an unmaintainable catch-all."),
            ("Business logic in the router", "Embedding data-fetching and business rules directly in route definitions instead of within feature modules."),
            ("No enforced boundaries", "Relying purely on code review discipline to prevent boundary violations, which erodes over time without lint automation."),
        ],
        verification=[
            "An ESLint boundary check fails CI when a feature imports another feature's internal file.",
            "A new engineer can implement a small change to one feature by only reading files inside that feature's folder.",
            "No feature-specific component or hook exists inside the shared/ folder.",
            "Removing a feature folder entirely does not break any other feature (verified by a dependency check or trial removal).",
        ],
        references=[
            "skills/40-frontend/frontend-state-and-forms/SKILL.md",
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "Bulletproof React — feature-folder architecture guidance.",
        ],
    ),
    dict(
        dir="40-frontend", slug="component-and-design-system", category="frontend",
        tags=["design-system", "components", "storybook"],
        desc="Use when building or consuming a shared component library and you need consistent, reusable, well-documented UI building blocks across an application or organization.",
        purpose=[
            "Without a shared design system, every team reinvents buttons, inputs, and layout primitives "
            "slightly differently, producing visual and behavioral inconsistency and duplicated accessibility "
            "bugs. This skill covers structuring a component library with clear composition patterns, "
            "documented variants, and a workflow (Storybook) for developing and reviewing components in "
            "isolation.",
            "It also addresses the boundary between 'dumb' presentational components and feature-specific "
            "components that consume them, so the design system stays generic and reusable.",
        ],
        when_use=[
            "You are building a new shared UI component intended for reuse across features or teams.",
            "Visual or behavioral inconsistency is appearing across similar UI elements in different parts of the app.",
            "You need a workflow to develop and visually review components independent of a full app build.",
        ],
        when_not=[
            "The component is genuinely one-off and specific to a single feature screen with no reuse potential.",
            "The organization already has an adopted third-party design system that fully covers the need — extend it rather than building a parallel one.",
        ],
        prereqs=[
            "skills/40-frontend/accessibility-wcag/SKILL.md, since every shared component must meet baseline accessibility requirements.",
            "skills/40-frontend/frontend-architecture/SKILL.md for where shared components live (shared/ui/).",
        ],
        workflow=[
            ("Identify genuinely reusable UI patterns", "Extract a component into the design system only after it (or something very similar) is needed in 2+ places."),
            ("Design components as composable primitives", "Prefer small composable pieces (Button, Stack, Card) over large monolithic components with many boolean props."),
            ("Define variants via a constrained prop API", "Use a fixed set of variant values (e.g. variant='primary' | 'secondary' | 'danger') rather than open-ended style props."),
            ("Document each component in Storybook", "Every variant and state (loading, disabled, error) gets its own story for visual review and manual QA."),
            ("Bake accessibility in by default", "Correct semantic HTML, ARIA attributes, and keyboard behavior are the component's responsibility, not each consumer's."),
            ("Version and changelog the design system", "Treat it as a versioned package; breaking changes to shared components go through a deliberate migration path."),
            ("Test components in isolation", "Unit/interaction tests run against the component alone, not requiring a full feature page to render it."),
        ],
        decision=[
            ("A UI pattern is used in exactly one feature so far", "Keep it local to that feature; don't prematurely generalize into the design system."),
            ("A UI pattern is needed in a second, unrelated feature", "Extract it into shared/ui with a documented, constrained prop API."),
            ("A component needs many visual variations", "Use a small, fixed variant enum plus composition, not an ever-growing list of boolean flags."),
            ("A component's behavior differs subtly per consuming team", "Support it via slots/children composition rather than an escape-hatch style override prop that undermines consistency."),
            ("A breaking change is needed to a widely used component", "Version it and provide a migration guide/codemod rather than changing behavior silently under consumers' feet."),
        ],
        code_lang="typescript",
        code_intro="A composable, accessible Button primitive with a constrained variant API:",
        code=(
            "type ButtonVariant = 'primary' | 'secondary' | 'danger';\n"
            "\n"
            "interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {\n"
            "  variant?: ButtonVariant;\n"
            "  isLoading?: boolean;\n"
            "}\n"
            "\n"
            "export function Button({\n"
            "  variant = 'primary',\n"
            "  isLoading = false,\n"
            "  disabled,\n"
            "  children,\n"
            "  ...rest\n"
            "}: ButtonProps) {\n"
            "  return (\n"
            "    <button\n"
            "      className={`btn btn--${variant}`}\n"
            "      disabled={disabled || isLoading}\n"
            "      aria-busy={isLoading}\n"
            "      {...rest}\n"
            "    >\n"
            "      {isLoading ? <Spinner aria-hidden=\"true\" /> : children}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
        ),
        code_notes=[
            "aria-busy communicates loading state to assistive technology, not just visually via the spinner.",
            "The variant prop is a closed union type, preventing arbitrary ad hoc style strings from being passed in.",
        ],
        code2_heading="A Storybook story documenting every Button state (TypeScript)",
        code2=("typescript",
            "Enabling visual review and manual QA of every variant and state in isolation:",
            "const meta: Meta<typeof Button> = { component: Button, title: 'Design System/Button' };\n"
            "export default meta;\n"
            "\n"
            "export const Primary: StoryObj<typeof Button> = { args: { variant: 'primary', children: 'Save' } };\n"
            "export const Danger: StoryObj<typeof Button> = { args: { variant: 'danger', children: 'Delete' } };\n"
            "export const Loading: StoryObj<typeof Button> = { args: { isLoading: true, children: 'Saving...' } };\n"
        ),
        checklist=[
            "A component is promoted to the design system only after being needed in two or more places.",
            "Component variant APIs are closed/constrained, not open-ended style props.",
            "Every component's variants and states are documented as Storybook stories.",
            "Accessibility (semantics, ARIA, keyboard) is built into the component, not left to consumers.",
            "Breaking changes to shared components go through versioning and a migration path.",
            "Components are tested in isolation, without requiring a full page render.",
        ],
        antipatterns=[
            ("Premature abstraction", "Building a 'flexible' shared component for a UI pattern used in only one place, guessing at future needs."),
            ("Prop explosion", "A Button component with a dozen boolean props (isRounded, isWide, isCompact...) instead of a small, composable variant system."),
            ("Style override escape hatches", "Allowing arbitrary className/style overrides that let every consumer bypass the design system's consistency."),
            ("Accessibility left to consumers", "Shipping a shared component with no ARIA attributes or keyboard support, expecting each consuming team to patch it individually."),
            ("Silent breaking changes", "Changing a shared component's behavior in place without versioning, breaking every consumer without warning."),
        ],
        verification=[
            "Every shared component has Storybook stories covering its documented variants and states.",
            "An automated accessibility check (e.g. axe) passes for each component's stories.",
            "No shared component accepts an arbitrary style/className override that bypasses its variant system.",
            "A breaking change to a shared component is accompanied by a version bump and migration notes.",
        ],
        references=[
            "skills/40-frontend/accessibility-wcag/SKILL.md",
            "skills/40-frontend/frontend-architecture/SKILL.md",
            "Storybook documentation.",
        ],
    ),
]
