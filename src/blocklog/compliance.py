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
    framework: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a compliance report.

    Parameters
    ----------
    trace_id:
        Scope the report to a specific trace.  Omit for a company-wide
        report.
    framework:
        Compliance framework (``"SOC2"``, ``"GDPR"``, ``"ISO27001"``…).
    date_from:
        ISO-8601 start of the reporting window.
    date_to:
        ISO-8601 end of the reporting window.
    metadata:
        Arbitrary extra data to embed in the report.
    """
    from blocklog._global import get_client

    return get_client().compliance.generate(
        trace_id=trace_id,
        framework=framework,
        date_from=date_from,
        date_to=date_to,
        metadata=metadata,
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
    expires_in: int | None = None,
    recipient_email: str | None = None,
) -> dict[str, Any]:
    """Create a shareable link for a compliance report."""
    from blocklog._global import get_client

    return get_client().compliance.share(
        report_id=report_id,
        expires_in=expires_in,
        recipient_email=recipient_email,
    )


def export(report_id: str, *, download: bool = False) -> dict[str, Any]:
    """Export a compliance report as JSON."""
    from blocklog._global import get_client

    return get_client().compliance.export(report_id=report_id, download=download)
