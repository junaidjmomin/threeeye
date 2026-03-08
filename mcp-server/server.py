"""
server.py — Third Eye MCP Server

Exposes tools for the on-chain consortium agent:
  • Blockchain tools  → read/write RiskConsortium on Sepolia
  • 0G Compute tools  → AI inference via 0G decentralized compute network
  • Agent tools       → composite workflows (analyze + broadcast in one call)

Run:
    python server.py

Or via MCP host config (stdio transport):
    {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py"],
      "env": { ... }   // see .env.example
    }
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env from the mcp-server directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Lazy-init clients so the server starts even without all env vars
_blockchain: "BlockchainClient | None" = None
_zeroG: "ZeroGComputeClient | None" = None


def get_blockchain():
    global _blockchain
    if _blockchain is None:
        from blockchain import BlockchainClient
        _blockchain = BlockchainClient()
    return _blockchain


def get_zeroG():
    global _zeroG
    if _zeroG is None:
        from zeroG import ZeroGComputeClient
        _zeroG = ZeroGComputeClient()
    return _zeroG


# ── MCP App ───────────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="thirdeye-consortium-agent",
    instructions=(
        "Third Eye on-chain consortium agent. "
        "Tools for broadcasting anonymized vendor risk signals to the Sepolia "
        "consortium ledger and running AI inference via 0G Compute. "
        "Vendor identities are always SHA-256 hashed before any on-chain write."
    ),
)


# ════════════════════════════════════════════════════════════════════════════
# BLOCKCHAIN TOOLS
# ════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def get_network_info() -> dict[str, Any]:
    """
    Return Sepolia network status and RiskConsortium contract details.
    Useful for confirming the agent is connected before any write.
    """
    try:
        return get_blockchain().network_info()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def hash_vendor_id(vendor_id: str) -> dict[str, str]:
    """
    SHA-256 hash a vendor ID string for privacy-preserving on-chain storage.

    Args:
        vendor_id: Canonical vendor identifier (e.g. "ACME_PAYMENTS_LTD").

    Returns:
        Dict with 'vendor_id' and 'vendor_hash' (hex, 0x-prefixed).
    """
    from blockchain import hash_vendor_id_hex
    return {
        "vendor_id":   vendor_id,
        "vendor_hash": hash_vendor_id_hex(vendor_id),
    }


@mcp.tool()
def broadcast_risk_signal(
    vendor_id: str,
    signal_type: str,
    risk_dimension: str,
    severity: str,
    cert_in_relevant: bool,
    recommended_action: str,
    ai_analysis: str = "",
) -> dict[str, Any]:
    """
    Broadcast an anonymized vendor risk signal to the Sepolia consortium ledger.
    The vendor_id is SHA-256 hashed before writing — identity never leaves.

    Args:
        vendor_id:          Canonical vendor identifier (will be hashed).
        signal_type:        CRITICAL_BREACH | REGULATORY_ACTION | CERT_IN_ADVISORY |
                            SCORE_THRESHOLD | FINANCIAL_STRESS
        risk_dimension:     cybersecurity | regulatory | operational | newsLegal |
                            financialHealth | dataPrivacy | concentration | esg | fourthParty
        severity:           CRITICAL | HIGH | WATCH
        cert_in_relevant:   True if this triggers the 6-hour CERT-In reporting window.
        recommended_action: INITIATE_6HR_CLOCK | ESCALATE_CISO | REVIEW_CONTRACT | MONITOR
        ai_analysis:        Optional 0G Compute inference narrative (max 512 chars on-chain).

    Returns:
        Transaction hash, block number, and vendor_hash written to chain.
    """
    try:
        result = get_blockchain().broadcast_signal(
            vendor_id=vendor_id,
            signal_type=signal_type,
            risk_dimension=risk_dimension,
            severity=severity,
            cert_in_relevant=cert_in_relevant,
            recommended_action=recommended_action,
            ai_analysis=ai_analysis,
        )
        result["broadcasted_at"] = datetime.now(timezone.utc).isoformat()
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_vendor_signals(vendor_id: str) -> dict[str, Any]:
    """
    Retrieve all on-chain consortium signals for a given vendor.

    Args:
        vendor_id: Canonical vendor identifier (hashed internally for lookup).

    Returns:
        List of signal dicts plus total count.
    """
    try:
        signals = get_blockchain().get_vendor_signals(vendor_id)
        return {
            "vendor_id":    vendor_id,
            "vendor_hash":  __import__("blockchain").hash_vendor_id_hex(vendor_id),
            "total":        len(signals),
            "signals":      [s.to_dict() for s in signals],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_recent_signals(count: int = 10) -> dict[str, Any]:
    """
    Retrieve the N most recent consortium signals from the ledger (max 100).

    Args:
        count: Number of recent signals to fetch (default 10, max 100).

    Returns:
        List of signal dicts, newest last.
    """
    try:
        count = min(count, 100)
        signals = get_blockchain().get_recent_signals(count)
        return {
            "count":   len(signals),
            "signals": [s.to_dict() for s in signals],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def check_vendor_critical_alert(vendor_id: str, lookback_hours: int = 24) -> dict[str, Any]:
    """
    Check whether a vendor has an active CRITICAL signal within a time window.
    Used to determine whether the 6-hour CERT-In clock should be activated.

    Args:
        vendor_id:       Canonical vendor identifier.
        lookback_hours:  How far back to look in hours (default 24).

    Returns:
        Dict with 'has_critical' bool and metadata.
    """
    try:
        since = int(time.time()) - (lookback_hours * 3600)
        has_critical = get_blockchain().has_active_critical_signal(vendor_id, since)
        return {
            "vendor_id":       vendor_id,
            "has_critical":    has_critical,
            "lookback_hours":  lookback_hours,
            "checked_at":      datetime.now(timezone.utc).isoformat(),
            "cert_in_action":  "ACTIVATE_6HR_CLOCK" if has_critical else "NO_ACTION",
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_total_signals() -> dict[str, Any]:
    """Return total number of signals on the consortium ledger."""
    try:
        total = get_blockchain().total_signals()
        return {"total_signals": total}
    except Exception as e:
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════════════════════
# 0G COMPUTE TOOLS
# ════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def analyze_vendor_risk(
    vendor_name: str,
    risk_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Run AI risk analysis on a vendor using 0G Compute decentralized inference.
    Returns structured assessment including severity, regulatory citations,
    and whether to broadcast to the consortium.

    Args:
        vendor_name: Human-readable vendor name (not written on-chain).
        risk_data:   Dict of raw risk signals, e.g.:
                     {
                       "composite_score": 22,
                       "cybersecurity_score": 18,
                       "trigger": "dark web credential dump — 12,400 records",
                       "cve_unpatched": ["CVE-2024-1187"],
                       "rbi_outsourcing_flagged": true
                     }

    Returns:
        Structured risk assessment JSON from 0G Compute inference.
    """
    try:
        return get_zeroG().analyze_vendor_risk(vendor_name, risk_data)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def decode_consortium_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """
    Translate a raw on-chain consortium signal into a plain-English triage brief
    for a risk officer. Uses 0G Compute inference.

    Args:
        signal: Signal dict as returned by get_recent_signals or get_vendor_signals.

    Returns:
        Dict with 'triage_brief' field.
    """
    try:
        brief = get_zeroG().decode_consortium_signal(signal)
        return {"triage_brief": brief}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def draft_rbi_incident_note(
    vendor_name: str,
    incident_summary: str,
    cert_in_clock_started: str,
) -> dict[str, Any]:
    """
    Draft an RBI/CERT-In incident notification note using 0G Compute AI.

    Args:
        vendor_name:            Vendor name.
        incident_summary:       Plain-English description of the incident.
        cert_in_clock_started:  ISO 8601 datetime when the 6-hour clock started.

    Returns:
        Dict with 'note' field containing the draft notification.
    """
    try:
        note = get_zeroG().draft_rbi_incident_note(
            vendor_name, incident_summary, cert_in_clock_started
        )
        return {"note": note}
    except Exception as e:
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════════════════════
# COMPOSITE AGENT TOOL
# ════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def run_on_chain_agent(
    vendor_id: str,
    vendor_name: str,
    risk_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Full autonomous agent workflow:
      1. Run 0G Compute AI analysis on vendor risk data.
      2. If analysis recommends consortium broadcast → hash vendor ID and
         write anonymized signal to Sepolia RiskConsortium.
      3. Return full agent decision log.

    Args:
        vendor_id:   Canonical vendor ID (will be hashed for on-chain write).
        vendor_name: Human-readable name (only used for AI prompt, never on-chain).
        risk_data:   Raw risk signals dict.

    Returns:
        Full agent run result including AI analysis, broadcast decision, and tx details.
    """
    agent_log: dict[str, Any] = {
        "vendor_name":    vendor_name,
        "vendor_hash":    None,
        "step_1_ai":      None,
        "step_2_broadcast": None,
        "agent_decision": None,
        "ran_at":         datetime.now(timezone.utc).isoformat(),
    }

    # Step 1 — AI analysis via 0G Compute
    try:
        analysis = get_zeroG().analyze_vendor_risk(vendor_name, risk_data)
        agent_log["step_1_ai"] = analysis
    except Exception as e:
        agent_log["step_1_ai"] = {"error": str(e)}
        agent_log["agent_decision"] = "ABORTED_AI_FAILURE"
        return agent_log

    if analysis.get("parse_error"):
        agent_log["agent_decision"] = "ABORTED_AI_PARSE_ERROR"
        return agent_log

    # Step 2 — Broadcast decision
    should_broadcast = analysis.get("consortium_broadcast", False)
    severity = analysis.get("severity", "WATCH")
    cert_in  = analysis.get("cert_in_relevant", False)

    # Auto-broadcast if CRITICAL even if AI didn't set the flag
    if severity == "CRITICAL":
        should_broadcast = True

    from blockchain import hash_vendor_id_hex
    agent_log["vendor_hash"] = hash_vendor_id_hex(vendor_id)

    if should_broadcast:
        try:
            tx_result = get_blockchain().broadcast_signal(
                vendor_id=vendor_id,
                signal_type=analysis.get("signal_type", "SCORE_THRESHOLD"),
                risk_dimension=analysis.get("primary_dimension", "cybersecurity"),
                severity=severity,
                cert_in_relevant=cert_in,
                recommended_action=analysis.get("recommended_action", "MONITOR"),
                ai_analysis=analysis.get("broadcast_narrative", ""),
            )
            agent_log["step_2_broadcast"] = tx_result
            agent_log["agent_decision"] = "BROADCAST_SENT"
        except Exception as e:
            agent_log["step_2_broadcast"] = {"error": str(e)}
            agent_log["agent_decision"] = "BROADCAST_FAILED"
    else:
        agent_log["step_2_broadcast"] = None
        agent_log["agent_decision"] = "NO_BROADCAST"

    return agent_log


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
