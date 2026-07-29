"""
blocklog.api.traces
~~~~~~~~~~~~~~~~~~~
Layer 2 client for trace and session queries.

Available via ``client.traces.*``.

Backend endpoints
-----------------
- GET  /api/v1/traces
- GET  /api/v1/traces/{trace_id}
- GET  /api/v1/sessions/{session_id}/timeline
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blocklog.client import BlocklogClient


class TracesClient:
    """Query traces and session timelines.

    Accessed as ``client.traces``.

    Examples
    --------
    >>> traces = client.traces.list(event_type="DECISION_COMPLETE", limit=20)
    >>> detail  = client.traces.get("trace-uuid")
    >>> timeline = client.traces.session_timeline("session-uuid")
    """

    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    def list(
        self,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        workflow_id: str | None = None,
        source: str | None = None,
        event_type: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List traces with optional filters.

        Parameters
        ----------
        trace_id:
            Filter to a specific trace.
        session_id:
            Filter to a specific session.
        workflow_id:
            Filter to a specific workflow.
        source:
            Filter by event source string.
        event_type:
            Filter by event type (e.g. ``"DECISION_COMPLETE"``).
        from_ts:
            ISO-8601 lower bound for event timestamp.
        to_ts:
            ISO-8601 upper bound for event timestamp.
        limit:
            Maximum number of results (1–200, default 50).

        Returns
        -------
        list[dict]
            List of trace/log records.
        """
        params: dict[str, Any] = {"limit": limit}
        if trace_id:
            params["trace_id"] = trace_id
        if session_id:
            params["session_id"] = session_id
        if workflow_id:
            params["workflow_id"] = workflow_id
        if source:
            params["source"] = source
        if event_type:
            params["event_type"] = event_type
        if from_ts:
            params["from"] = from_ts
        if to_ts:
            params["to"] = to_ts

        result = self._client.retry.run(
            lambda: self._client.transport.request("GET", "/traces", params=params)
        )
        return result.get("items", result) if isinstance(result, dict) else result

    def get(self, trace_id: str) -> dict[str, Any]:
        """Fetch detailed information about a specific trace.

        Parameters
        ----------
        trace_id:
            UUID of the trace.
        """
        return self._client.retry.run(
            lambda: self._client.transport.request("GET", f"/traces/{trace_id}")
        )

    def session_timeline(
        self,
        session_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return the paginated event timeline for a session.

        Parameters
        ----------
        session_id:
            UUID of the session.
        cursor:
            Pagination cursor from a previous response.
        limit:
            Max events to return (1–500, default 100).

        Returns
        -------
        dict
            Paginated response with ``items`` and optional ``next_cursor``.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/sessions/{session_id}/timeline", params=params
            )
        )
