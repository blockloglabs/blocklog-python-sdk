"""
blocklog.incident
~~~~~~~~~~~~~~~~~
Module-level namespace for incident management.

Usage (Layer 1)::

    from blocklog import incident

    inc = incident.create(
        title="Anomalous BUY signal on TSLA",
        trace_id="trace-abc",
        severity="high",
    )

    inc.assign("alice@fund.com")
    inc.annotate("Reviewing related decisions from the same session")
    inc.resolve(summary="False positive — model weights corrected")
    inc.close()

    report = inc.report()
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blocklog.api.incidents import IncidentHandle


def create(
    title: str,
    *,
    trace_id: str | None = None,
    severity: str = "medium",
    description: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> IncidentHandle:
    """Create a new incident.

    Parameters
    ----------
    title:
        Short title describing the incident.
    trace_id:
        UUID of the trace associated with this incident.
    severity:
        ``"low"``, ``"medium"``, ``"high"``, or ``"critical"``.
    description:
        Longer free-text description.
    metadata:
        Arbitrary extra fields.

    Returns
    -------
    IncidentHandle
        A live handle with access to the full lifecycle (assign, resolve,
        close, annotate, report, etc.).

    Examples
    --------
    >>> inc = blocklog.incident.create(
    ...     title="Unexpected SELL on AAPL",
    ...     trace_id="trace-abc",
    ...     severity="high",
    ... )
    >>> inc.assign("alice@fund.com")
    >>> inc.resolve(summary="False positive")
    """
    from blocklog._global import get_client

    return get_client().incidents.create(
        title=title,
        trace_id=trace_id,
        severity=severity,
        description=description,
        metadata=metadata,
    )


def get(incident_id: str) -> IncidentHandle:
    """Fetch an existing incident by ID."""
    from blocklog._global import get_client

    return get_client().incidents.get(incident_id)


def list_all() -> list[IncidentHandle]:
    """List all incidents for the authenticated company."""
    from blocklog._global import get_client

    return get_client().incidents.list()
