"""
blocklog.approval
~~~~~~~~~~~~~~~~~
Module-level namespace for human approval workflows.

Usage (Layer 1)::

    from blocklog import approval

    approval.request(
        decision_id="dec_abc123",
        reason="Trade exceeds $500k threshold",
        reviewer="risk-team@fund.com",
    )

    approval.reject(reviewer="alice@fund.com", reason="Insufficient data")

    approval.escalate(
        from_reviewer="alice@fund.com",
        to_reviewer="head-of-risk@fund.com",
        reason="Requires executive sign-off",
    )

    trail = approval.audit_trail()
"""

from __future__ import annotations

from typing import Any


def request(
    decision_id: str | None = None,
    *,
    reason: str,
    reviewer: str | None = None,
    log_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Request human approval for a decision.

    This is a **non-blocking** call — it registers the approval request
    and triggers configured webhooks/notifications, then returns
    immediately.

    Parameters
    ----------
    decision_id:
        UUID of the decision requiring approval.
    reason:
        Human-readable explanation of why approval is needed.
    reviewer:
        Email / identifier of the intended reviewer.
    log_id:
        UUID of a specific log entry, if approval is on a log rather
        than a top-level decision.
    metadata:
        Extra context to store with the approval request.
    """
    from blocklog._global import get_client

    return get_client().approval.request(
        decision_id=decision_id,
        reason=reason,
        reviewer=reviewer,
        log_id=log_id,
        metadata=metadata,
    )


def reject(
    reviewer: str, *, reason: str, decision_id: str | None = None
) -> dict[str, Any]:
    """Record that a reviewer has rejected a decision.

    Parameters
    ----------
    reviewer:
        Identity of the person rejecting.
    reason:
        Explanation for the rejection.
    decision_id:
        Optional reference to the decision being rejected.
    """
    from blocklog._global import get_client

    return get_client().approval.reject(
        reviewer=reviewer, reason=reason, decision_id=decision_id
    )


def escalate(
    from_reviewer: str,
    to_reviewer: str,
    *,
    reason: str,
) -> dict[str, Any]:
    """Escalate an approval request to a different reviewer.

    Parameters
    ----------
    from_reviewer:
        Current reviewer escalating the decision.
    to_reviewer:
        Target reviewer who should take over.
    reason:
        Explanation for the escalation.
    """
    from blocklog._global import get_client

    return get_client().approval.escalate(
        from_reviewer=from_reviewer,
        to_reviewer=to_reviewer,
        reason=reason,
    )


def list_overrides() -> list[dict[str, Any]]:
    """Return all HITL override records for the company."""
    from blocklog._global import get_client

    return get_client().approval.list_overrides()


def audit_trail() -> list[dict[str, Any]]:
    """Return the full HITL audit trail in reverse-chronological order."""
    from blocklog._global import get_client

    return get_client().approval.audit_trail()
