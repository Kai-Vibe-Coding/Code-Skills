---
name: background-jobs-and-messaging
description: Use when work must run outside the request/response cycle, such as scheduled jobs, retries, or asynchronous processing triggered by messages on a queue.
category: backend
tags: [background-jobs, messaging, queues]
maturity: stable
updated: 2026-08-21
---

## Purpose

Not all work belongs inside an HTTP request: long-running tasks, scheduled jobs, and cross-service communication need durable background processing that survives restarts and handles failures gracefully. This skill covers structuring background jobs and message-driven processing in .NET using hosted services, a job scheduler, and a message broker.

It emphasizes idempotency and reliable delivery, since background work is retried far more often than request/response calls and must tolerate at-least-once delivery semantics.

## When to use / When NOT to use

**Use this skill when:**

- A use case involves work that shouldn't block the HTTP response (sending emails, generating reports).
- Work must run on a schedule (nightly reconciliation, cleanup jobs).
- Services need to communicate asynchronously via events rather than synchronous calls.

**Do NOT use this skill when:**

- The work is fast and must complete before responding to the caller — do it synchronously in the request instead.
- You're designing the event schema itself — see skills/20-architecture/event-driven-architecture/SKILL.md first.

## Prerequisites

- skills/20-architecture/event-driven-architecture/SKILL.md for the messaging patterns underlying this skill.
- skills/20-architecture/resilience-patterns/SKILL.md for retry/backoff behavior of job processing.
- A message broker (e.g. RabbitMQ, Azure Service Bus) or job scheduling library (Hangfire, Quartz.NET) selected.

## Workflow

1. **Classify the work as scheduled, queued, or fire-and-forget** - Scheduled jobs run on a timer; queued jobs process messages from a broker; fire-and-forget defers non-critical work briefly.
2. **Implement scheduled jobs as hosted services** - Use IHostedService/BackgroundService with a timer, or a scheduler like Hangfire for cron-style recurring jobs.
3. **Implement message consumers as durable subscribers** - A consumer reads from a durable queue and acknowledges only after successful processing (at-least-once delivery).
4. **Design every handler to be idempotent** - Use a processed-message-id table or natural idempotency keys so re-delivery doesn't cause duplicate side effects.
5. **Apply retry with backoff and a dead-letter queue** - Failed messages retry with exponential backoff a bounded number of times, then move to a dead-letter queue for investigation.
6. **Emit domain events transactionally via the outbox pattern** - Write the event to an outbox table in the same transaction as the state change, then publish it asynchronously.
7. **Monitor queue depth and failure rate** - Wire dead-letter queue size and processing failure rate into skills/60-devops/observability/SKILL.md dashboards and alerts.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Work must run at a fixed time daily | Use a scheduled hosted job (Hangfire recurring job or Quartz.NET trigger). |
| Work is triggered by another service's event | Use a durable message consumer subscribed to that event, not polling. |
| A handler must not process the same message twice | Store processed message IDs and check/skip on redelivery — assume at-least-once delivery always. |
| A state change must reliably trigger an event | Use the transactional outbox pattern instead of publishing directly inside the same transaction as the DB write. |
| A message fails repeatedly | Route it to a dead-letter queue after a bounded retry count rather than retrying indefinitely and blocking the queue. |

## Reference implementation

An idempotent message consumer using an outbox-published event:

```csharp
public class OrderPlacedConsumer : IConsumer<OrderPlacedEvent>
{
    private readonly IProcessedMessageStore _processed;
    private readonly IEmailSender _email;

    public async Task Consume(ConsumeContext<OrderPlacedEvent> context)
    {
        var messageId = context.MessageId?.ToString() ?? context.Message.OrderId.ToString();
        if (await _processed.WasProcessedAsync(messageId, context.CancellationToken))
            return; // already handled this delivery, safe to skip

        await _email.SendOrderConfirmationAsync(context.Message.OrderId, context.CancellationToken);
        await _processed.MarkProcessedAsync(messageId, context.CancellationToken);
    }
}
```

- Checking WasProcessedAsync first makes the consumer safe under at-least-once delivery, where the broker may redeliver on ack failure.
- MarkProcessedAsync should be committed atomically with any other state change the handler makes, ideally in one transaction.

### Transactional outbox write alongside a state change (C#)

Guaranteeing the event is never lost even if publishing fails immediately after commit:

```csharp
await using var tx = await _db.Database.BeginTransactionAsync(ct);
order.Submit();
_db.Outbox.Add(new OutboxMessage
{
    Id = Guid.NewGuid(),
    Type = nameof(OrderPlacedEvent),
    Payload = JsonSerializer.Serialize(new OrderPlacedEvent(order.Id)),
    OccurredAt = DateTime.UtcNow
});
await _db.SaveChangesAsync(ct);
await tx.CommitAsync(ct);
// A separate background poller reads unpublished Outbox rows and publishes them to the broker.
```

## Checklist

- [ ] Every message consumer is idempotent against redelivery, verified with a repeated-delivery test.
- [ ] Scheduled work uses a hosted service or scheduler library, not an ad hoc Thread.Sleep loop.
- [ ] State changes that must emit events use the transactional outbox pattern, not direct in-transaction publish.
- [ ] Failed messages retry with bounded exponential backoff, then land in a dead-letter queue.
- [ ] Queue depth and dead-letter counts are monitored with alerts, not just logs.
- [ ] Background job failures are logged with enough context to diagnose without reproducing manually.

## Anti-patterns

- **Publish-then-commit** - Publishing an event before committing the database transaction, risking a published event for a change that then fails to commit.
- **Non-idempotent consumers** - Assuming exactly-once delivery and performing non-idempotent side effects (e.g. charging a card twice) on redelivery.
- **Infinite retry with no dead-letter queue** - Retrying a poison message forever, blocking the queue and hiding the real error from anyone.
- **Thread.Sleep-based scheduling** - Implementing 'scheduled' jobs with an infinite loop and Task.Delay instead of a proper scheduler with observability and skip-if-still-running semantics.
- **Silent failure swallowing** - Catching and ignoring exceptions in a background job so failures never surface in logs or alerts.

## Verification

- Redelivering the same message to a consumer twice produces no duplicate side effects, verified by an idempotency test.
- Killing the process mid-transaction never results in a published event without a corresponding committed state change.
- Dead-letter queue depth and failure-rate alerts are configured and tested to fire.
- A scheduled job's execution history is visible via logs/dashboard, not just inferred from side effects.

## References

- skills/20-architecture/event-driven-architecture/SKILL.md
- skills/20-architecture/resilience-patterns/SKILL.md
- skills/60-devops/observability/SKILL.md
- MassTransit / Hangfire documentation.
