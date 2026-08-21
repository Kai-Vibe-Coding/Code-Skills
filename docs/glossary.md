# Glossary

Terms used consistently across skills in this catalog.

- **ADR (Architecture Decision Record):** A short document capturing a
  significant architectural decision, its context, and its consequences.
  See `templates/adr.template.md`.

- **Bounded Context:** A Domain-Driven Design boundary within which a
  particular domain model applies unambiguously.

- **CQRS:** Command Query Responsibility Segregation — separating the
  model used to write data from the model used to read it.

- **DoR / DoD:** Definition of Ready / Definition of Done — the entry and
  exit criteria for a unit of work.

- **Idempotency:** A property of an operation such that performing it
  multiple times has the same effect as performing it once.

- **Maturity (skill metadata):** `draft` skills are new or unreviewed;
  `stable` skills have been reviewed and are safe to rely on as-is.

- **Outbox Pattern:** A reliability pattern that persists an event to an
  "outbox" table in the same transaction as a business change, then
  publishes it asynchronously.

- **RPO / RTO:** Recovery Point Objective / Recovery Time Objective — the
  maximum tolerable data loss and downtime for a system during an incident.

- **SLI / SLO / SLA:** Service Level Indicator (a measured metric),
  Objective (an internal target for that metric), and Agreement (an
  externally committed target, often with penalties).

- **STRIDE:** A threat modeling mnemonic covering Spoofing, Tampering,
  Repudiation, Information Disclosure, Denial of Service, and Elevation of
  Privilege.

- **Trust Boundary:** A point in a system where data or control crosses
  between components with different levels of trust.

- **Zero-downtime migration:** A database schema change applied without
  taking the application offline, typically via expand/contract phases.
