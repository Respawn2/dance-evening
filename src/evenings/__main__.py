"""Entry point: python -m evenings."""

import uvicorn

from evenings.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "evenings.app:create_app",
        factory=True,
        host="0.0.0.0",  # inside a container the server must accept any address
        port=settings.port,
        log_config=None,  # logging is configured by structlog; no second setup
    )


if __name__ == "__main__":
    main()
