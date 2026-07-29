from __future__ import annotations

from blocklog.api.auth import AsyncAuthClient
from blocklog.api.teams import AsyncTeamsClient
from blocklog.client import BlocklogClient
from blocklog.config import BlocklogConfig
from blocklog.models.responses import IngestResponse
from blocklog.transport.httpx_async import AsyncTransport


class AsyncBlocklogClient(BlocklogClient):
    def __init__(self, config: BlocklogConfig | None = None, **kwargs) -> None:
        super().__init__(config, **kwargs)
        self.transport = AsyncTransport(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            access_token=self.config.access_token,
            timeout=self.config.timeout,
            debug=self.config.debug,
        )
        self.teams = AsyncTeamsClient(self)
        self.auth = AsyncAuthClient(self)

    async def event(self, event_type: str, payload: dict, **kwargs) -> IngestResponse:
        envelope = self._build_event(event_type=event_type, payload=payload, **kwargs)
        result = await self.transport.request(
            "POST", "/logs", json=self._serialize(envelope)
        )
        return IngestResponse.model_validate(result)

    async def flush(self, *, batch=None):
        batch = batch or self.buffer.flush()
        if not batch:
            return {"ingested": 0, "log_ids": []}
        payload = {"logs": [self._serialize(item) for item in batch]}
        return await self.transport.request("POST", "/logs/batch", json=payload)
