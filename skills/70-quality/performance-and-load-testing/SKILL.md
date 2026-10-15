---
name: performance-and-load-testing
description: Use when you need to verify a system meets its latency and throughput requirements under realistic and peak load before it reaches production.
category: quality
tags: [load-testing, performance-testing, k6]
maturity: stable
updated: 2026-08-21
---

## Purpose

Functional tests confirm correctness but say nothing about how a system behaves under real concurrent load — that's where capacity and latency problems actually surface. This skill covers designing load tests that reflect realistic traffic patterns, defining pass/fail thresholds tied to actual SLOs, and running different test types (load, stress, soak) for different questions.

It emphasizes running performance tests continuously (or at least per significant release) rather than only once before a major launch, since performance regressions creep in gradually.

## When to use / When NOT to use

**Use this skill when:**

- You need to validate a service meets its latency/throughput SLOs before a major launch or scaling event.
- You suspect a recent change introduced a performance regression.
- You need to determine a system's actual capacity limits ahead of an anticipated traffic spike.

**Do NOT use this skill when:**

- You're diagnosing a single already-identified slow query — see skills/50-database/indexing-and-query-optimization/SKILL.md for a more targeted approach.
- The system has no meaningful concurrent user load (e.g. an internal single-user batch tool).

## Prerequisites

- skills/60-devops/observability/SKILL.md for the metrics load test results should be measured against.
- skills/20-architecture/scalability-and-capacity-planning/SKILL.md for the target load profile and SLOs being validated.

## Workflow

1. **Define pass/fail thresholds tied to real SLOs** - e.g. p95 latency under 300ms and error rate under 0.1% at target throughput — not just 'run it and see'.
2. **Model realistic traffic patterns, not uniform load** - Reflect real usage: ramp-up, peak, and think-time between actions, not every virtual user hammering one endpoint simultaneously with zero pause.
3. **Run a load test at expected peak traffic** - Confirm the system meets its SLOs at the traffic level actually expected in production.
4. **Run a stress test to find the breaking point** - Increase load beyond expected peak until the system degrades, to know the actual headroom and failure mode.
5. **Run a soak test for sustained-duration issues** - A multi-hour test at moderate load reveals memory leaks or resource exhaustion that a short test wouldn't surface.
6. **Test against a production-representative environment** - Run against infrastructure sized and configured like production, not a scaled-down dev environment, or the results won't be meaningful.
7. **Correlate load test results with backend observability** - Watch CPU, memory, DB connection pool, and queue depth during the test, not just client-observed latency.
8. **Run performance tests as part of the regular release cadence** - Catch gradual regressions per release rather than only discovering them once at a big launch event.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| You need to confirm the system meets its SLOs at expected peak traffic | Run a load test at that specific target throughput with realistic traffic shape. |
| You need to know the system's actual maximum capacity | Run a stress test that ramps load until failure, identifying the true bottleneck (CPU, DB connections, thread pool). |
| You suspect a slow memory leak or resource exhaustion over time | Run a soak test over several hours at moderate, sustained load. |
| A load test result looks fine at the client but the backend feels sluggish | Correlate with backend metrics (DB pool, CPU) — the bottleneck may be masked by client-side retry/timeout behavior. |
| A load test passes in a scaled-down test environment | Distrust the result until it's confirmed on a production-representative environment, since scaled-down infra often hides real bottlenecks. |

## Reference implementation

A k6 load test modeling realistic traffic with think-time and SLO-based thresholds:

```javascript
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 200 },   // ramp up to expected peak
    { duration: '5m', target: 200 },   // sustain peak
    { duration: '2m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'],  // SLO: p95 latency under 300ms
    http_req_failed: ['rate<0.001'],   // SLO: error rate under 0.1%
  },
};

export default function () {
  const res = http.get('https://staging.example.com/api/orders');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(Math.random() * 3 + 1); // realistic think-time between requests
}
```

- Thresholds are tied directly to SLOs (p95 latency, error rate), making the test result an automatic pass/fail rather than requiring manual interpretation.
- sleep() with randomized think-time better approximates real user behavior than firing requests back-to-back with zero pause.

### A CI gate failing the pipeline on an SLO breach (YAML)

Making performance regression a release-blocking signal, not just informational:

```yaml
- name: Run load test
  run: k6 run --out json=results.json load-test.js
- name: Fail on threshold breach
  run: |
    if grep -q '"thresholds_failed":true' results.json; then
      echo 'Performance SLO breached'; exit 1;
    fi
```

## Checklist

- [ ] Pass/fail thresholds are tied to real SLOs, not left as an ambiguous 'run and eyeball it' result.
- [ ] Traffic patterns model realistic ramp-up, peak, and think-time rather than uniform zero-pause load.
- [ ] Load, stress, and soak tests are used for their distinct purposes rather than one generic test for everything.
- [ ] Tests run against a production-representative environment, not a significantly scaled-down one.
- [ ] Backend observability (CPU, DB pool, queue depth) is correlated with client-observed results during the test.
- [ ] Performance tests run as part of the regular release cadence, not only once before a major launch.

## Anti-patterns

- **No defined pass/fail criteria** - Running a load test and eyeballing 'it seems fine' instead of an explicit SLO-based threshold.
- **Unrealistic zero-think-time load** - Firing requests back-to-back with no pause between them, producing a load shape nothing like real user behavior.
- **Testing only in a scaled-down environment** - Running load tests against a tiny dev environment and assuming results transfer directly to production-scale infrastructure.
- **One-time pre-launch testing only** - Load testing once before a big launch and never again, missing gradual performance regressions introduced by later releases.
- **Ignoring backend metrics during the test** - Looking only at client-side latency/throughput numbers without correlating against server-side resource utilization to find the real bottleneck.

## Verification

- A load test run reports an automatic pass/fail based on SLO thresholds, not manual interpretation.
- A stress test identifies the specific resource (CPU, DB connections, thread pool) that becomes the bottleneck at failure.
- A soak test of several hours shows stable memory/resource usage, not a steady upward trend indicating a leak.
- Load test results are confirmed consistent between the test environment and a production-representative environment.

## References

- skills/60-devops/observability/SKILL.md
- skills/20-architecture/scalability-and-capacity-planning/SKILL.md
- k6 documentation.
