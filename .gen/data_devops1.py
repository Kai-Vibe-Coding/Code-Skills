SKILLS = [
    dict(
        dir="60-devops", slug="docker-containerization", category="devops",
        tags=["docker", "containers", "dockerfile"],
        desc="Use when packaging an application into a container image and you need a small, secure, reproducible Dockerfile and image build process.",
        purpose=[
            "Poorly written Dockerfiles produce bloated, slow-to-build images with unnecessary attack surface "
            "and non-reproducible builds. This skill covers multi-stage builds, minimal base images, layer "
            "caching for fast rebuilds, and running containers as a non-root user by default.",
            "It applies to any language but uses .NET 8 as the running example, since that's the primary "
            "backend stack referenced across this skill catalog.",
        ],
        when_use=[
            "You are writing or reviewing a Dockerfile for a new service.",
            "An existing image is unexpectedly large, slow to build, or runs as root.",
            "You need to reduce container build time in CI via better layer caching.",
        ],
        when_not=[
            "The team has standardized on a different packaging model (e.g. serverless zip deployment) with no container runtime involved.",
            "You're debugging a Kubernetes-specific scheduling issue — see skills/60-devops/kubernetes-deployment/SKILL.md instead.",
        ],
        prereqs=[
            "skills/30-backend/dotnet-solution-bootstrap/SKILL.md for the solution structure being containerized.",
            "skills/80-security/dependency-and-supply-chain-security/SKILL.md for base image and dependency scanning practices.",
        ],
        workflow=[
            ("Use multi-stage builds", "Build with the full SDK image in one stage, then copy only the published output into a minimal runtime image."),
            ("Choose a minimal, current base image", "Use an official slim/alpine or distroless-style runtime image over a full OS image to reduce size and attack surface."),
            ("Order Dockerfile instructions for cache efficiency", "Copy dependency manifests (csproj/package.json) and restore before copying full source, so dependency layers are cached across builds."),
            ("Run as a non-root user", "Create and switch to an unprivileged user before the final ENTRYPOINT/CMD, never running the app as root."),
            ("Set explicit resource-relevant environment variables", "Configure ASPNETCORE_URLS, timezone, and culture explicitly rather than relying on image defaults."),
            ("Add a health check instruction", "Define HEALTHCHECK (or rely on the orchestrator's probe) so the container's liveness is observable."),
            ("Pin base image versions explicitly", "Use a specific tag (e.g. 8.0.4-alpine) rather than floating 'latest', so builds are reproducible."),
            ("Scan the final image for vulnerabilities in CI", "Run a container scanner (e.g. Trivy) against the built image before pushing to a registry."),
        ],
        decision=[
            ("Building a .NET 8 web API image", "Use the mcr.microsoft.com/dotnet/sdk image for build stage and mcr.microsoft.com/dotnet/aspnet for the runtime stage."),
            ("Image needs the smallest possible attack surface", "Use an Alpine or distroless variant of the runtime base image, if the app's dependencies support it."),
            ("Build is slow due to full source copy before restore", "Reorder COPY instructions so *.csproj/package.json are copied and restored before the rest of the source."),
            ("Container currently runs as root", "Add a dedicated non-root user (USER appuser) before the final stage's ENTRYPOINT."),
            ("Need to verify no known CVEs ship in the final image", "Add an image vulnerability scan as a required CI step, not just a manual occasional check."),
        ],
        code_lang="dockerfile",
        code_intro="A multi-stage, non-root Dockerfile for a .NET 8 API with cache-efficient layering:",
        code=(
            "FROM mcr.microsoft.com/dotnet/sdk:8.0.4-alpine AS build\n"
            "WORKDIR /src\n"
            "COPY [\"src/OrderPlatform.Api/OrderPlatform.Api.csproj\", \"src/OrderPlatform.Api/\"]\n"
            "COPY [\"src/OrderPlatform.Application/OrderPlatform.Application.csproj\", \"src/OrderPlatform.Application/\"]\n"
            "RUN dotnet restore \"src/OrderPlatform.Api/OrderPlatform.Api.csproj\"\n"
            "COPY . .\n"
            "RUN dotnet publish \"src/OrderPlatform.Api/OrderPlatform.Api.csproj\" -c Release -o /app --no-restore\n"
            "\n"
            "FROM mcr.microsoft.com/dotnet/aspnet:8.0.4-alpine AS runtime\n"
            "RUN addgroup -S appgroup && adduser -S appuser -G appgroup\n"
            "WORKDIR /app\n"
            "COPY --from=build /app .\n"
            "ENV ASPNETCORE_URLS=http://+:8080\n"
            "USER appuser\n"
            "EXPOSE 8080\n"
            "HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost:8080/health || exit 1\n"
            "ENTRYPOINT [\"dotnet\", \"OrderPlatform.Api.dll\"]\n"
        ),
        code_notes=[
            "Copying only .csproj files before `dotnet restore` means source-only changes reuse the cached restore layer, speeding up rebuilds significantly.",
            "USER appuser is set after all root-requiring setup (package installs, user creation) is complete, so the app itself never runs as root.",
        ],
        code2_heading="A .dockerignore file to keep build context small (text)",
        code2=("text",
            "Excluding files that bloat the build context and slow down `docker build`:",
            "bin/\n"
            "obj/\n"
            "**/*.user\n"
            ".git/\n"
            ".vs/\n"
            "**/node_modules/\n"
            "tests/\n"
        ),
        checklist=[
            "The Dockerfile uses multi-stage builds so the final image doesn't contain SDK/build tooling.",
            "Dependency manifests are copied and restored before full source, maximizing layer cache reuse.",
            "The container runs as a non-root user in the final stage.",
            "Base image tags are pinned to a specific version, not 'latest'.",
            "A health check is defined so the container's liveness is observable by the orchestrator.",
            "The built image is scanned for known vulnerabilities in CI before being pushed to a registry.",
        ],
        antipatterns=[
            ("Single-stage build with SDK in production image", "Shipping the full SDK and build tools in the runtime image, bloating size and increasing attack surface."),
            ("Running as root", "Leaving the container's default root user in place for the application process, unnecessarily elevating the blast radius of a container escape."),
            ("Copying all source before restore", "COPY . . followed by restore, invalidating the dependency cache layer on every single source file change."),
            ("Floating 'latest' base image tags", "Using FROM mcr.microsoft.com/dotnet/aspnet:latest, making builds non-reproducible as the base image changes underneath you."),
            ("No image scanning", "Pushing images to a registry with no automated vulnerability scan, shipping known CVEs into production unnoticed."),
        ],
        verification=[
            "`docker build` reuses the dependency-restore layer when only application source (not csproj/package.json) changes.",
            "`docker run` followed by a user check (whoami inside the container) confirms the process runs as a non-root user.",
            "A container vulnerability scan runs in CI and blocks the pipeline on critical/high findings.",
            "The final image size is meaningfully smaller than a single-stage build using the full SDK image.",
        ],
        references=[
            "skills/80-security/dependency-and-supply-chain-security/SKILL.md",
            "skills/60-devops/kubernetes-deployment/SKILL.md",
            "Docker documentation — multi-stage builds and best practices.",
        ],
    ),
    dict(
        dir="60-devops", slug="kubernetes-deployment", category="devops",
        tags=["kubernetes", "deployment", "helm"],
        desc="Use when deploying a containerized service to Kubernetes and you need correct resource requests, health probes, and rollout configuration for reliable operation.",
        purpose=[
            "A Kubernetes Deployment with no resource limits, missing probes, or default rollout settings can "
            "starve the cluster, get killed at the wrong time, or roll out badly during a bad deploy. This "
            "skill covers the essential Deployment/Service manifest configuration — resource requests/limits, "
            "liveness/readiness probes, and rolling update strategy — needed for a service to run reliably.",
            "It treats Helm charts (or Kustomize) as the standard packaging mechanism for reusable, "
            "parameterized manifests across environments.",
        ],
        when_use=[
            "You are deploying a new service to Kubernetes for the first time.",
            "An existing deployment shows OOMKills, failed rollouts, or traffic sent to not-yet-ready pods.",
            "You are configuring autoscaling or multi-environment deployment via Helm values.",
        ],
        when_not=[
            "The workload runs on a simpler platform (e.g. a PaaS or serverless container service) with no direct Kubernetes manifests involved.",
            "You're debugging the container image itself rather than its Kubernetes deployment configuration — see skills/60-devops/docker-containerization/SKILL.md instead.",
        ],
        prereqs=[
            "skills/60-devops/docker-containerization/SKILL.md for the image being deployed, including its health check endpoint.",
            "skills/60-devops/observability/SKILL.md for the metrics/logging the deployment should expose.",
        ],
        workflow=[
            ("Define resource requests and limits", "Set CPU/memory requests based on measured usage, and limits to prevent one pod from starving the node."),
            ("Add liveness and readiness probes", "Liveness restarts a stuck pod; readiness removes a not-yet-ready pod from load balancing without restarting it."),
            ("Configure a safe rolling update strategy", "maxUnavailable and maxSurge tuned so capacity never drops below what's needed during a rollout."),
            ("Externalize configuration via ConfigMaps and Secrets", "Environment-specific values and sensitive values are never baked into the image."),
            ("Package manifests with Helm for reuse across environments", "One chart with environment-specific values.yaml files, not copy-pasted YAML per environment."),
            ("Set PodDisruptionBudgets for critical services", "Ensure voluntary disruptions (node drains, cluster upgrades) don't take down all replicas simultaneously."),
            ("Configure autoscaling based on real metrics", "Use HorizontalPodAutoscaler targeting CPU or custom metrics reflecting actual load, not guesswork."),
            ("Verify rollouts before considering them complete", "Watch rollout status and readiness in CI/CD, automatically rolling back on failure rather than leaving a broken deploy live."),
        ],
        decision=[
            ("A pod's liveness probe is failing due to a slow-starting dependency", "Add a startupProbe with a longer grace period rather than loosening the liveness probe's own timing."),
            ("A rollout must never drop below full capacity", "Set maxUnavailable: 0 and maxSurge: 1 (or higher) so new pods come up before old ones terminate."),
            ("A service handles bursty traffic", "Configure an HPA scaling on CPU or a custom request-rate metric, with sensible min/max replica bounds."),
            ("Multiple replicas exist for high availability", "Add a PodDisruptionBudget ensuring at least N replicas stay available during voluntary disruptions."),
            ("Configuration differs across dev/staging/production", "Use one Helm chart with per-environment values.yaml files, not separate copy-pasted manifest sets."),
        ],
        code_lang="yaml",
        code_intro="A Deployment manifest with resource limits, probes, and a safe rollout strategy:",
        code=(
            "apiVersion: apps/v1\n"
            "kind: Deployment\n"
            "metadata:\n"
            "  name: order-api\n"
            "spec:\n"
            "  replicas: 3\n"
            "  strategy:\n"
            "    type: RollingUpdate\n"
            "    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }\n"
            "  template:\n"
            "    spec:\n"
            "      containers:\n"
            "        - name: order-api\n"
            "          image: registry.example.com/order-api:1.4.2\n"
            "          resources:\n"
            "            requests: { cpu: \"250m\", memory: \"256Mi\" }\n"
            "            limits: { cpu: \"500m\", memory: \"512Mi\" }\n"
            "          readinessProbe:\n"
            "            httpGet: { path: /health/ready, port: 8080 }\n"
            "            initialDelaySeconds: 5\n"
            "          livenessProbe:\n"
            "            httpGet: { path: /health/live, port: 8080 }\n"
            "            initialDelaySeconds: 15\n"
            "            periodSeconds: 20\n"
        ),
        code_notes=[
            "maxUnavailable: 0 with maxSurge: 1 guarantees full capacity is maintained throughout the rollout, at the cost of briefly running one extra pod.",
            "Separate readiness and liveness endpoints let a pod be marked not-ready (e.g. warming a cache) without being killed by the liveness probe.",
        ],
        code2_heading="A PodDisruptionBudget protecting availability during node maintenance (YAML)",
        code2=("yaml",
            "Ensuring at least 2 replicas remain available even during a voluntary cluster disruption:",
            "apiVersion: policy/v1\n"
            "kind: PodDisruptionBudget\n"
            "metadata:\n"
            "  name: order-api-pdb\n"
            "spec:\n"
            "  minAvailable: 2\n"
            "  selector:\n"
            "    matchLabels: { app: order-api }\n"
        ),
        checklist=[
            "Every container has resource requests and limits set based on measured usage.",
            "Liveness and readiness probes are defined separately with appropriate initial delays.",
            "Rolling update strategy guarantees the required minimum capacity throughout a deploy.",
            "Configuration and secrets are externalized via ConfigMaps/Secrets, never baked into the image.",
            "A PodDisruptionBudget protects availability for services with more than one replica.",
            "Manifests are packaged via Helm (or Kustomize) with per-environment values, not duplicated YAML.",
        ],
        antipatterns=[
            ("No resource limits", "Deploying a pod with no memory limit, allowing it to consume node resources unbounded and cause node-wide instability."),
            ("Single combined health endpoint", "Using the same endpoint for both liveness and readiness, causing a slow-warming pod to be killed and restarted in a crash loop instead of just marked not-ready."),
            ("maxUnavailable defaulting to 25%", "Accepting the default rolling update settings without considering whether a capacity dip during rollout is acceptable for this service."),
            ("Secrets baked into the image or plain manifests", "Committing a database password directly into a ConfigMap or Docker image instead of a proper Secret/secret manager."),
            ("Copy-pasted manifests per environment", "Maintaining separate near-duplicate YAML files per environment instead of one parameterized Helm chart."),
        ],
        verification=[
            "A load test confirms the pod is OOMKilled or throttled appropriately only when actually exceeding its set limits, not prematurely.",
            "A rolling deploy under load shows zero dropped requests, confirmed via a synthetic traffic test during rollout.",
            "Draining a node hosting one replica does not take the service below its PodDisruptionBudget's minAvailable.",
            "No Secret value appears in a ConfigMap, Deployment manifest, or image layer, confirmed by a manifest/image scan.",
        ],
        references=[
            "skills/60-devops/docker-containerization/SKILL.md",
            "skills/60-devops/observability/SKILL.md",
            "Kubernetes documentation — Deployments, Probes, and PodDisruptionBudgets.",
        ],
    ),
]
