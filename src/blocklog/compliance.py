"""
blocklog.compliance
~~~~~~~~~~~~~~~~~~~
Module-level namespace for compliance report generation.

Usage (Layer 1)::

    import blocklog

    report = blocklog.compliance.generate(
        trace_id="trace-abc",
        framework="SOC2",
    )
    print(report["id"])

    dashboard = blocklog.compliance.dashboard()
    reports   = blocklog.compliance.list()
    share_url = blocklog.compliance.share(report["id"], expires_in=86400)
"""

from __future__ import annotations

from typing import Any


def generate(
    trace_id: str | None = None,
    *,
    title: str | None = None,
    report_kind: str = "design_partner_readiness",
    scope_type: str | None = None,
    framework: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    metadata: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate a compliance report."""
    from blocklog._global import get_client

    return get_client().compliance.generate(
        trace_id=trace_id,
        title=title,
        report_kind=report_kind,
        scope_type=scope_type,
        framework=framework,
        date_from=date_from,
        date_to=date_to,
        metadata=metadata,
        **kwargs,
    )


def get(report_id: str) -> dict[str, Any]:
    """Fetch a compliance report by ID."""
    from blocklog._global import get_client

    return get_client().compliance.get(report_id)


def list() -> list[dict[str, Any]]:
    """List all compliance reports for the company."""
    from blocklog._global import get_client

    return get_client().compliance.list()


def dashboard() -> dict[str, Any]:
    """Return the compliance dashboard summary."""
    from blocklog._global import get_client

    return get_client().compliance.dashboard()


def share(
    report_id: str,
    *,
    recipients: list[str] | None = None,
    recipient_email: str | None = None,
    expires_in: int | None = None,
    expires_in_days: int | None = None,
    note: str | None = None,
    create_auditor_api_key: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a shareable link for a compliance report."""
    from blocklog._global import get_client

    return get_client().compliance.share(
        report_id=report_id,
        recipients=recipients,
        recipient_email=recipient_email,
        expires_in=expires_in,
        expires_in_days=expires_in_days,
        note=note,
        create_auditor_api_key=create_auditor_api_key,
        **kwargs,
    )


def export(report_id: str, *, download: bool = False) -> dict[str, Any]:
    """Export a compliance report as JSON."""
    from blocklog._global import get_client

    return get_client().compliance.export(report_id=report_id, download=download)
