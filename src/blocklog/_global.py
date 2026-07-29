from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from blocklog.client import BlocklogClient

_global_client: Optional["BlocklogClient"] = None


def get_client() -> "BlocklogClient":
    if _global_client is None:
        raise RuntimeError(
            "Blocklog API key not configured.\n\n"
            "Use:\n"
            "from blocklog import init\n"
            'init(api_key="YOUR_API_KEY")'
        )
    return _global_client


def set_client(client: "BlocklogClient") -> None:
    global _global_client
    _global_client = client
