---
name: docker-containerization
description: Use when packaging an application into a container image and you need a small, secure, reproducible Dockerfile and image build process.
category: devops
tags: [docker, containers, dockerfile]
maturity: stable
updated: 2026-08-21
---

## Purpose

Poorly written Dockerfiles produce bloated, slow-to-build images with unnecessary attack surface and non-reproducible builds. This skill covers multi-stage builds, minimal base images, layer caching for fast rebuilds, and running containers as a non-root user by default.

It applies to any language but uses .NET 8 as the running example, since that's the primary backend stack referenced across this skill catalog.

## When to use / When NOT to use

**Use this skill when:**

- You are writing or reviewing a Dockerfile for a new service.
- An existing image is unexpectedly large, slow to build, or runs as root.
- You need to reduce container build time in CI via better layer caching.

**Do NOT use this skill when:**

- The team has standardized on a different packaging model (e.g. serverless zip deployment) with no container runtime involved.
- You're debugging a Kubernetes-specific scheduling issue — see skills/60-devops/kubernetes-deployment/SKILL.md instead.

## Prerequisites

- skills/30-backend/dotnet-solution-bootstrap/SKILL.md for the solution structure being containerized.
- skills/80-security/dependency-and-supply-chain-security/SKILL.md for base image and dependency scanning practices.

## Workflow

1. **Use multi-stage builds** - Build with the full SDK image in one stage, then copy only the published output into a minimal runtime image.
2. **Choose a minimal, current base image** - Use an official slim/alpine or distroless-style runtime image over a full OS image to reduce size and attack surface.
3. **Order Dockerfile instructions for cache efficiency** - Copy dependency manifests (csproj/package.json) and restore before copying full source, so dependency layers are cached across builds.
4. **Run as a non-root user** - Create and switch to an unprivileged user before the final ENTRYPOINT/CMD, never running the app as root.
5. **Set explicit resource-relevant environment variables** - Configure ASPNETCORE_URLS, timezone, and culture explicitly rather than relying on image defaults.
6. **Add a health check instruction** - Define HEALTHCHECK (or rely on the orchestrator's probe) so the container's liveness is observable.
7. **Pin base image versions explicitly** - Use a specific tag (e.g. 8.0.4-alpine) rather than floating 'latest', so builds are reproducible.
8. **Scan the final image for vulnerabilities in CI** - Run a container scanner (e.g. Trivy) against the built image before pushing to a registry.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Building a .NET 8 web API image | Use the mcr.microsoft.com/dotnet/sdk image for build stage and mcr.microsoft.com/dotnet/aspnet for the runtime stage. |
| Image needs the smallest possible attack surface | Use an Alpine or distroless variant of the runtime base image, if the app's dependencies support it. |
| Build is slow due to full source copy before restore | Reorder COPY instructions so *.csproj/package.json are copied and restored before the rest of the source. |
| Container currently runs as root | Add a dedicated non-root user (USER appuser) before the final stage's ENTRYPOINT. |
| Need to verify no known CVEs ship in the final image | Add an image vulnerability scan as a required CI step, not just a manual occasional check. |

## Reference implementation

A multi-stage, non-root Dockerfile for a .NET 8 API with cache-efficient layering:

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0.4-alpine AS build
WORKDIR /src
COPY ["src/OrderPlatform.Api/OrderPlatform.Api.csproj", "src/OrderPlatform.Api/"]
COPY ["src/OrderPlatform.Application/OrderPlatform.Application.csproj", "src/OrderPlatform.Application/"]
RUN dotnet restore "src/OrderPlatform.Api/OrderPlatform.Api.csproj"
COPY . .
RUN dotnet publish "src/OrderPlatform.Api/OrderPlatform.Api.csproj" -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0.4-alpine AS runtime
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=build /app .
ENV ASPNETCORE_URLS=http://+:8080
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "OrderPlatform.Api.dll"]
```

- Copying only .csproj files before `dotnet restore` means source-only changes reuse the cached restore layer, speeding up rebuilds significantly.
- USER appuser is set after all root-requiring setup (package installs, user creation) is complete, so the app itself never runs as root.

### A .dockerignore file to keep build context small (text)

Excluding files that bloat the build context and slow down `docker build`:

```text
bin/
obj/
**/*.user
.git/
.vs/
**/node_modules/
tests/
```

## Checklist

- [ ] The Dockerfile uses multi-stage builds so the final image doesn't contain SDK/build tooling.
- [ ] Dependency manifests are copied and restored before full source, maximizing layer cache reuse.
- [ ] The container runs as a non-root user in the final stage.
- [ ] Base image tags are pinned to a specific version, not 'latest'.
- [ ] A health check is defined so the container's liveness is observable by the orchestrator.
- [ ] The built image is scanned for known vulnerabilities in CI before being pushed to a registry.

## Anti-patterns

- **Single-stage build with SDK in production image** - Shipping the full SDK and build tools in the runtime image, bloating size and increasing attack surface.
- **Running as root** - Leaving the container's default root user in place for the application process, unnecessarily elevating the blast radius of a container escape.
- **Copying all source before restore** - COPY . . followed by restore, invalidating the dependency cache layer on every single source file change.
- **Floating 'latest' base image tags** - Using FROM mcr.microsoft.com/dotnet/aspnet:latest, making builds non-reproducible as the base image changes underneath you.
- **No image scanning** - Pushing images to a registry with no automated vulnerability scan, shipping known CVEs into production unnoticed.

## Verification

- `docker build` reuses the dependency-restore layer when only application source (not csproj/package.json) changes.
- `docker run` followed by a user check (whoami inside the container) confirms the process runs as a non-root user.
- A container vulnerability scan runs in CI and blocks the pipeline on critical/high findings.
- The final image size is meaningfully smaller than a single-stage build using the full SDK image.

## References

- skills/80-security/dependency-and-supply-chain-security/SKILL.md
- skills/60-devops/kubernetes-deployment/SKILL.md
- Docker documentation — multi-stage builds and best practices.
