"""
blocklog.api.replay
~~~~~~~~~~~~~~~~~~~
Layer 2 client for forensic replay sessions.

Available via ``client.replay.*``.

Backend endpoints
-----------------
- POST  /api/v1/forensics/replays
- GET   /api/v1/forensics/replays/{id}
- GET   /api/v1/forensics/replays/{id}/timeline
- GET   /api/v1/forensics/replays/{id}/root-cause
- GET   /api/v1/forensics/replays/{id}/causal-graph
- GET   /api/v1/forensics/replays/{id}/staleness
- GET   /api/v1/forensics/replays/{id}/divergence
- POST  /api/v1/forensics/replays/{id}/counterfactuals
- POST  /api/v1/forensics/compare
- GET   /api/v1/forensics/compare/{id}
- POST  /api/v1/replay/sessions  (simple replay)
- GET   /api/v1/replay/sessions/{id}
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blocklog.client import BlocklogClient


class ReplaySession:
    """A forensic replay session.

    Wraps a backend replay session and provides lazy-loaded access to
    all sub-resources: timeline, root cause, causal graph, staleness
    heatmap, divergences, and counterfactuals.

    Obtained from ``client.replay.create()`` or ``blocklog.replay()``.

    Examples
    --------
    >>> session = client.replay.create(trace_id="trace-abc")
    >>> session.timeline()
    >>> session.root_cause()
    >>> session.compare(other_trace_id="trace-def")
    """

    def __init__(self, data: dict[str, Any], client: ReplayClient) -> None:
        self._data = data
        self._client = client
        self.id: str = str(data.get("id", data.get("replay_session_id", "")))

    # -- Raw data --

    @property
    def raw(self) -> dict[str, Any]:
        """The full raw session data from the backend."""
        return self._data

    # -- Sub-resource accessors --

    def timeline(self) -> list[dict[str, Any]]:
        """Return the chronological event timeline for this replay.

        Returns
        -------
        list[dict]
            Ordered list of timeline items.
        """
        return self._client.timeline(self.id)

    def root_cause(self) -> dict[str, Any]:
        """Perform root-cause analysis on this replay.

        The backend applies heuristics to detect:
        - Stale context / data freshness violations
        - Policy violations (authorization denied)
        - Integrity failures (receipt status anomalies)

        Returns
        -------
        dict
            Keys: ``detected``, ``root_cause_type``, ``description``,
            ``confidence``, ``remediation``.
        """
        return self._client.root_cause(self.id)

    def causal_graph(self) -> dict[str, Any]:
        """Return the causal graph (nodes + edges) for this replay.

        Useful for visualising the chain of causality across agents,
        tools, decisions, and execution receipts.

        Returns
        -------
        dict
            Keys: ``nodes``, ``edges``.
        """
        return self._client.causal_graph(self.id)

    def staleness(self) -> dict[str, Any]:
        """Return the staleness heatmap for data sources used in this replay.

        Returns
        -------
        dict
            Keys: ``overall_staleness_rating``, ``findings``.
        """
        return self._client.staleness(self.id)

    def divergence(self) -> list[dict[str, Any]]:
        """Return divergence analysis results for this replay.

        Returns
        -------
        list[dict]
            List of detected divergence events.
        """
        return self._client.divergence(self.id)

    def counterfactual(
        self,
        token_id: str,
        *,
        modified_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Run a counterfactual (what-if) simulation on this replay.

        Parameters
        ----------
        token_id:
            The execution token ID to simulate against.
        modified_inputs:
            Dict of input fields to override in the simulation.

        Returns
        -------
        dict
            Counterfactual analysis result.
        """
        return self._client.counterfactual(
            self.id, token_id=token_id, modified_inputs=modified_inputs
        )

    def compare(self, other_trace_id: str) -> dict[str, Any]:
        """Compare this replay session against another trace.

        Creates a new replay session for ``other_trace_id``, then runs a
        forensic comparison against this session.

        Parameters
        ----------
        other_trace_id:
            Trace ID of the session to compare against.

        Returns
        -------
        dict
            Comparison result including ``differences`` list.
        """
        other = self._client.create(trace_id=other_trace_id)
        return self._client.compare(self.id, other.id)

    def __repr__(self) -> str:
        return f"<ReplaySession id={self.id!r}>"


class ReplayClient:
    """Manage forensic replay sessions.

    Accessed as ``client.replay``.

    Examples
    --------
    >>> session = client.replay.create(trace_id="trace-abc")
    >>> session.root_cause()
    >>> session.compare("trace-def")
    """

    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    def create(
        self,
        trace_id: str,
        *,
        token_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReplaySession:
        """Create a forensic replay session for a given trace.

        Parameters
        ----------
        trace_id:
            The trace to replay.
        token_id:
            Execution token ID to bind to this session.
        metadata:
            Extra metadata for the replay session.

        Returns
        -------
        ReplaySession
            A session handle with access to all forensic sub-resources.
        """
        payload: dict[str, Any] = {"trace_id": trace_id}
        if token_id is not None:
            payload["token_id"] = token_id
        if metadata is not None:
            payload["metadata"] = metadata

        data = self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", "/forensics/replays", json=payload
            )
        )
        return ReplaySession(data, self)

    def get(self, replay_session_id: str) -> ReplaySession:
        """Fetch an existing replay session by ID."""
        data = self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/replays/{replay_session_id}"
            )
        )
        return ReplaySession(data, self)

    def timeline(self, replay_session_id: str) -> list[dict[str, Any]]:
        """Return the event timeline for a replay session."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/replays/{replay_session_id}/timeline"
            )
        )

    def root_cause(self, replay_session_id: str) -> dict[str, Any]:
        """Run root-cause analysis on a replay session."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/replays/{replay_session_id}/root-cause"
            )
        )

    def causal_graph(self, replay_session_id: str) -> dict[str, Any]:
        """Return the causal graph for a replay session."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/replays/{replay_session_id}/causal-graph"
            )
        )

    def staleness(self, replay_session_id: str) -> dict[str, Any]:
        """Return staleness heatmap for a replay session."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/replays/{replay_session_id}/staleness"
            )
        )

    def divergence(self, replay_session_id: str) -> list[dict[str, Any]]:
        """Return divergence analysis for a replay session."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/replays/{replay_session_id}/divergence"
            )
        )

    def counterfactual(
        self,
        replay_session_id: str,
        *,
        token_id: str,
        modified_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Run a counterfactual simulation."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST",
                f"/forensics/replays/{replay_session_id}/counterfactuals",
                json={"token_id": token_id, "modified_inputs": modified_inputs},
            )
        )

    def compare(
        self,
        baseline_session_id: str,
        candidate_session_id: str,
    ) -> dict[str, Any]:
        """Compare two replay sessions and return a diff of differences."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST",
                "/forensics/compare",
                json={
                    "baseline_session_id": baseline_session_id,
                    "candidate_session_id": candidate_session_id,
                },
            )
        )

    def get_comparison(self, comparison_id: str) -> dict[str, Any]:
        """Retrieve a previously computed replay comparison."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/forensics/compare/{comparison_id}"
            )
        )
