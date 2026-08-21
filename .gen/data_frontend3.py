SKILLS = [
    dict(
        dir="40-frontend", slug="frontend-state-and-forms", category="frontend",
        tags=["state-management", "forms", "validation"],
        desc="Use when deciding where application state should live and how to build robust, validated forms without over-centralizing simple local UI state.",
        purpose=[
            "Overusing a global state library for every piece of UI state creates unnecessary coupling and "
            "re-renders, while under-using shared state causes prop-drilling and duplicated server-data "
            "fetching. This skill establishes a decision framework for local vs shared vs server state, and "
            "a validated-forms pattern that keeps validation logic close to the schema, not scattered across "
            "handlers.",
            "It distinguishes server state (data fetched from an API, with caching/staleness concerns) from "
            "client state (UI-only concerns like 'is this dropdown open'), since they need fundamentally "
            "different tools.",
        ],
        when_use=[
            "You are deciding whether new state belongs in local component state, a shared store, or a server-state cache.",
            "You are building a form with more than a couple of fields requiring validation.",
            "Prop-drilling or unnecessary re-renders are appearing due to state placed too high or too low.",
        ],
        when_not=[
            "A single component's transient UI state (e.g. hover state) — always keep this local, never lift it to global state.",
            "You're deep-diving one field's validation edge case; the broader state architecture doesn't need revisiting for that.",
        ],
        prereqs=[
            "skills/40-frontend/frontend-architecture/SKILL.md for where feature-level state lives.",
            "skills/20-architecture/api-design-rest/SKILL.md (or GraphQL) for the API shape server state is fetched from.",
        ],
        workflow=[
            ("Classify each piece of state before choosing a tool", "Server state (fetched data), shared UI state (cross-feature), or local UI state (single component)."),
            ("Use a server-state library for anything fetched from an API", "React Query/TanStack Query or SWR for caching, refetching, and staleness — not manual useEffect fetch-and-setState."),
            ("Keep local UI state local", "Dropdown open/closed, input focus, hover — useState inside the component, never lifted to a global store."),
            ("Reserve global/shared state for truly cross-cutting concerns", "Current user, theme, feature flags — not feature-specific data better modeled as server state."),
            ("Define form schemas with a validation library", "Use Zod (or similar) to define the shape and validation rules once, shared between client-side checks and type inference."),
            ("Wire schema validation into the form library", "Connect the schema to React Hook Form (or equivalent) so validation runs consistently on blur/submit."),
            ("Surface validation errors accessibly", "Follow skills/40-frontend/accessibility-wcag/SKILL.md's error-association pattern for every invalid field."),
            ("Handle async submission state explicitly", "Track and surface loading/success/error state for form submission, disabling the submit button during in-flight requests."),
        ],
        decision=[
            ("Data comes from a backend API and can go stale", "Use a server-state library (React Query/SWR), never manual useState + useEffect fetching."),
            ("State is only relevant to one component instance", "Keep it as local useState; don't lift it to context or a global store."),
            ("State must be shared across unrelated features (e.g. logged-in user)", "Use a lightweight global store or context provider, scoped narrowly to that concern."),
            ("A form has complex cross-field validation (e.g. date range)", "Express it in the Zod schema's refine/superRefine, not ad hoc handler logic."),
            ("A form is trivial (one search box)", "A single useState with inline validation is fine; a full schema library is unnecessary ceremony."),
        ],
        code_lang="typescript",
        code_intro="Server-state fetching with caching via React Query, versus local UI state:",
        code=(
            "function OrdersPage() {\n"
            "  // Server state: cached, revalidated, deduplicated across the app\n"
            "  const { data: orders, isLoading, error } = useQuery({\n"
            "    queryKey: ['orders'],\n"
            "    queryFn: () => fetchOrders(),\n"
            "    staleTime: 30_000,\n"
            "  });\n"
            "\n"
            "  // Local UI state: irrelevant outside this component, never global\n"
            "  const [isFilterOpen, setIsFilterOpen] = useState(false);\n"
            "\n"
            "  if (isLoading) return <Spinner />;\n"
            "  if (error) return <ErrorBanner message=\"Could not load orders\" />;\n"
            "  return (\n"
            "    <>\n"
            "      <button onClick={() => setIsFilterOpen(o => !o)}>Filters</button>\n"
            "      {isFilterOpen && <OrderFilters />}\n"
            "      <OrderList orders={orders ?? []} />\n"
            "    </>\n"
            "  );\n"
            "}\n"
        ),
        code_notes=[
            "staleTime avoids redundant refetches while keeping data reasonably fresh, tuned per data volatility.",
            "isFilterOpen never needs to live outside this component, so it stays as simple local state.",
        ],
        code2_heading="A schema-validated form with accessible error surfacing (Zod + React Hook Form, TypeScript)",
        code2=("typescript",
            "One schema drives both validation and type inference, wired into the form library:",
            "const checkoutSchema = z.object({\n"
            "  email: z.string().email('Enter a valid email address'),\n"
            "  quantity: z.number().int().min(1, 'Quantity must be at least 1'),\n"
            "});\n"
            "type CheckoutForm = z.infer<typeof checkoutSchema>;\n"
            "\n"
            "function CheckoutForm() {\n"
            "  const { register, handleSubmit, formState: { errors, isSubmitting } } =\n"
            "    useForm<CheckoutForm>({ resolver: zodResolver(checkoutSchema) });\n"
            "\n"
            "  return (\n"
            "    <form onSubmit={handleSubmit(submitOrder)}>\n"
            "      <label htmlFor=\"email\">Email</label>\n"
            "      <input id=\"email\" {...register('email')} aria-describedby=\"email-error\" />\n"
            "      {errors.email && <p id=\"email-error\" role=\"alert\">{errors.email.message}</p>}\n"
            "      <button type=\"submit\" disabled={isSubmitting}>Place order</button>\n"
            "    </form>\n"
            "  );\n"
            "}\n"
        ),
        checklist=[
            "State is explicitly classified as server, shared, or local before choosing a management approach.",
            "Data fetched from an API uses a server-state library with caching, not manual useEffect + setState.",
            "Local, single-component UI state stays local and is never lifted to global state unnecessarily.",
            "Form validation is defined once in a schema, shared between client checks and type inference.",
            "Validation errors are surfaced accessibly, associated with their field and announced to assistive technology.",
            "Form submission tracks and disables during in-flight state, preventing duplicate submits.",
        ],
        antipatterns=[
            ("Global store for everything", "Putting every piece of state, including transient UI toggles, into a global store, causing unnecessary re-renders and coupling."),
            ("Manual fetch-and-setState for server data", "Reimplementing caching, deduplication, and revalidation by hand with useEffect instead of a server-state library."),
            ("Validation logic scattered in handlers", "Writing ad hoc if-checks across multiple submit handlers instead of one shared schema."),
            ("Prop drilling instead of appropriate scoping", "Passing state through five layers of components instead of placing it at the right level (local, feature context, or server cache)."),
            ("No submission-in-flight handling", "Leaving the submit button enabled during an async request, allowing duplicate submissions."),
        ],
        verification=[
            "A code review confirms no manual useEffect-based data fetching duplicates what a server-state library already handles.",
            "Every form's validation rules exist in one schema location, not duplicated across handlers.",
            "Rapidly clicking submit does not produce duplicate network requests, verified by a test or network trace.",
            "Local UI-only state (e.g. dropdown open) is never found in the global store during code review.",
        ],
        references=[
            "skills/40-frontend/frontend-architecture/SKILL.md",
            "skills/40-frontend/accessibility-wcag/SKILL.md",
            "TanStack Query and Zod documentation.",
        ],
    ),
]
