# SDK architecture

The Python SDK is a context-aware wrapper over the Blocklog HTTP API. It owns
authentication headers, timeouts, safe read retries, event serialization, and
optional batching. The backend owns validation, persistence, rate limiting, and
verification artifacts.

```text
Python application -> Python SDK -> HTTP/API -> Blocklog backend
                                         -> execution/event infrastructure
                                         -> verification and receipts
```

`record_event()` calls the backend-supported `POST /api/v1/logs` route. Batched
events use `POST /api/v1/logs/batch`. These mutations are not automatically
retried because the backend's ingestion contract does not document idempotent
replay behavior. GET operations may be retried for transient errors.

The execution-management backend currently exposes `/api/v1/executions` and
its step/status routes; its request shape is defined by the backend FastAPI
signatures and remains the source of truth.
