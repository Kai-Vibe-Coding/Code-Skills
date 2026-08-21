SKILLS = [
    dict(
        dir="60-devops", slug="ci-cd-pipelines", category="devops",
        tags=["ci-cd", "pipelines", "automation"],
        desc="Use when designing or reviewing a build/test/deploy pipeline to ensure fast feedback, reliable gates, and safe automated deployment.",
        purpose=[
            "A slow or unreliable CI/CD pipeline erodes trust in automation and encourages engineers to skip "
            "or ignore its results. This skill covers structuring pipelines into fast, parallelized stages "
            "with clear quality gates (build, test, scan, deploy), and progressive deployment automation that "
            "reduces the risk of any single change.",
            "It emphasizes making the pipeline itself a first-class piece of engineering, versioned and "
            "reviewed like any other code, not an afterthought bolted on once a project already exists.",
        ],
        when_use=[
            "You are setting up CI/CD for a new service or repository.",
            "An existing pipeline is slow, flaky, or missing key quality gates (tests, security scans).",
            "You are moving from manual deployment to automated, gated deployment.",
        ],
        when_not=[
            "The project is an experimental prototype not headed to production — a full pipeline may be premature.",
            "You're debugging one specific flaky test rather than the pipeline's overall structure — fix that test directly first.",
        ],
        prereqs=[
            "skills/70-quality/test-strategy/SKILL.md for what tests should run at which pipeline stage.",
            "skills/80-security/sast-dast-and-security-in-ci/SKILL.md for the security scanning gates to include.",
            "skills/60-devops/release-strategies/SKILL.md for how the pipeline's deploy stage should behave.",
        ],
        workflow=[
            ("Trigger CI on every push and pull request", "Fast feedback on every change, not just on merge to main."),
            ("Run fast checks first, in parallel where possible", "Lint, unit tests, and build run in parallel jobs before slower integration/E2E tests."),
            ("Fail fast on the cheapest checks", "Static analysis and unit tests should fail the pipeline in seconds/minutes, before expensive integration tests even start."),
            ("Cache dependencies between runs", "Cache package manager downloads (NuGet, npm) keyed by lockfile hash to avoid re-downloading on every run."),
            ("Build once, deploy the same artifact everywhere", "Produce one versioned build artifact/image and promote it through environments, never rebuilding per environment."),
            ("Gate deployment on required checks", "Merges to main and deploys are blocked unless build, tests, and security scans all pass."),
            ("Automate progressive deployment", "Deploy to staging automatically, then to production via a controlled strategy (canary/blue-green) per skills/60-devops/release-strategies/SKILL.md."),
            ("Version and review pipeline configuration like code", "Pipeline YAML changes go through the same PR review as application code."),
        ],
        decision=[
            ("A test suite is slow and blocking fast feedback", "Split into fast unit tests (run on every push) and slower integration/E2E tests (run on PR or a separate stage), not one monolithic suite."),
            ("Different environments need different configuration", "Inject environment-specific config at deploy time into one built artifact, rather than rebuilding per environment."),
            ("A security scan finding blocks a release", "Fail the pipeline for critical/high findings per skills/80-security/sast-dast-and-security-in-ci/SKILL.md policy, don't silently ignore it."),
            ("Deployment to production needs to be safer", "Add a canary or blue-green stage with automated rollback triggers rather than a single big-bang deploy."),
            ("Pipeline runs are flaky and inconsistent", "Treat flaky tests/steps as a bug to fix immediately, not something to retry indefinitely and ignore."),
        ],
        code_lang="yaml",
        code_intro="A staged GitHub Actions pipeline with parallel fast checks and a gated deploy:",
        code=(
            "name: CI\n"
            "on: [push, pull_request]\n"
            "jobs:\n"
            "  lint-and-test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-dotnet@v4\n"
            "        with: { dotnet-version: '8.0.x' }\n"
            "      - run: dotnet format --verify-no-changes\n"
            "      - run: dotnet test --logger trx --results-directory TestResults\n"
            "\n"
            "  security-scan:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - run: trivy fs --exit-code 1 --severity CRITICAL,HIGH .\n"
            "\n"
            "  deploy-staging:\n"
            "    needs: [lint-and-test, security-scan]\n"
            "    if: github.ref == 'refs/heads/main'\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: ./scripts/deploy.sh staging ${{ github.sha }}\n"
        ),
        code_notes=[
            "deploy-staging only runs after both lint-and-test and security-scan succeed, and only on main, keeping the deploy gate explicit.",
            "The same commit SHA is used as the deploy artifact version, ensuring what's tested is exactly what's deployed.",
        ],
        code2_heading="Caching dependencies keyed by lockfile hash (YAML)",
        code2=("yaml",
            "Avoiding redundant downloads on every pipeline run:",
            "- uses: actions/cache@v4\n"
            "  with:\n"
            "    path: ~/.nuget/packages\n"
            "    key: nuget-${{ hashFiles('**/packages.lock.json') }}\n"
            "    restore-keys: nuget-\n"
        ),
        checklist=[
            "CI triggers on every push and pull request, not only on merge to main.",
            "Fast checks (lint, unit tests) run before and gate slower integration/E2E tests.",
            "Dependencies are cached between runs, keyed by a lockfile hash.",
            "One versioned build artifact is promoted through environments rather than rebuilt per environment.",
            "Merges and deploys are blocked unless all required checks (build, test, security scan) pass.",
            "Pipeline configuration changes go through code review like any other change.",
        ],
        antipatterns=[
            ("Monolithic slow pipeline", "Running every test (unit, integration, E2E) sequentially in one long job, delaying feedback on simple mistakes by tens of minutes."),
            ("Rebuild per environment", "Building a separate artifact for staging and production instead of promoting one tested artifact, risking untested differences between them."),
            ("Optional security scans", "Running a SAST/dependency scan but not failing the build on critical findings, making the scan purely informational and easy to ignore."),
            ("Manual, undocumented deploy steps", "Relying on an engineer running commands from memory to deploy instead of a scripted, versioned pipeline step."),
            ("Ignoring flaky tests", "Retrying a known-flaky test indefinitely instead of fixing or quarantining it, eroding trust in the whole pipeline's signal."),
        ],
        verification=[
            "A trivial one-line change reaches a pass/fail CI result within a target time budget (e.g. under 10 minutes for fast checks).",
            "The exact artifact deployed to production is confirmed to be the same one that passed staging tests (by version/SHA).",
            "A critical security finding is confirmed to block the pipeline in a test run.",
            "Pipeline YAML changes are visible in PR history with the same review requirements as application code.",
        ],
        references=[
            "skills/70-quality/test-strategy/SKILL.md",
            "skills/80-security/sast-dast-and-security-in-ci/SKILL.md",
            "skills/60-devops/release-strategies/SKILL.md",
        ],
    ),
    dict(
        dir="60-devops", slug="infrastructure-as-code", category="devops",
        tags=["iac", "terraform", "infrastructure"],
        desc="Use when provisioning or modifying cloud infrastructure and you need it defined declaratively, version-controlled, and reviewed like application code.",
        purpose=[
            "Manually clicking through a cloud console to provision infrastructure is unrepeatable, "
            "undocumented, and impossible to review. This skill establishes Infrastructure as Code (IaC) "
            "using a declarative tool (Terraform, as the running example) with modules, remote state, and a "
            "plan-review-apply workflow that treats infrastructure changes with the same rigor as application "
            "code changes.",
            "It also covers structuring state and modules so environments (dev/staging/production) stay "
            "consistent while allowing controlled per-environment variation.",
        ],
        when_use=[
            "You are provisioning new cloud infrastructure (compute, networking, databases, queues).",
            "Existing infrastructure was created manually and needs to be brought under version control.",
            "You need consistent, repeatable environments across dev/staging/production.",
        ],
        when_not=[
            "You are making a one-off, throwaway sandbox resource for a few hours of manual experimentation with no lasting need.",
            "The change is purely application configuration (env vars, feature flags) already covered by skills/30-backend/configuration-and-feature-flags/SKILL.md.",
        ],
        prereqs=[
            "skills/80-security/secrets-and-key-management/SKILL.md for how credentials used by IaC tooling are stored and rotated.",
            "A remote state backend (e.g. cloud storage bucket with locking) already provisioned or planned.",
        ],
        workflow=[
            ("Define infrastructure declaratively in version control", "All resources described in Terraform (or equivalent) files, committed and reviewed like code."),
            ("Use remote state with locking", "Store state in a shared backend (e.g. S3 + DynamoDB lock table) so concurrent applies don't corrupt state."),
            ("Structure reusable modules per resource type", "A module for 'a standard web service' or 'a standard database' encapsulates best-practice defaults, reused across services."),
            ("Parameterize per-environment differences", "Use variables/workspaces for the handful of things that legitimately differ between dev/staging/production (size, replica count), not the whole structure."),
            ("Run plan before every apply", "Review the diff a change would make to real infrastructure before applying it, in CI and locally."),
            ("Require review and approval for apply, especially in production", "Treat `terraform apply` against production as a gated, reviewed action, not an unattended step run by anyone at any time."),
            ("Avoid manual console changes ('ClickOps')", "Any manual change made outside IaC causes drift; if it must happen in an emergency, import it back into code immediately after."),
            ("Tag and document every resource's ownership", "Every resource carries owner/team/environment tags for cost attribution and operational clarity."),
        ],
        decision=[
            ("A new microservice needs standard supporting infrastructure", "Use an existing shared module (e.g. 'web-service') rather than writing bespoke Terraform for each new service."),
            ("An environment needs a smaller/cheaper instance size than production", "Parameterize instance size/count via variables, keeping the same module structure across environments."),
            ("Infrastructure state shows drift from a manual console change", "Import the manual change into Terraform state immediately, or revert it, rather than leaving code and reality out of sync."),
            ("A production change is high-risk (e.g. deleting a resource)", "Require an explicit manual approval gate on `terraform apply` for production, even if lower environments auto-apply."),
            ("Multiple teams manage related infrastructure", "Split state by logical boundary (e.g. per service or per environment) to limit blast radius, rather than one giant shared state file."),
        ],
        code_lang="hcl",
        code_intro="A reusable Terraform module for a standard web service, parameterized per environment:",
        code=(
            "# modules/web-service/main.tf\n"
            "variable \"environment\" { type = string }\n"
            "variable \"instance_count\" {\n"
            "  type    = number\n"
            "  default = 2\n"
            "}\n"
            "variable \"instance_size\" {\n"
            "  type    = string\n"
            "  default = \"small\"\n"
            "}\n"
            "\n"
            "resource \"cloud_app_service\" \"this\" {\n"
            "  name          = \"order-api-${var.environment}\"\n"
            "  instance_count = var.instance_count\n"
            "  instance_size  = var.instance_size\n"
            "  tags = { team = \"orders\", environment = var.environment, managed_by = \"terraform\" }\n"
            "}\n"
            "\n"
            "# environments/production/main.tf\n"
            "module \"order_api\" {\n"
            "  source          = \"../../modules/web-service\"\n"
            "  environment     = \"production\"\n"
            "  instance_count  = 4\n"
            "  instance_size   = \"large\"\n"
            "}\n"
        ),
        code_notes=[
            "The same module is reused for dev/staging/production; only instance_count and instance_size differ per environment.",
            "Consistent tagging (team, environment, managed_by) supports cost attribution and quickly identifying non-IaC-managed resources.",
        ],
        code2_heading="Remote state configuration with locking (HCL)",
        code2=("hcl",
            "Preventing concurrent applies from corrupting shared state:",
            "terraform {\n"
            "  backend \"s3\" {\n"
            "    bucket         = \"acme-terraform-state\"\n"
            "    key            = \"orders/production/terraform.tfstate\"\n"
            "    region         = \"us-east-1\"\n"
            "    dynamodb_table = \"terraform-locks\"\n"
            "    encrypt        = true\n"
            "  }\n"
            "}\n"
        ),
        checklist=[
            "All infrastructure is defined declaratively in version-controlled IaC files, not created manually.",
            "Remote state with locking prevents concurrent applies from corrupting state.",
            "Reusable modules encapsulate best-practice defaults for common resource types.",
            "Per-environment differences are parameterized via variables, not duplicated module structures.",
            "`terraform plan` is reviewed before every apply, especially for production.",
            "Every resource is tagged with owning team and environment for cost and operational clarity.",
        ],
        antipatterns=[
            ("ClickOps", "Making manual changes in the cloud console 'just this once', causing drift between actual infrastructure and the IaC definition."),
            ("One giant state file for everything", "Storing all environments and services in a single Terraform state, maximizing blast radius for any mistake or lock contention."),
            ("Unreviewed production applies", "Allowing `terraform apply` against production to run unattended with no plan review or approval gate."),
            ("Copy-pasted per-environment Terraform", "Duplicating near-identical Terraform files per environment instead of one parameterized module, causing them to drift apart over time."),
            ("No resource tagging", "Provisioning resources with no owner/team/environment tags, making cost attribution and cleanup of orphaned resources difficult."),
        ],
        verification=[
            "A `terraform plan` run against production shows zero unexpected diff (no undetected drift) before a scheduled change.",
            "Attempting a concurrent `terraform apply` from two locations is blocked by the state lock, confirmed by a test.",
            "Every environment's infrastructure is provisioned from the same shared module, confirmed by reviewing the environment-specific configuration files.",
            "A resource created outside Terraform is detected via drift and imported or removed within an agreed time window.",
        ],
        references=[
            "skills/80-security/secrets-and-key-management/SKILL.md",
            "skills/60-devops/cost-and-resource-optimization/SKILL.md",
            "HashiCorp Terraform documentation.",
        ],
    ),
]
