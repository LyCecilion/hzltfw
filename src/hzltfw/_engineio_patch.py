"""Monkey-patch engineio ASGI handler to prevent KeyError on unexpected events.

Root cause:
  engineio's ASGI translate_request() calls receive() and only handles
  'http.request' and 'websocket.connect' events. Any other event type
  (e.g. 'http.disconnect' from a dropped connection) causes it to return
  an empty dict {}. Downstream, handle_request() then crashes with:
    KeyError: 'REQUEST_METHOD'

This patch wraps handle_request to catch that specific KeyError gracefully.
"""

from __future__ import annotations

import functools

import engineio


def apply() -> None:
    """Apply the monkey-patch to engineio's AsyncServer."""
    _original = engineio.AsyncServer.handle_request

    @functools.wraps(_original)
    async def _patched_handle_request(self, *args, **kwargs):
        try:
            return await _original(self, *args, **kwargs)
        except KeyError as exc:
            key = exc.args[0] if exc.args else ""
            if key == "REQUEST_METHOD":
                # translate_request returned {} — typically from http.disconnect
                # or another non-standard ASGI event. Nothing to handle here.
                return None
            raise

    engineio.AsyncServer.handle_request = _patched_handle_request
