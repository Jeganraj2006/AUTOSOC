from autosoc_api.services.llm import OllamaLLMService


def test_legacy_llm_adapter_does_not_invent_high_confidence() -> None:
    result = OllamaLLMService()._parse_llm_response(
        '{"summary":"Observed evidence only.","findings":["A finding"],"recommended_actions":[]}',
        "Synthetic incident",
        "198.51.100.10",
    )

    for section_name in (
        "verification_specialist",
        "incident_investigator",
        "threat_intel_enricher",
        "risk_assessor",
    ):
        assert result[section_name]["confidence"] == "not_assessed"
