"""
blocklog.api.compliance
~~~~~~~~~~~~~~~~~~~~~~~
Layer 2 client for compliance report generation.

Available via ``client.compliance.*``.

Backend endpoints
-----------------
- GET   /api/v1/compliance/dashboard
- GET   /api/v1/compliance/reports
- POST  /api/v1/compliance/reports
- GET   /api/v1/compliance/reports/{id}
- POST  /api/v1/compliance/reports/{id}/share
- GET   /api/v1/compliance/reports/{id}/export
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blocklog.client import BlocklogClient


class ComplianceClient:
    """Generate and manage compliance reports.

    Accessed as ``client.compliance``.

    Examples
    --------
    >>> report = client.compliance.generate(
    ...     trace_id="trace-abc",
    ...     framework="SOC2",
    ... )
    >>> share_url = client.compliance.share(report["id"], expires_in=86400)
    """

    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    def generate(
        self,
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
            Scope the report to a specific trace.  Omit to generate a
            company-wide report.
        framework:
            Compliance framework (``"SOC2"``, ``"GDPR"``, ``"ISO27001"``…).
        date_from:
            ISO-8601 start of the reporting window.
        date_to:
            ISO-8601 end of the reporting window.
        metadata:
            Arbitrary extra data to embed in the report.

        Returns
        -------
        dict
            The generated report record.
        """
        payload: dict[str, Any] = {}
        if trace_id is not None:
            payload["trace_id"] = trace_id
        if framework is not None:
            payload["framework"] = framework
        if date_from is not None:
            payload["date_from"] = date_from
        if date_to is not None:
            payload["date_to"] = date_to
        if metadata is not None:
            payload["metadata"] = metadata

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", "/compliance/reports", json=payload
            )
        )

    def get(self, report_id: str) -> dict[str, Any]:
        """Fetch a compliance report by ID."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/compliance/reports/{report_id}"
            )
        )

    def list(self) -> list[dict[str, Any]]:
        """List all compliance reports for the company."""
        result = self._client.retry.run(
            lambda: self._client.transport.request("GET", "/compliance/reports")
        )
        return result.get("items", result) if isinstance(result, dict) else result

    def dashboard(self) -> dict[str, Any]:
        """Return the compliance dashboard summary."""
        return self._client.retry.run(
            lambda: self._client.transport.request("GET", "/compliance/dashboard")
        )

    def share(
        self,
        report_id: str,
        *,
        expires_in: int | None = None,
        recipient_email: str | None = None,
    ) -> dict[str, Any]:
        """Create a shareable link for a compliance report.

        Parameters
        ----------
        report_id:
            UUID of the report to share.
        expires_in:
            Seconds until the share link expires.
        recipient_email:
            Optional email of the recipient (for audit purposes).

        Returns
        -------
        dict
            Response including ``share_url`` or ``token``.
        """
        payload: dict[str, Any] = {}
        if expires_in is not None:
            payload["expires_in"] = expires_in
        if recipient_email is not None:
            payload["recipient_email"] = recipient_email

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", f"/compliance/reports/{report_id}/share", json=payload
            )
        )

    def export(
        self,
        report_id: str,
        *,
        download: bool = False,
    ) -> dict[str, Any]:
        """Export a compliance report as JSON.

        Parameters
        ----------
        report_id:
            UUID of the report to export.
        download:
            When ``True``, request the binary download stream (returned
            as raw content from the backend).
        """
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET",
                f"/compliance/reports/{report_id}/export",
                params={"download": str(download).lower()},
            )
        )
