from __future__ import annotations

from typing import TYPE_CHECKING, Any

from blocklog.models.teams import (
    NotifyTestResponse,
    Team,
    TeamMember,
    TeamRole,
    normalize_team,
    normalize_team_member,
    to_backend_role,
)

if TYPE_CHECKING:
    from blocklog.async_client import AsyncBlocklogClient
    from blocklog.client import BlocklogClient


class TeamMembersClient:
    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    def list(self, team_id: str) -> list[TeamMember]:
        payload = self._client.retry.run(
            lambda: self._client.transport.request("GET", f"/teams/{team_id}/members")
        )
        return [normalize_team_member(item) for item in (payload or [])]

    def add(
        self,
        team_id: str,
        *,
        user_id: str | None = None,
        email: str | None = None,
        role: TeamRole | None = None,
        is_on_call: bool = False,
        notification_channels: list[str] | None = None,
    ) -> TeamMember:
        payload: dict[str, Any] = {
            "is_on_call": is_on_call,
            "notification_channels": notification_channels or [],
        }
        if user_id is not None:
            payload["user_id"] = int(user_id)
        if email is not None:
            payload["email"] = email
        if role is not None:
            payload["role"] = to_backend_role(role).value

        response = self._client.transport.request(
            "POST", f"/teams/{team_id}/members", json=payload
        )
        return normalize_team_member(response)

    def update(
        self,
        team_id: str,
        member_id: str,
        *,
        role: TeamRole | None = None,
        is_on_call: bool | None = None,
        notification_channels: list[str] | None = None,
    ) -> TeamMember:
        payload: dict[str, Any] = {}
        if role is not None:
            payload["role"] = to_backend_role(role).value
        if is_on_call is not None:
            payload["is_on_call"] = is_on_call
        if notification_channels is not None:
            payload["notification_channels"] = notification_channels

        response = self._client.transport.request(
            "PATCH",
            f"/teams/{team_id}/members/{member_id}",
            json=payload,
        )
        return normalize_team_member(response)

    def remove(self, team_id: str, member_id: str) -> None:
        self._client.transport.request(
            "DELETE", f"/teams/{team_id}/members/{member_id}"
        )


class TeamsClient:
    def __init__(self, client: BlocklogClient) -> None:
        self._client = client
        self.members = TeamMembersClient(client)

    def list(self) -> list[Team]:
        payload = self._client.retry.run(
            lambda: self._client.transport.request("GET", "/teams")
        )
        return [normalize_team(item) for item in (payload or [])]

    def get(self, team_id: str) -> Team:
        payload = self._client.retry.run(
            lambda: self._client.transport.request("GET", f"/teams/{team_id}")
        )
        return normalize_team(payload)

    def create(self, **payload) -> Team:
        return normalize_team(
            self._client.transport.request("POST", "/teams", json=payload)
        )

    def update(self, team_id: str, **payload) -> Team:
        return normalize_team(
            self._client.transport.request("PATCH", f"/teams/{team_id}", json=payload)
        )

    def delete(self, team_id: str) -> None:
        self._client.transport.request("DELETE", f"/teams/{team_id}")

    def notify_test(self, team_id: str) -> NotifyTestResponse:
        payload = self._client.transport.request(
            "POST", f"/teams/{team_id}/notify-test", json={}
        )
        return NotifyTestResponse.model_validate(payload)


class AsyncTeamMembersClient:
    def __init__(self, client: AsyncBlocklogClient) -> None:
        self._client = client

    async def list(self, team_id: str) -> list[TeamMember]:
        payload = await self._client.transport.request(
            "GET", f"/teams/{team_id}/members"
        )
        return [normalize_team_member(item) for item in (payload or [])]

    async def add(
        self,
        team_id: str,
        *,
        user_id: str | None = None,
        email: str | None = None,
        role: TeamRole | None = None,
        is_on_call: bool = False,
        notification_channels: list[str] | None = None,
    ) -> TeamMember:
        payload: dict[str, Any] = {
            "is_on_call": is_on_call,
            "notification_channels": notification_channels or [],
        }
        if user_id is not None:
            payload["user_id"] = int(user_id)
        if email is not None:
            payload["email"] = email
        if role is not None:
            payload["role"] = to_backend_role(role).value

        response = await self._client.transport.request(
            "POST", f"/teams/{team_id}/members", json=payload
        )
        return normalize_team_member(response)

    async def update(
        self,
        team_id: str,
        member_id: str,
        *,
        role: TeamRole | None = None,
        is_on_call: bool | None = None,
        notification_channels: list[str] | None = None,
    ) -> TeamMember:
        payload: dict[str, Any] = {}
        if role is not None:
            payload["role"] = to_backend_role(role).value
        if is_on_call is not None:
            payload["is_on_call"] = is_on_call
        if notification_channels is not None:
            payload["notification_channels"] = notification_channels

        response = await self._client.transport.request(
            "PATCH",
            f"/teams/{team_id}/members/{member_id}",
            json=payload,
        )
        return normalize_team_member(response)

    async def remove(self, team_id: str, member_id: str) -> None:
        await self._client.transport.request(
            "DELETE", f"/teams/{team_id}/members/{member_id}"
        )


class AsyncTeamsClient:
    def __init__(self, client: AsyncBlocklogClient) -> None:
        self._client = client
        self.members = AsyncTeamMembersClient(client)

    async def list(self) -> list[Team]:
        payload = await self._client.transport.request("GET", "/teams")
        return [normalize_team(item) for item in (payload or [])]

    async def get(self, team_id: str) -> Team:
        payload = await self._client.transport.request("GET", f"/teams/{team_id}")
        return normalize_team(payload)

    async def create(self, **payload) -> Team:
        response = await self._client.transport.request("POST", "/teams", json=payload)
        return normalize_team(response)

    async def update(self, team_id: str, **payload) -> Team:
        response = await self._client.transport.request(
            "PATCH", f"/teams/{team_id}", json=payload
        )
        return normalize_team(response)

    async def delete(self, team_id: str) -> None:
        await self._client.transport.request("DELETE", f"/teams/{team_id}")

    async def notify_test(self, team_id: str) -> NotifyTestResponse:
        payload = await self._client.transport.request(
            "POST", f"/teams/{team_id}/notify-test", json={}
        )
        return NotifyTestResponse.model_validate(payload)
