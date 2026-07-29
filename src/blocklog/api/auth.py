from __future__ import annotations

from typing import TYPE_CHECKING

from blocklog.models.auth import LoginResponse, SignupResponse, TokenResponse, User
from blocklog.models.teams import normalize_team
from blocklog.team_utils import get_primary_team

if TYPE_CHECKING:
    from blocklog.async_client import AsyncBlocklogClient
    from blocklog.client import BlocklogClient


class AuthClient:
    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    def me(self) -> User:
        payload = self._client.transport.request("GET", "/auth/me")
        return User.model_validate(payload)

    def signup(self, **payload) -> SignupResponse:
        token_response = TokenResponse.model_validate(
            self._client.transport.request(
                "POST", "/auth/signup", json=payload, skip_auth=True
            )
        )
        if token_response.team_id is None:
            raise RuntimeError(
                "Signup succeeded but no team was returned by the backend."
            )

        user = User.model_validate(
            self._client.transport.request(
                "GET",
                "/auth/me",
                token_override=token_response.access_token,
            )
        )
        team = normalize_team(
            self._client.transport.request(
                "GET",
                f"/teams/{token_response.team_id}",
                token_override=token_response.access_token,
            )
        )
        return SignupResponse(
            user=user,
            token=token_response.access_token,
            expires_in=token_response.expires_in,
            team=team,
        )

    def login(self, email: str, password: str) -> LoginResponse:
        token_response = TokenResponse.model_validate(
            self._client.transport.request(
                "POST",
                "/auth/login",
                json={"email": email, "password": password},
                skip_auth=True,
            )
        )
        user = User.model_validate(
            self._client.transport.request(
                "GET",
                "/auth/me",
                token_override=token_response.access_token,
            )
        )
        teams = self._client.transport.request(
            "GET",
            "/teams",
            token_override=token_response.access_token,
        )
        primary_team = get_primary_team(
            [normalize_team(item) for item in (teams or [])]
        )
        return LoginResponse(
            user=user,
            token=token_response.access_token,
            expires_in=token_response.expires_in,
            team=primary_team,
        )


class AsyncAuthClient:
    def __init__(self, client: AsyncBlocklogClient) -> None:
        self._client = client

    async def me(self) -> User:
        payload = await self._client.transport.request("GET", "/auth/me")
        return User.model_validate(payload)

    async def signup(self, **payload) -> SignupResponse:
        token_response = TokenResponse.model_validate(
            await self._client.transport.request(
                "POST", "/auth/signup", json=payload, skip_auth=True
            )
        )
        if token_response.team_id is None:
            raise RuntimeError(
                "Signup succeeded but no team was returned by the backend."
            )

        user = User.model_validate(
            await self._client.transport.request(
                "GET",
                "/auth/me",
                token_override=token_response.access_token,
            )
        )
        team = normalize_team(
            await self._client.transport.request(
                "GET",
                f"/teams/{token_response.team_id}",
                token_override=token_response.access_token,
            )
        )
        return SignupResponse(
            user=user,
            token=token_response.access_token,
            expires_in=token_response.expires_in,
            team=team,
        )

    async def login(self, email: str, password: str) -> LoginResponse:
        token_response = TokenResponse.model_validate(
            await self._client.transport.request(
                "POST",
                "/auth/login",
                json={"email": email, "password": password},
                skip_auth=True,
            )
        )
        user = User.model_validate(
            await self._client.transport.request(
                "GET",
                "/auth/me",
                token_override=token_response.access_token,
            )
        )
        teams = await self._client.transport.request(
            "GET",
            "/teams",
            token_override=token_response.access_token,
        )
        primary_team = get_primary_team(
            [normalize_team(item) for item in (teams or [])]
        )
        return LoginResponse(
            user=user,
            token=token_response.access_token,
            expires_in=token_response.expires_in,
            team=primary_team,
        )
