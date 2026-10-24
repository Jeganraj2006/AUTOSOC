import logging
from typing import Dict, Any
from autosoc_schemas.events import NormalizedSecurityEvent, EnrichedSecurityEvent
from .base import BaseEnricher

logger = logging.getLogger(__name__)

class AssetEnricher(BaseEnricher):
    @property
    def enricher_name(self) -> str:
        return "asset_enricher"
        
    async def enrich(self, event: NormalizedSecurityEvent, enriched: EnrichedSecurityEvent) -> None:
        try:
            # Dummy/Stub local logic for Asset
            # In a real environment, this queries a local Asset database
            if event.source_ip and event.source_ip.startswith("10."):
                enriched.asset_criticality = "high"
                enriched.asset_environment = "production"
            elif event.hostname and "dev" in event.hostname.lower():
                enriched.asset_environment = "development"
                enriched.asset_category = "workstation"
        except Exception as e:
            logger.warning(f"Asset enrichment failed safely: {e}")

class GeoIPEnricher(BaseEnricher):
    @property
    def enricher_name(self) -> str:
        return "geoip_enricher"
        
    async def enrich(self, event: NormalizedSecurityEvent, enriched: EnrichedSecurityEvent) -> None:
        try:
            if event.source_ip and not event.source_ip.startswith("10.") and not event.source_ip.startswith("192.168."):
                # Stub mapping
                if event.source_ip.startswith("8.8"):
                    enriched.geo_country = "US"
                    enriched.ip_classification = "public"
        except Exception as e:
            logger.warning(f"GeoIP enrichment failed safely: {e}")

class ThreatIntelligenceEnricher(BaseEnricher):
    @property
    def enricher_name(self) -> str:
        return "ti_enricher"
        
    async def enrich(self, event: NormalizedSecurityEvent, enriched: EnrichedSecurityEvent) -> None:
        try:
            # Example IP Reputation match
            bad_ips = {"198.51.100.42"}
            if event.source_ip in bad_ips:
                enriched.ip_reputation_status = "malicious"
                enriched.ti_indicator_match_refs.append(event.source_ip)
                enriched.ti_source_refs.append("local_blocklist")
                enriched.ti_confidence = "high"
        except Exception as e:
            logger.warning(f"TI enrichment failed safely: {e}")

class MitreCandidateEnricher(BaseEnricher):
    @property
    def enricher_name(self) -> str:
        return "mitre_candidate_enricher"
        
    async def enrich(self, event: NormalizedSecurityEvent, enriched: EnrichedSecurityEvent) -> None:
        try:
            if event.event_category == "process" and event.command_line and "whoami" in event.command_line.lower():
                enriched.candidate_mitre_techniques.append("T1033") # System Owner/User Discovery
                enriched.candidate_mitre_confidence = "low"
                enriched.candidate_mitre_source = "heuristic"
        except Exception as e:
            logger.warning(f"MITRE candidate enrichment failed safely: {e}")

class EnrichmentEngine:
    def __init__(self):
        self.enrichers = [
            AssetEnricher(),
            GeoIPEnricher(),
            ThreatIntelligenceEnricher(),
            MitreCandidateEnricher()
        ]
        
    async def enrich_event(self, event: NormalizedSecurityEvent) -> EnrichedSecurityEvent:
        # Create the enriched event initialized with the normalized event's data
        enriched = EnrichedSecurityEvent(**event.model_dump())
        
        for enricher in self.enrichers:
            await enricher.enrich(event, enriched)
            
        return enriched
