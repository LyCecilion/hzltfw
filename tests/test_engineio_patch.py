import asyncio

import engineio

from hzltfw._engineio_patch import apply_engineio_asgi_disconnect_patch


def test_engineio_patch_ignores_asgi_disconnect_request_method_error() -> None:
    apply_engineio_asgi_disconnect_patch()
    server = engineio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
    sent_messages: list[dict[str, object]] = []

    async def receive() -> dict[str, object]:
        return {"type": "http.disconnect"}

    async def send(message: dict[str, object]) -> None:
        sent_messages.append(message)

    result = asyncio.run(
        server.handle_request(
            {"type": "http", "path": "/socket.io/", "headers": []},
            receive,
            send,
        )
    )

    assert result is None
    assert sent_messages == []
