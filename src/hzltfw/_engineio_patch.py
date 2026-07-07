"""Compatibility patch for an Engine.IO ASGI disconnect edge case."""

from __future__ import annotations

import functools
from typing import Any

import engineio

_PATCH_MARKER = "_hzltfw_asgi_disconnect_patch"


def apply_engineio_asgi_disconnect_patch() -> None:
    """Ignore a known Engine.IO crash for disconnected ASGI requests."""
    current_handle_request = engineio.AsyncServer.handle_request
    if getattr(current_handle_request, _PATCH_MARKER, False):
        return

    @functools.wraps(current_handle_request)
    async def patched_handle_request(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return await current_handle_request(self, *args, **kwargs)
        except KeyError as exc:
            if exc.args == ("REQUEST_METHOD",):
                return None
            raise

    setattr(patched_handle_request, _PATCH_MARKER, True)
    engineio.AsyncServer.handle_request = patched_handle_request
