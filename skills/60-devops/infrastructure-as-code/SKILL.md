---
name: infrastructure-as-code
description: Use when provisioning or modifying cloud infrastructure and you need it defined declaratively, version-controlled, and reviewed like application code.
category: devops
tags: [iac, terraform, infrastructure]
maturity: stable
updated: 2026-08-21
---

## Purpose

Manually clicking through a cloud console to provision infrastructure is unrepeatable, undocumented, and impossible to review. This skill establishes Infrastructure as Code (IaC) using a declarative tool (Terraform, as the running example) with modules, remote state, and a plan-review-apply workflow that treats infrastructure changes with the same rigor as application code changes.

It also covers structuring state and modules so environments (dev/staging/production) stay consistent while allowing controlled per-environment variation.

## When to use / When NOT to use

**Use this skill when:**

- You are provisioning new cloud infrastructure (compute, networking, databases, queues).
- Existing infrastructure was created manually and needs to be brought under version control.
- You need consistent, repeatable environments across dev/staging/production.

**Do NOT use this skill when:**

- You are making a one-off, throwaway sandbox resource for a few hours of manual experimentation with no lasting need.
- The change is purely application configuration (env vars, feature flags) already covered by skills/30-backend/configuration-and-feature-flags/SKILL.md.

## Prerequisites

- skills/80-security/secrets-and-key-management/SKILL.md for how credentials used by IaC tooling are stored and rotated.
- A remote state backend (e.g. cloud storage bucket with locking) already provisioned or planned.

## Workflow

1. **Define infrastructure declaratively in version control** - All resources described in Terraform (or equivalent) files, committed and reviewed like code.
2. **Use remote state with locking** - Store state in a shared backend (e.g. S3 + DynamoDB lock table) so concurrent applies don't corrupt state.
3. **Structure reusable modules per resource type** - A module for 'a standard web service' or 'a standard database' encapsulates best-practice defaults, reused across services.
4. **Parameterize per-environment differences** - Use variables/workspaces for the handful of things that legitimately differ between dev/staging/production (size, replica count), not the whole structure.
5. **Run plan before every apply** - Review the diff a change would make to real infrastructure before applying it, in CI and locally.
6. **Require review and approval for apply, especially in production** - Treat `terraform apply` against production as a gated, reviewed action, not an unattended step run by anyone at any time.
7. **Avoid manual console changes ('ClickOps')** - Any manual change made outside IaC causes drift; if it must happen in an emergency, import it back into code immediately after.
8. **Tag and document every resource's ownership** - Every resource carries owner/team/environment tags for cost attribution and operational clarity.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A new microservice needs standard supporting infrastructure | Use an existing shared module (e.g. 'web-service') rather than writing bespoke Terraform for each new service. |
| An environment needs a smaller/cheaper instance size than production | Parameterize instance size/count via variables, keeping the same module structure across environments. |
| Infrastructure state shows drift from a manual console change | Import the manual change into Terraform state immediately, or revert it, rather than leaving code and reality out of sync. |
| A production change is high-risk (e.g. deleting a resource) | Require an explicit manual approval gate on `terraform apply` for production, even if lower environments auto-apply. |
| Multiple teams manage related infrastructure | Split state by logical boundary (e.g. per service or per environment) to limit blast radius, rather than one giant shared state file. |

## Reference implementation

A reusable Terraform module for a standard web service, parameterized per environment:

```hcl
# modules/web-service/main.tf
variable "environment" { type = string }
variable "instance_count" {
  type    = number
  default = 2
}
variable "instance_size" {
  type    = string
  default = "small"
}

resource "cloud_app_service" "this" {
  name          = "order-api-${var.environment}"
  instance_count = var.instance_count
  instance_size  = var.instance_size
  tags = { team = "orders", environment = var.environment, managed_by = "terraform" }
}

# environments/production/main.tf
module "order_api" {
  source          = "../../modules/web-service"
  environment     = "production"
  instance_count  = 4
  instance_size   = "large"
}
```

- The same module is reused for dev/staging/production; only instance_count and instance_size differ per environment.
- Consistent tagging (team, environment, managed_by) supports cost attribution and quickly identifying non-IaC-managed resources.

### Remote state configuration with locking (HCL)

Preventing concurrent applies from corrupting shared state:

```hcl
terraform {
  backend "s3" {
    bucket         = "acme-terraform-state"
    key            = "orders/production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

## Checklist

- [ ] All infrastructure is defined declaratively in version-controlled IaC files, not created manually.
- [ ] Remote state with locking prevents concurrent applies from corrupting state.
- [ ] Reusable modules encapsulate best-practice defaults for common resource types.
- [ ] Per-environment differences are parameterized via variables, not duplicated module structures.
- [ ] `terraform plan` is reviewed before every apply, especially for production.
- [ ] Every resource is tagged with owning team and environment for cost and operational clarity.

## Anti-patterns

- **ClickOps** - Making manual changes in the cloud console 'just this once', causing drift between actual infrastructure and the IaC definition.
- **One giant state file for everything** - Storing all environments and services in a single Terraform state, maximizing blast radius for any mistake or lock contention.
- **Unreviewed production applies** - Allowing `terraform apply` against production to run unattended with no plan review or approval gate.
- **Copy-pasted per-environment Terraform** - Duplicating near-identical Terraform files per environment instead of one parameterized module, causing them to drift apart over time.
- **No resource tagging** - Provisioning resources with no owner/team/environment tags, making cost attribution and cleanup of orphaned resources difficult.

## Verification

- A `terraform plan` run against production shows zero unexpected diff (no undetected drift) before a scheduled change.
- Attempting a concurrent `terraform apply` from two locations is blocked by the state lock, confirmed by a test.
- Every environment's infrastructure is provisioned from the same shared module, confirmed by reviewing the environment-specific configuration files.
- A resource created outside Terraform is detected via drift and imported or removed within an agreed time window.

## References

- skills/80-security/secrets-and-key-management/SKILL.md
- skills/60-devops/cost-and-resource-optimization/SKILL.md
- HashiCorp Terraform documentation.
