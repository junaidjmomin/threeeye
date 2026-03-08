"""
blockchain.py — Web3 client for the RiskConsortium contract on Sepolia.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# ── ABI (minimal — only the functions the MCP server calls) ──────────────────

RISK_CONSORTIUM_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "name": "vendorHash",        "type": "bytes32"},
            {"indexed": False, "name": "signalType",        "type": "string"},
            {"indexed": False, "name": "severity",          "type": "string"},
            {"indexed": False, "name": "certInRelevant",    "type": "bool"},
            {"indexed": False, "name": "recommendedAction", "type": "string"},
            {"indexed": False, "name": "timestamp",         "type": "uint256"},
            {"indexed": True,  "name": "broadcaster",       "type": "address"},
        ],
        "name": "SignalBroadcast",
        "type": "event",
    },
    {
        "inputs": [
            {"name": "broadcaster", "type": "address"},
            {"name": "alias_",      "type": "string"},
        ],
        "name": "addBroadcaster",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "vendorHash",        "type": "bytes32"},
            {"name": "signalType",        "type": "string"},
            {"name": "riskDimension",     "type": "string"},
            {"name": "severity",          "type": "string"},
            {"name": "certInRelevant",    "type": "bool"},
            {"name": "recommendedAction", "type": "string"},
            {"name": "aiAnalysis",        "type": "string"},
        ],
        "name": "broadcastSignal",
        "outputs": [{"name": "signalIndex", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSignals",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "index", "type": "uint256"}],
        "name": "getSignal",
        "outputs": [
            {"name": "vendorHash",        "type": "bytes32"},
            {"name": "signalType",        "type": "string"},
            {"name": "riskDimension",     "type": "string"},
            {"name": "severity",          "type": "string"},
            {"name": "certInRelevant",    "type": "bool"},
            {"name": "recommendedAction", "type": "string"},
            {"name": "timestamp",         "type": "uint256"},
            {"name": "broadcasterAlias_", "type": "string"},
            {"name": "aiAnalysis",        "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "vendorHash", "type": "bytes32"}],
        "name": "getVendorSignalIndices",
        "outputs": [{"name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "count", "type": "uint256"}],
        "name": "getRecentSignalIndices",
        "outputs": [{"name": "indices", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "vendorHash", "type": "bytes32"},
            {"name": "since",      "type": "uint256"},
        ],
        "name": "hasActiveCriticalSignal",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "broadcaster", "type": "address"}],
        "name": "authorizedBroadcasters",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_vendor_id(vendor_id: str) -> bytes:
    """SHA-256 hash a vendor ID string, return 32-byte bytes."""
    return hashlib.sha256(vendor_id.encode()).digest()


def hash_vendor_id_hex(vendor_id: str) -> str:
    """Return hex string of SHA-256 hash (with 0x prefix)."""
    return "0x" + hashlib.sha256(vendor_id.encode()).hexdigest()


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class RiskSignalData:
    index: int
    vendor_hash: str
    signal_type: str
    risk_dimension: str
    severity: str
    cert_in_relevant: bool
    recommended_action: str
    timestamp: int
    broadcaster_alias: str
    ai_analysis: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index":              self.index,
            "vendor_hash":        self.vendor_hash,
            "signal_type":        self.signal_type,
            "risk_dimension":     self.risk_dimension,
            "severity":           self.severity,
            "cert_in_relevant":   self.cert_in_relevant,
            "recommended_action": self.recommended_action,
            "timestamp":          self.timestamp,
            "broadcaster_alias":  self.broadcaster_alias,
            "ai_analysis":        self.ai_analysis,
        }


# ── Client ────────────────────────────────────────────────────────────────────

class BlockchainClient:
    """Thin wrapper around Web3 for the RiskConsortium contract on Sepolia."""

    def __init__(self) -> None:
        rpc_url          = os.environ["SEPOLIA_RPC_URL"]
        self._privkey    = os.environ.get("BROADCASTER_PRIVKEY", "")
        contract_address = os.environ["CONTRACT_ADDRESS"]

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # Sepolia is PoA-compatible
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if not self.w3.is_connected():
            raise RuntimeError(f"Cannot connect to Sepolia RPC: {rpc_url}")

        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=RISK_CONSORTIUM_ABI,
        )

        self.account = (
            self.w3.eth.account.from_key(self._privkey)
            if self._privkey
            else None
        )

    # ── Read ──────────────────────────────────────────────────────────────────

    def total_signals(self) -> int:
        return self.contract.functions.totalSignals().call()

    def get_signal(self, index: int) -> RiskSignalData:
        result = self.contract.functions.getSignal(index).call()
        return RiskSignalData(
            index=index,
            vendor_hash=result[0].hex(),
            signal_type=result[1],
            risk_dimension=result[2],
            severity=result[3],
            cert_in_relevant=result[4],
            recommended_action=result[5],
            timestamp=result[6],
            broadcaster_alias=result[7],
            ai_analysis=result[8],
        )

    def get_vendor_signals(self, vendor_id: str) -> list[RiskSignalData]:
        vh = hash_vendor_id(vendor_id)
        indices = self.contract.functions.getVendorSignalIndices(vh).call()
        return [self.get_signal(i) for i in indices]

    def get_recent_signals(self, count: int = 10) -> list[RiskSignalData]:
        indices = self.contract.functions.getRecentSignalIndices(count).call()
        return [self.get_signal(i) for i in indices]

    def has_active_critical_signal(self, vendor_id: str, since_unix: int) -> bool:
        vh = hash_vendor_id(vendor_id)
        return self.contract.functions.hasActiveCriticalSignal(vh, since_unix).call()

    def is_authorized(self, address: str) -> bool:
        return self.contract.functions.authorizedBroadcasters(
            Web3.to_checksum_address(address)
        ).call()

    # ── Write ─────────────────────────────────────────────────────────────────

    def broadcast_signal(
        self,
        vendor_id: str,
        signal_type: str,
        risk_dimension: str,
        severity: str,
        cert_in_relevant: bool,
        recommended_action: str,
        ai_analysis: str = "",
    ) -> dict[str, Any]:
        if not self.account:
            raise ValueError("BROADCASTER_PRIVKEY not configured — cannot send transactions")

        vendor_hash_bytes = hash_vendor_id(vendor_id)

        fn = self.contract.functions.broadcastSignal(
            vendor_hash_bytes,
            signal_type,
            risk_dimension,
            severity,
            cert_in_relevant,
            recommended_action,
            ai_analysis[:512],  # cap at 512 chars for gas efficiency
        )

        tx = fn.build_transaction({
            "from":  self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "gas":   300_000,
            "gasPrice": self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self._privkey)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "tx_hash":      tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "status":       "success" if receipt["status"] == 1 else "failed",
            "vendor_hash":  hash_vendor_id_hex(vendor_id),
        }

    def network_info(self) -> dict[str, Any]:
        chain_id = self.w3.eth.chain_id
        return {
            "chain_id":         chain_id,
            "network":          "sepolia" if chain_id == 11155111 else f"chain-{chain_id}",
            "contract_address": self.contract.address,
            "latest_block":     self.w3.eth.block_number,
            "broadcaster":      self.account.address if self.account else None,
        }
