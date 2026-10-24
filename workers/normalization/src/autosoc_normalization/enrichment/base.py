from abc import ABC, abstractmethod
from typing import Optional
from autosoc_schemas.events import NormalizedSecurityEvent, EnrichedSecurityEvent

class BaseEnricher(ABC):
    @property
    @abstractmethod
    def enricher_name(self) -> str:
        pass
        
    @abstractmethod
    async def enrich(self, event: NormalizedSecurityEvent, enriched: EnrichedSecurityEvent) -> None:
        """
        Mutates the `enriched` event in place with additional contextual data.
        Must not raise exceptions that break the pipeline. Failures must be isolated.
        """
        pass
