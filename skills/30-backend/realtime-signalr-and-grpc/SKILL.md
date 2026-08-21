---
name: realtime-signalr-and-grpc
description: Use when a feature needs server-push updates to clients or high-throughput internal service-to-service calls and you must choose between SignalR and gRPC.
category: backend
tags: [signalr, grpc, realtime]
maturity: stable
updated: 2026-08-21
---

## Purpose

REST over HTTP is poorly suited to two common needs: pushing live updates to browser clients, and high-throughput, strongly-typed internal service calls. SignalR provides real-time server-to-client messaging over WebSockets with fallback transports, while gRPC provides efficient, strongly-typed, bidirectional streaming for service-to-service communication.

This skill covers choosing between them correctly and structuring each so they don't become brittle, hard-to-scale additions to the architecture.

## When to use / When NOT to use

**Use this skill when:**

- A UI needs live updates (notifications, live dashboards, chat) without polling.
- Two internal services need high-throughput, low-latency, strongly-typed calls, potentially with streaming.
- You are deciding between REST, SignalR, and gRPC for a new communication requirement.

**Do NOT use this skill when:**

- A simple request/response REST call would suffice — see skills/20-architecture/api-design-rest/SKILL.md instead.
- The client is a public third-party integrator that expects a standard REST/GraphQL contract, not gRPC or SignalR-specific protocols.

## Prerequisites

- skills/20-architecture/api-design-graphql-and-grpc/SKILL.md for gRPC contract design fundamentals.
- skills/20-architecture/resilience-patterns/SKILL.md for reconnect/backoff behavior.
- A load balancer/proxy that supports HTTP/2 and WebSockets if scaling beyond one instance.

## Workflow

1. **Identify the communication shape needed** - Server-push to many browser clients suggests SignalR; internal high-throughput RPC suggests gRPC.
2. **For SignalR, design hubs around a small set of client-facing operations** - Keep hub methods thin, delegating real logic to the Application layer via MediatR.
3. **Use groups for targeted broadcasting** - Add connections to groups (e.g. per-order, per-tenant) rather than broadcasting every update to every connected client.
4. **Configure a backplane for multi-instance SignalR** - Use Redis or Azure SignalR Service as a backplane so messages reach clients connected to any instance.
5. **For gRPC, define contracts in .proto files first** - Treat the .proto file as the source of truth, generating both client and server stubs from it.
6. **Use gRPC streaming only when genuinely needed** - Prefer unary calls unless the use case truly needs client, server, or bidirectional streaming.
7. **Plan reconnect and backoff on the client for both** - SignalR's automatic reconnect and gRPC client retry policies should be configured explicitly, not left at defaults.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Browser needs live order status updates | Use SignalR with a per-order group, pushed from the Application layer after a domain event. |
| Two internal microservices need a low-latency RPC call | Use gRPC with a well-defined .proto contract. |
| A public third-party API is being exposed | Use REST/GraphQL, not gRPC or SignalR, for broad client compatibility. |
| SignalR needs to scale beyond one instance | Add a backplane (Redis or Azure SignalR Service) before scaling out, or messages will only reach clients on the same instance. |
| A gRPC call needs a stream of continuously changing data | Use server streaming; reserve bidirectional streaming for genuinely two-way continuous exchanges. |

## Reference implementation

A thin SignalR hub delegating to the Application layer, broadcasting to a per-order group:

```csharp
public class OrderStatusHub : Hub
{
    public async Task JoinOrderGroup(string orderId) =>
        await Groups.AddToGroupAsync(Context.ConnectionId, $"order-{orderId}");
}

// Called from an Application-layer event handler after OrderStatusChanged:
public class OrderStatusNotifier : INotificationHandler<OrderStatusChangedEvent>
{
    private readonly IHubContext<OrderStatusHub> _hub;
    public OrderStatusNotifier(IHubContext<OrderStatusHub> hub) => _hub = hub;

    public Task Handle(OrderStatusChangedEvent e, CancellationToken ct) =>
        _hub.Clients.Group($"order-{e.OrderId}")
            .SendAsync("orderStatusChanged", new { e.OrderId, e.NewStatus }, ct);
}
```

- The hub itself contains no business logic; notifications originate from domain event handlers in the Application layer.
- Group naming ($"order-{orderId}") ensures only clients watching that specific order receive the update.

### A gRPC service contract and minimal implementation (proto + C#)

Contract-first gRPC definition, with the server implementation delegating to Application handlers:

```protobuf
service InventoryService {
  rpc ReserveStock (ReserveStockRequest) returns (ReserveStockReply);
}
message ReserveStockRequest { string product_id = 1; int32 quantity = 2; }
message ReserveStockReply { bool reserved = 1; int32 remaining = 2; }

// C# server implementation
public override async Task<ReserveStockReply> ReserveStock(
    ReserveStockRequest request, ServerCallContext context)
{
    var result = await _mediator.Send(new ReserveStockCommand(
        request.ProductId, request.Quantity), context.CancellationToken);
    return new ReserveStockReply { Reserved = result.Reserved, Remaining = result.Remaining };
}
```

## Checklist

- [ ] The communication shape (push vs RPC) was deliberately chosen, not defaulted to whatever was easiest.
- [ ] SignalR hubs are thin and delegate business logic to the Application layer.
- [ ] Broadcasts use targeted groups, not all-clients broadcast, where only a subset should receive updates.
- [ ] A backplane is configured for SignalR if the service scales to more than one instance.
- [ ] gRPC contracts are defined in .proto files as the source of truth for both client and server.
- [ ] Streaming is used only where the use case genuinely requires it, not as a default choice.

## Anti-patterns

- **Broadcasting to all clients** - Sending every update to every connected SignalR client instead of scoping via groups, wasting bandwidth and leaking data across tenants.
- **Business logic inside the hub** - Implementing domain rules directly in a SignalR Hub class instead of delegating to the Application layer.
- **No backplane at scale** - Deploying SignalR across multiple instances without a backplane, causing clients on different instances to miss messages.
- **gRPC for public third-party APIs** - Exposing gRPC as the only interface for external partner integrations that expect standard REST/GraphQL.
- **Streaming used unnecessarily** - Defaulting to bidirectional streaming for what is really a simple unary request/response, adding needless complexity.

## Verification

- A load test with multiple instances confirms SignalR messages reach clients connected to any instance (backplane works).
- Hub methods contain no direct business logic, confirmed by code review.
- gRPC contract changes go through .proto review before server/client code is regenerated.
- Reconnect/backoff behavior is exercised in a test that simulates a dropped connection.

## References

- skills/20-architecture/api-design-graphql-and-grpc/SKILL.md
- skills/20-architecture/resilience-patterns/SKILL.md
- Microsoft Learn — ASP.NET Core SignalR and gRPC documentation.
