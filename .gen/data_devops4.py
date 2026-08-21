SKILLS = [
    dict(
        dir="60-devops", slug="incident-response-and-runbooks", category="devops",
        tags=["incident-response", "runbooks", "on-call"],
        desc="Use when an on-call engineer needs a repeatable process for detecting, triaging, and resolving a production incident, backed by written runbooks for known failure modes.",
        purpose=[
            "Without a defined process, incidents are handled inconsistently — some resolved quickly by "
            "someone who happens to know the system, others dragging on because no one knows where to start. "
            "This skill establishes a repeatable incident response process (detect, triage, mitigate, "
            "resolve, review) and a runbook format for documenting known failure modes so any on-call "
            "engineer can act effectively.",
            "It treats the post-incident review as equally important as the resolution itself, since "
            "recurring incidents without a blameless review process indicate a broken feedback loop.",
        ],
        when_use=[
            "You are setting up or improving an on-call rotation and incident response process.",
            "A recent incident took longer to resolve than it should have because no runbook existed.",
            "You need to write a runbook for a known, previously-diagnosed failure mode.",
        ],
        when_not=[
            "The issue is a routine, already-triaged bug fix with no active production impact — handle it through the normal engineering workflow instead.",
            "You're investigating a security breach specifically — see skills/80-security/security-incident-response/SKILL.md for that specialized process.",
        ],
        prereqs=[
            "skills/60-devops/observability/SKILL.md for the signals that trigger and inform incident detection.",
            "A defined on-call rotation and paging tool already in place.",
        ],
        workflow=[
            ("Detect via alerting, not customer reports", "Alerts fire from SLO burn rate or key health metrics before customers notice, per skills/60-devops/observability/SKILL.md."),
            ("Declare the incident and assign an incident commander", "One clear owner coordinates the response; others investigate and execute under their direction."),
            ("Triage severity and communicate status", "Classify impact (SEV1-3), and post regular status updates to a status page or stakeholder channel."),
            ("Mitigate before root-causing", "Stop the bleeding first (rollback, feature-flag kill switch, scale up) even before fully understanding the root cause."),
            ("Follow the relevant runbook if one exists", "A written runbook for a known failure mode gives step-by-step mitigation instructions, reducing time-to-mitigate."),
            ("Resolve and confirm recovery", "Verify metrics have returned to normal and the mitigation is stable before declaring the incident resolved."),
            ("Hold a blameless post-incident review", "Document a timeline, contributing factors, and follow-up action items, focusing on systemic causes, not individual blame."),
            ("Write or update a runbook from what was learned", "Every incident without a prior runbook should produce one, or update an existing one, for next time."),
        ],
        decision=[
            ("An alert fires for a known, previously-diagnosed failure mode", "Follow its existing runbook directly rather than re-diagnosing from scratch."),
            ("An alert fires for a novel, undiagnosed issue", "Declare an incident, assign a commander, and investigate live, documenting findings for a future runbook."),
            ("The fix requires understanding root cause before it's safe to mitigate", "Still look for a safe stop-gap (traffic shed, circuit breaker, flag disable) while root-causing continues in parallel."),
            ("An incident recurs for the second time in a similar way", "Treat this as a signal the post-incident action items from the first occurrence weren't actually completed or were ineffective."),
            ("A postmortem reveals an individual's mistake as a contributing factor", "Focus on the process/system gap that allowed the mistake to cause impact, not on blaming the individual."),
        ],
        code_lang="markdown",
        code_intro="A runbook entry for a known, previously-diagnosed failure mode:",
        code=(
            "## Runbook: Order API returning 503s under high checkout volume\n"
            "\n"
            "**Symptoms:** OrderApiFastBurn alert fires; 5xx rate on /checkout exceeds 2%.\n"
            "\n"
            "**Likely cause:** Downstream payment provider latency spike causing thread-pool exhaustion.\n"
            "\n"
            "**Mitigation steps:**\n"
            "1. Check the payment provider status page and the `PaymentGatewayLatency` dashboard.\n"
            "2. If provider latency is elevated, enable the `PaymentProviderCircuitBreaker` feature flag\n"
            "   to fail fast and show a 'try again shortly' message instead of hanging requests.\n"
            "3. Scale the order-api Deployment replicas from 3 to 6 to absorb queued retries.\n"
            "4. Monitor error rate for 10 minutes; if it doesn't recover, escalate to the payments on-call.\n"
            "\n"
            "**Resolution:** Once payment provider latency normalizes, disable the circuit breaker flag\n"
            "and scale replicas back down.\n"
        ),
        code_notes=[
            "The runbook gives concrete, executable steps (flag names, dashboard names, exact scaling numbers), not vague advice like 'investigate payments'.",
            "It's written from a prior real incident, keeping it grounded in what actually happened rather than speculation.",
        ],
        code2_heading="A blameless post-incident review template excerpt (Markdown)",
        code2=("markdown",
            "Focused on timeline and systemic factors, not individual blame:",
            "## Incident Review: 2026-01-14 Checkout Outage\n"
            "\n"
            "**Impact:** 18 minutes of elevated 5xx errors on checkout, ~4% of attempted orders failed.\n"
            "\n"
            "**Timeline:** 14:02 alert fired -> 14:05 incident declared -> 14:11 mitigation applied -> 14:20 resolved.\n"
            "\n"
            "**Contributing factors:** No circuit breaker existed for the payment provider dependency;\n"
            "thread-pool exhaustion cascaded from one slow dependency to the whole checkout path.\n"
            "\n"
            "**Action items:** Add a circuit breaker (owner: X, due: Y); create this runbook (done).\n"
        ),
        checklist=[
            "Incidents are detected via automated alerting tied to SLOs, not primarily via customer reports.",
            "Every declared incident has a clear incident commander and severity classification.",
            "Mitigation is attempted before full root-cause analysis, prioritizing stopping user impact quickly.",
            "A runbook exists (or is created) for every recurring or previously-diagnosed failure mode.",
            "A blameless post-incident review happens after every significant incident, with concrete action items.",
            "Post-incident action items are tracked to completion, not left open indefinitely.",
        ],
        antipatterns=[
            ("Customer-reported detection", "Learning about an outage from customer support tickets before any internal alert fired, indicating a monitoring gap."),
            ("No incident commander", "Multiple engineers investigating in parallel with no clear coordination, duplicating effort or missing critical steps."),
            ("Root-cause-first response", "Refusing to apply any mitigation until the root cause is fully understood, prolonging user-facing impact unnecessarily."),
            ("Tribal-knowledge-only troubleshooting", "Only one specific engineer knows how to resolve a recurring issue, with no runbook capturing that knowledge."),
            ("Blame-focused postmortems", "Post-incident reviews that focus on which individual made a mistake instead of what systemic gap allowed it to cause impact."),
        ],
        verification=[
            "A sample of recent incidents shows detection time close to alert-fire time, not customer-report time.",
            "Every SEV1/SEV2 incident in the last quarter has a completed, blameless post-incident review document.",
            "A runbook exists for each of the top recurring alert types, verified against the alert catalog.",
            "Action items from past reviews are tracked and show a completion rate, not an ever-growing backlog.",
        ],
        references=[
            "skills/60-devops/observability/SKILL.md",
            "skills/80-security/security-incident-response/SKILL.md",
            "Google SRE Book — Incident Response and Postmortems.",
            "templates/runbook.template.md",
        ],
    ),
    dict(
        dir="60-devops", slug="cost-and-resource-optimization", category="devops",
        tags=["finops", "cost-optimization", "cloud"],
        desc="Use when cloud infrastructure spend needs to be understood, attributed, and reduced without compromising reliability or performance.",
        purpose=[
            "Cloud costs left unmanaged tend to grow through over-provisioning, orphaned resources, and lack "
            "of visibility into which team or feature is driving spend. This skill covers cost attribution "
            "via tagging, right-sizing resources based on actual usage, and applying cost-saving purchase "
            "options (reserved/spot capacity) without sacrificing the reliability guarantees the system needs.",
            "It treats cost as a first-class non-functional requirement, reviewed alongside performance and "
            "reliability rather than as an afterthought handled only when a bill spikes unexpectedly.",
        ],
        when_use=[
            "Cloud spend is growing faster than usage/traffic would justify.",
            "You need to attribute cost to specific teams, services, or features for accountability.",
            "You are reviewing whether a workload is over-provisioned relative to its actual utilization.",
        ],
        when_not=[
            "The system is pre-launch or low-traffic and cost is genuinely negligible relative to engineering time spent optimizing it.",
            "The proposed cost-saving change (e.g. aggressive spot usage) would compromise a reliability guarantee more valuable than the savings.",
        ],
        prereqs=[
            "skills/60-devops/infrastructure-as-code/SKILL.md for consistent tagging enforced at provisioning time.",
            "skills/60-devops/observability/SKILL.md for the utilization metrics right-sizing decisions depend on.",
        ],
        workflow=[
            ("Tag every resource with owner and purpose", "Consistent team/service/environment tags enable cost attribution in billing reports, enforced via IaC policy."),
            ("Review utilization against provisioned capacity regularly", "Compare actual CPU/memory/IO usage against requested/reserved capacity to find over-provisioned resources."),
            ("Right-size based on measured usage, not guesswork", "Reduce instance size or replica count for consistently underutilized resources, informed by real metrics over a representative period."),
            ("Use autoscaling to match capacity to real demand", "Scale down during low-traffic periods automatically rather than provisioning for peak load permanently."),
            ("Apply committed-use discounts for stable, predictable workloads", "Reserved instances or savings plans for baseline capacity that's reliably running long-term."),
            ("Use spot/preemptible capacity only for interruption-tolerant workloads", "Batch jobs and stateless, retriable workloads are good candidates; anything stateful or latency-critical is not."),
            ("Clean up orphaned and unused resources", "Regularly identify and remove unattached volumes, idle load balancers, and unused snapshots that accrue cost with no benefit."),
            ("Set budget alerts per team/project", "Automated alerts on spend anomalies catch runaway costs quickly, not at the end of a monthly billing cycle."),
        ],
        decision=[
            ("A resource consistently runs at 10% CPU utilization", "Right-size it to a smaller instance type or reduce replica count, backed by the observed metric history."),
            ("Traffic has a predictable daily/weekly pattern with clear low-traffic periods", "Use autoscaling (including scale-to-zero for non-critical workloads) rather than static peak-sized provisioning."),
            ("A workload runs continuously and predictably for a year or more", "Purchase reserved capacity/savings plans for that baseline rather than paying full on-demand rates indefinitely."),
            ("A batch job can tolerate being interrupted and retried", "Run it on spot/preemptible instances at a significant discount versus on-demand."),
            ("An orphaned resource (unattached disk, idle load balancer) is found", "Confirm it's truly unused, then delete it; don't let 'just in case' resources accumulate cost indefinitely."),
        ],
        code_lang="hcl",
        code_intro="Enforcing cost-attribution tags via a Terraform policy check:",
        code=(
            "# Required tags enforced at plan time via a policy-as-code check (e.g. Sentinel/OPA)\n"
            "resource \"cloud_compute_instance\" \"api\" {\n"
            "  name          = \"order-api\"\n"
            "  instance_type = \"m5.large\"\n"
            "  tags = {\n"
            "    team        = \"orders\"\n"
            "    environment = \"production\"\n"
            "    cost_center = \"CC-4471\"\n"
            "  }\n"
            "}\n"
            "\n"
            "# Policy rule (conceptual): reject any resource lacking team/environment/cost_center tags\n"
            "# so every line item in the cloud bill can be attributed to a specific owner.\n"
        ),
        code_notes=[
            "Enforcing tags at plan time (failing the pipeline on missing tags) is far more reliable than asking engineers to remember to tag resources manually.",
            "cost_center enables direct mapping from cloud billing exports to internal budget owners.",
        ],
        code2_heading="A budget alert configuration to catch anomalous spend early (YAML, conceptual)",
        code2=("yaml",
            "Alerting well before a monthly bill surprises anyone:",
            "budgets:\n"
            "  - name: orders-team-monthly\n"
            "    amount: 5000\n"
            "    currency: USD\n"
            "    filter: { tag: { team: orders } }\n"
            "    alerts:\n"
            "      - threshold_percent: 80\n"
            "        notify: [\"orders-team-slack\"]\n"
            "      - threshold_percent: 100\n"
            "        notify: [\"orders-team-slack\", \"finops-oncall\"]\n"
        ),
        checklist=[
            "Every provisioned resource carries owner/team/environment tags, enforced at plan/apply time.",
            "Resource sizing is reviewed against measured utilization, not left at original provisioning guesses indefinitely.",
            "Autoscaling matches capacity to real demand rather than permanently provisioning for peak load.",
            "Committed-use discounts are applied to stable, predictable baseline workloads.",
            "Spot/preemptible capacity is used only for genuinely interruption-tolerant workloads.",
            "Orphaned resources are identified and cleaned up on a regular cadence, and budget alerts catch spend anomalies early.",
        ],
        antipatterns=[
            ("Untagged resources", "Provisioning infrastructure with no owner/team tags, making it impossible to attribute cost or safely clean it up later."),
            ("Provision-for-peak-forever", "Sizing a service permanently for its highest-ever traffic spike instead of using autoscaling to match real, varying demand."),
            ("Spot instances for stateful critical workloads", "Running a primary database or stateful critical service on preemptible/spot capacity, risking data loss or downtime on reclaim."),
            ("Orphaned resource accumulation", "Leaving unattached disks, idle load balancers, and old snapshots running indefinitely because no one is responsible for cleaning them up."),
            ("Cost reviewed only after a billing surprise", "Treating cost optimization as a reactive fire-drill after an unexpectedly large invoice instead of an ongoing practice."),
        ],
        verification=[
            "A billing report can attribute at least 95% of monthly spend to a specific team/service via tags.",
            "A right-sizing review identifies and resizes/removes resources running below an agreed utilization threshold for a sustained period.",
            "No stateful, critical workload is found running on spot/preemptible capacity during an infrastructure audit.",
            "Budget alerts fire correctly in a test scenario before spend reaches 100% of the configured threshold.",
        ],
        references=[
            "skills/60-devops/infrastructure-as-code/SKILL.md",
            "skills/60-devops/observability/SKILL.md",
            "FinOps Foundation — FinOps Framework.",
        ],
    ),
]
