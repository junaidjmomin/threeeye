"""Tests for LLM signal parser with mocked provider."""
import json

import pytest

from app.engine.llm.signal_parser import ParsedSignal, parse_signal


class MockProvider:
    """Mock LLM provider that returns predetermined JSON responses."""

    def __init__(self, response: dict):
        self._response = response

    async def complete(self, system: str, user: str) -> str:
        return json.dumps(self._response)

    async def complete_json(self, system: str, user: str) -> dict:
        return self._response


@pytest.mark.asyncio
async def test_parse_signal_returns_parsed_signal():
    provider = MockProvider({
        "vendor_name": "Infosys",
        "dimension": "cybersecurity",
        "severity": 8,
        "signal_type": "CRITICAL_BREACH",
        "regulatory_implication": "CERT-In Directions 2022, Section 4",
        "confidence": 0.9,
        "summary": "Infosys reported a critical data breach affecting 100k customers",
    })

    result = await parse_signal(
        text="Infosys suffers major breach, customer data leaked",
        vendor_names=["Infosys", "TCS", "Wipro"],
        provider=provider,
    )

    assert isinstance(result, ParsedSignal)
    assert result.vendor_name == "Infosys"
    assert result.dimension == "cybersecurity"
    assert result.severity == 8
    assert result.signal_type == "CRITICAL_BREACH"
    assert result.confidence == 0.9
    assert result.regulatory_implication is not None


@pytest.mark.asyncio
async def test_parse_signal_clamps_severity():
    provider = MockProvider({
        "vendor_name": "TCS",
        "dimension": "regulatory",
        "severity": 15,  # out of range
        "signal_type": "REGULATORY_ACTION",
        "regulatory_implication": None,
        "confidence": 0.7,
        "summary": "RBI fine",
    })

    result = await parse_signal("TCS fined by RBI", ["TCS"], provider)
    assert result.severity == 10  # clamped to max


@pytest.mark.asyncio
async def test_parse_signal_invalid_dimension_becomes_none():
    provider = MockProvider({
        "vendor_name": "Wipro",
        "dimension": "invalid_dimension_xyz",
        "severity": 5,
        "signal_type": "NEGATIVE_NEWS",
        "regulatory_implication": None,
        "confidence": 0.6,
        "summary": "test",
    })

    result = await parse_signal("Wipro news", ["Wipro"], provider)
    assert result.dimension is None


@pytest.mark.asyncio
async def test_parse_signal_llm_failure_returns_unknown():
    class FailingProvider:
        async def complete(self, *args): raise RuntimeError("API error")
        async def complete_json(self, *args): raise RuntimeError("API error")

    result = await parse_signal("some text", ["Vendor"], FailingProvider())
    assert result.signal_type == "UNKNOWN"
    assert result.confidence == 0.0
    assert result.vendor_name is None


@pytest.mark.asyncio
async def test_parse_signal_vendor_fuzzy_match():
    """Vendor name in LLM response doesn't need to be exact match."""
    provider = MockProvider({
        "vendor_name": "Infosys Limited",  # slightly different from list
        "dimension": "operational",
        "severity": 4,
        "signal_type": "OPERATIONAL_FAILURE",
        "regulatory_implication": None,
        "confidence": 0.75,
        "summary": "Outage",
    })

    result = await parse_signal("Infosys outage", ["Infosys", "TCS"], provider)
    assert result.vendor_name == "Infosys"  # fuzzy matched
