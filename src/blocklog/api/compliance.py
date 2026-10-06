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
        title: str | None = None,
        report_kind: str = "design_partner_readiness",
        scope_type: str | None = None,
        framework: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a compliance report."""
        effective_scope = scope_type or ("trace" if trace_id is not None else "company")
        report_title = title or f"Compliance Report - {framework or 'General'}"
        payload: dict[str, Any] = {
            "title": report_title,
            "report_kind": report_kind,
            "scope_type": effective_scope,
        }
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
        recipients: list[str] | None = None,
        recipient_email: str | None = None,
        expires_in: int | None = None,
        expires_in_days: int | None = None,
        note: str | None = None,
        create_auditor_api_key: bool = False,
    ) -> dict[str, Any]:
        """Create a shareable link for a compliance report."""
        target_recipients = recipients or (
            [] if not recipient_email else [recipient_email]
        )
        payload: dict[str, Any] = {
            "recipients": target_recipients,
            "create_auditor_api_key": create_auditor_api_key,
        }
        if expires_in_days is not None:
            payload["expires_in_days"] = expires_in_days
        elif expires_in is not None:
            payload["expires_in"] = expires_in
            payload["expires_in_days"] = max(1, expires_in // 86400)
        if note is not None:
            payload["note"] = note
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
