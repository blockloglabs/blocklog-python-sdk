"""
blocklog.api.incidents
~~~~~~~~~~~~~~~~~~~~~~
Layer 2 client for the full Incident lifecycle.

Available via ``client.incidents.*``.

Backend endpoints
-----------------
- GET    /api/v1/incidents
- POST   /api/v1/incidents
- GET    /api/v1/incidents/{id}
- PATCH  /api/v1/incidents/{id}
- POST   /api/v1/incidents/{id}/assign
- POST   /api/v1/incidents/{id}/resolve
- POST   /api/v1/incidents/{id}/close
- POST   /api/v1/incidents/{id}/report
- GET    /api/v1/incidents/{id}/report
- GET    /api/v1/incidents/{id}/annotations
- POST   /api/v1/incidents/{id}/annotations
- GET    /api/v1/incidents/{id}/workspace
- POST   /api/v1/incidents/{id}/workspace
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blocklog.client import BlocklogClient


class IncidentHandle:
    """A live handle to a specific incident returned by ``create()`` or ``get()``.

    Provides a fluent, object-oriented interface to the incident lifecycle.

    Examples
    --------
    >>> inc = client.incidents.create(title="Anomalous SELL on AAPL", trace_id="...")
    >>> inc.assign("alice@fund.com")
    >>> inc.annotate("Reviewing related decisions from the same session")
    >>> inc.resolve(summary="False positive — model weights corrected")
    """

    def __init__(self, data: dict[str, Any], client: IncidentsClient) -> None:
        self._data = data
        self._client = client
        self.id: str = str(data.get("id", ""))

    # -- Convenience accessors --

    @property
    def title(self) -> str:
        return self._data.get("title", "")

    @property
    def status(self) -> str:
        return self._data.get("status", "")

    @property
    def severity(self) -> str:
        return self._data.get("severity", "")

    # -- Lifecycle methods --

    def assign(self, assignee: str, *, notes: str | None = None) -> IncidentHandle:
        """Assign this incident to a team member."""
        self._data = self._client.assign(self.id, assignee=assignee, notes=notes)
        return self

    def resolve(
        self,
        summary: str,
        *,
        root_cause: Any = None,
        remediation_actions: Any = None,
    ) -> IncidentHandle:
        """Mark this incident as resolved."""
        self._data = self._client.resolve(
            self.id,
            summary=summary,
            root_cause=root_cause,
            remediation_actions=remediation_actions,
        )
        return self

    def close(
        self, *, notes: str = "", approval_status: str = "approved"
    ) -> IncidentHandle:
        """Close this incident."""
        self._data = self._client.close(
            self.id, notes=notes, approval_status=approval_status
        )
        return self

    def annotate(self, text: str, *, author: str | None = None) -> dict[str, Any]:
        """Add an annotation (comment/note) to this incident."""
        return self._client.annotate(self.id, text=text, author=author)

    def add_workspace_item(
        self,
        item_type: str,
        reference_id: str,
        *,
        label: str | None = None,
    ) -> dict[str, Any]:
        """Add a workspace item (trace, decision, log) to this incident."""
        return self._client.add_workspace_item(
            self.id, item_type=item_type, reference_id=reference_id, label=label
        )

    def report(self) -> dict[str, Any]:
        """Generate (or retrieve) the investigation report for this incident."""
        return self._client.report(self.id)

    def annotations(self) -> list[dict[str, Any]]:
        """Return all annotations on this incident."""
        return self._client.annotations(self.id)

    def workspace(self) -> list[dict[str, Any]]:
        """Return workspace items pinned to this incident."""
        return self._client.workspace_items(self.id)

    def refresh(self) -> IncidentHandle:
        """Re-fetch the latest state from the backend."""
        self._data = self._client.get(self.id)._data
        return self

    def __repr__(self) -> str:
        return f"<IncidentHandle id={self.id!r} status={self.status!r} severity={self.severity!r}>"


class IncidentsClient:
    """Manage the full incident lifecycle.

    Accessed as ``client.incidents``.

    Examples
    --------
    >>> inc = client.incidents.create(
    ...     title="Unexpected SELL on AAPL",
    ...     trace_id="trace-abc",
    ...     severity="high",
    ... )
    >>> inc.assign("alice@fund.com")
    >>> inc.resolve(summary="False positive — corrected")
    """

    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    def create(
        self,
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
            A live handle to the created incident.
        """
        payload: dict[str, Any] = {"title": title, "severity": severity}
        if trace_id is not None:
            payload["trace_id"] = trace_id
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata

        data = self._client.retry.run(
            lambda: self._client.transport.request("POST", "/incidents", json=payload)
        )
        return IncidentHandle(data, self)

    def get(self, incident_id: str) -> IncidentHandle:
        """Fetch a single incident by ID."""
        data = self._client.retry.run(
            lambda: self._client.transport.request("GET", f"/incidents/{incident_id}")
        )
        return IncidentHandle(data, self)

    def list(self) -> list[IncidentHandle]:
        """List all incidents for the authenticated company."""
        items = self._client.retry.run(
            lambda: self._client.transport.request("GET", "/incidents")
        )
        return [IncidentHandle(item, self) for item in (items or [])]

    def update(self, incident_id: str, **fields: Any) -> dict[str, Any]:
        """Partially update an incident's fields."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "PATCH", f"/incidents/{incident_id}", json=fields
            )
        )

    def assign(
        self, incident_id: str, *, assignee: str, notes: str | None = None
    ) -> dict[str, Any]:
        """Assign an incident to a reviewer."""
        payload: dict[str, Any] = {"assignee": assignee}
        if notes:
            payload["notes"] = notes
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", f"/incidents/{incident_id}/assign", json=payload
            )
        )

    def resolve(
        self,
        incident_id: str,
        *,
        summary: str,
        root_cause: Any = None,
        remediation_actions: Any = None,
    ) -> dict[str, Any]:
        """Mark an incident as resolved."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST",
                f"/incidents/{incident_id}/resolve",
                json={
                    "resolution_summary": summary,
                    "root_cause": root_cause,
                    "remediation_actions": remediation_actions,
                },
            )
        )

    def close(
        self,
        incident_id: str,
        *,
        notes: str = "",
        approval_status: str = "approved",
    ) -> dict[str, Any]:
        """Close an incident."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST",
                f"/incidents/{incident_id}/close",
                json={
                    "closure_notes": notes,
                    "approval_status": approval_status,
                },
            )
        )

    def report(self, incident_id: str) -> dict[str, Any]:
        """Generate the investigation report for an incident."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", f"/incidents/{incident_id}/report", json={}
            )
        )

    def get_report(self, incident_id: str) -> dict[str, Any]:
        """Retrieve a previously generated investigation report."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/incidents/{incident_id}/report"
            )
        )

    def annotate(
        self,
        incident_id: str,
        *,
        text: str,
        author: str | None = None,
    ) -> dict[str, Any]:
        """Add a text annotation to an incident."""
        payload: dict[str, Any] = {"text": text}
        if author:
            payload["author"] = author
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", f"/incidents/{incident_id}/annotations", json=payload
            )
        )

    def annotations(self, incident_id: str) -> list[dict[str, Any]]:
        """Return all annotations on an incident."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/incidents/{incident_id}/annotations"
            )
        )

    def add_workspace_item(
        self,
        incident_id: str,
        *,
        item_type: str,
        reference_id: str,
        label: str | None = None,
    ) -> dict[str, Any]:
        """Pin a workspace item (trace, decision, log) to an incident."""
        payload: dict[str, Any] = {"item_type": item_type, "reference_id": reference_id}
        if label:
            payload["label"] = label
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", f"/incidents/{incident_id}/workspace", json=payload
            )
        )

    def workspace_items(self, incident_id: str) -> list[dict[str, Any]]:
        """Return workspace items pinned to an incident."""
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/incidents/{incident_id}/workspace"
            )
        )
