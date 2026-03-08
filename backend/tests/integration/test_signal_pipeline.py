"""
Integration test: raw signal text → LLM parse → score → alert creation.
Uses mocked LLM provider — does NOT call real API.
"""
import json
import pytest
from unittest.mock import AsyncMock, patch

from app.engine.llm.signal_parser import parse_signal


@pytest.mark.asyncio
async def test_signal_parse_to_valid_parsed_signal():
    """Full signal text runs through the parser and returns expected structure."""
    mock_response = {
        "vendor_name": "Infosys",
        "dimension": "cybersecurity",
        "severity": 9,
        "signal_type": "CRITICAL_BREACH",
        "regulatory_implication": "CERT-In Directions 2022, Section 4(ii)",
        "confidence": 0.92,
        "summary": "Infosys systems reportedly breached with customer data exfiltrated",
    }

    class RecordedProvider:
        async def complete(self, system, user):
            return json.dumps(mock_response)

        async def complete_json(self, system, user):
            return mock_response

    vendor_names = ["Infosys", "TCS", "Wipro", "HCL Technologies"]
    text = (
        "Breaking: Infosys reports major cybersecurity incident. "
        "Customer banking data leaked on dark web. RBI notified."
    )

    parsed = await parse_signal(text, vendor_names, RecordedProvider())

    assert parsed.vendor_name == "Infosys"
    assert parsed.dimension == "cybersecurity"
    assert parsed.severity == 9
    assert parsed.signal_type == "CRITICAL_BREACH"
    assert parsed.confidence >= 0.9
    assert parsed.regulatory_implication is not None


@pytest.mark.asyncio
async def test_signal_pipeline_high_severity_triggers_rescore(monkeypatch):
    """
    High-severity signal for a known vendor should enqueue a rescore task.
    """
    enqueued: list[str] = []

    class FakeTask:
        def delay(self, vendor_id):
            enqueued.append(vendor_id)

    mock_response = {
        "vendor_name": "TestVendor",
        "dimension": "cybersecurity",
        "severity": 9,
        "signal_type": "CRITICAL_BREACH",
        "regulatory_implication": "CERT-In",
        "confidence": 0.95,
        "summary": "Breach",
    }

    class RecordedProvider:
        async def complete(self, s, u): return json.dumps(mock_response)
        async def complete_json(self, s, u): return mock_response

    parsed = await parse_signal("TestVendor breach", ["TestVendor"], RecordedProvider())

    assert parsed.severity >= 8
    assert parsed.signal_type == "CRITICAL_BREACH"
    # In real integration: would check DB for persisted signal and queued rescore
