from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def from_timestamp(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=UTC)
