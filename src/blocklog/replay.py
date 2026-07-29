"""
blocklog.replay
~~~~~~~~~~~~~~~
Module-level factory for forensic replay sessions.

Usage (Layer 1)::

    import blocklog

    session = blocklog.replay("trace-abc-123")

    # Explore what happened
    timeline   = session.timeline()
    root_cause = session.root_cause()
    graph      = session.causal_graph()
    stale      = session.staleness()

    # What would have happened differently?
    cf = session.counterfactual(token_id="tok_x", modified_inputs={"price": 400})

    # Compare against another run
    diff = session.compare(other_trace_id="trace-def-456")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blocklog.api.replay import ReplaySession


def replay(
    trace_id: str,
    *,
    token_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ReplaySession:
    """Create a forensic replay session for a trace.

    Parameters
    ----------
    trace_id:
        The trace to replay.  All events associated with this trace will
        be reconstructed into a timeline, causal graph, and analysis.
    token_id:
        Execution token ID to bind to the session (required for
        counterfactual simulations).
    metadata:
        Optional extra metadata for the replay session.

    Returns
    -------
    ReplaySession
        A session handle with methods for timeline, root_cause,
        causal_graph, staleness, divergence, counterfactual, and compare.

    Examples
    --------
    >>> session = blocklog.replay("trace-abc")
    >>> cause = session.root_cause()
    >>> print(cause["description"])
    """
    from blocklog._global import get_client

    return get_client().replay.create(
        trace_id=trace_id, token_id=token_id, metadata=metadata
    )
