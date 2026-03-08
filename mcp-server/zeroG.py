"""
zeroG.py — 0G Compute Network client for decentralized AI inference.

0G Compute provides OpenAI-compatible inference endpoints backed by a
decentralized provider network with on-chain payment settlement.

Docs:  https://docs.0g.ai/compute-network
SDK:   https://github.com/0glabs/0g-serving-user-broker
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

# ─── Prompt templates ─────────────────────────────────────────────────────────

RISK_ANALYSIS_SYSTEM = """You are Third Eye, an AI vendor risk analyst for Indian banks.
You analyze vendor risk signals across 9 dimensions:
cybersecurity, regulatory, operational, newsLegal, financialHealth, dataPrivacy,
concentration, esg, fourthParty.

Regulations in scope: RBI IT Outsourcing Directions 2023, CERT-In 6-hour window,
DPDP Act 2023 (₹200 Cr penalty surface).

Always respond in JSON with this exact shape:
{
  "risk_summary": "<2-3 sentence plain-English summary>",
  "primary_dimension": "<one of the 9 dimensions>",
  "severity": "CRITICAL|HIGH|WATCH|STABLE",
  "cert_in_relevant": true|false,
  "recommended_action": "INITIATE_6HR_CLOCK|ESCALATE_CISO|REVIEW_CONTRACT|MONITOR|NO_ACTION",
  "signal_type": "CRITICAL_BREACH|REGULATORY_ACTION|CERT_IN_ADVISORY|SCORE_THRESHOLD|FINANCIAL_STRESS|NONE",
  "regulatory_citations": ["<e.g. RBI IT Outsourcing Directions 2023 §4.2>"],
  "consortium_broadcast": true|false,
  "broadcast_narrative": "<max 512 chars — what to write as aiAnalysis on-chain>"
}"""

SIGNAL_DECODE_SYSTEM = """You are a risk analyst. Given an on-chain consortium signal,
produce a plain-English triage summary for a bank's risk officer.
Be concise (3-5 sentences). Note CERT-In obligations if cert_in_relevant is true."""


# ─── Client ───────────────────────────────────────────────────────────────────

class ZeroGComputeClient:
    """
    Wraps the 0G Compute inference endpoint.

    Environment variables:
      ZG_SERVING_ENDPOINT   Base URL of the 0G serving node
                            e.g. https://inference.0g.ai/v1
      ZG_API_KEY            API key / bearer token for the 0G serving broker
      ZG_MODEL              Model name served by 0G (default: meta-llama/Llama-3-8b-instruct)
    """

    def __init__(self) -> None:
        endpoint  = os.environ.get("ZG_SERVING_ENDPOINT", "https://inference.0g.ai/v1")
        api_key   = os.environ.get("ZG_API_KEY", "zg-placeholder")
        self.model = os.environ.get("ZG_MODEL", "meta-llama/Llama-3-8b-instruct")

        self.client = OpenAI(
            base_url=endpoint,
            api_key=api_key,
        )

    # ── Core inference ────────────────────────────────────────────────────────

    def _chat(self, system: str, user: str, max_tokens: int = 800) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",  "content": system},
                {"role": "user",    "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze_vendor_risk(
        self,
        vendor_name: str,
        risk_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze raw vendor risk data and return structured risk assessment.
        The result drives whether to broadcast to the on-chain consortium.
        """
        import json

        user_prompt = f"""Vendor: {vendor_name}

Risk Data:
{json.dumps(risk_data, indent=2)}

Analyze this vendor's risk posture. Determine severity, relevant regulations,
and whether this warrants a consortium broadcast to other Indian banks."""

        raw = self._chat(RISK_ANALYSIS_SYSTEM, user_prompt)

        # Parse JSON — tolerate markdown fences
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # Return raw text wrapped if JSON parse fails
            return {"raw_response": raw, "parse_error": True}

    def decode_consortium_signal(self, signal: dict[str, Any]) -> str:
        """
        Translate a raw on-chain signal dict into a plain-English triage brief
        for a risk officer.
        """
        import json

        user_prompt = f"""On-chain consortium signal received:
{json.dumps(signal, indent=2)}

Produce a triage brief for the bank's risk officer."""

        return self._chat(SIGNAL_DECODE_SYSTEM, user_prompt, max_tokens=300)

    def draft_rbi_incident_note(
        self,
        vendor_name: str,
        incident_summary: str,
        cert_in_clock_started: str,
    ) -> str:
        """
        Draft a short RBI/CERT-In incident notification note.
        """
        system = (
            "You are a compliance officer at an Indian bank. Draft a concise incident "
            "notification note suitable for RBI/CERT-In submission under the 6-hour reporting "
            "obligation. Use formal language. Max 400 words."
        )
        user = (
            f"Vendor: {vendor_name}\n"
            f"Incident: {incident_summary}\n"
            f"CERT-In clock started: {cert_in_clock_started}\n\n"
            "Draft the notification note."
        )
        return self._chat(system, user, max_tokens=500)
