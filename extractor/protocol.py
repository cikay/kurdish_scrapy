from typing import Protocol, Any


class ContentExtractorProtocol(Protocol):
    def extract(self, html, url) -> Any:
        pass
