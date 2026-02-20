from typing import Protocol, Any


class ContentExtractorProtocol(Protocol):
    def extract(html, url) -> Any:
        pass
