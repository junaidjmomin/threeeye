// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RiskConsortium
 * @notice Third Eye on-chain consortium ledger for inter-bank vendor risk signals.
 *         All vendor identities are SHA-256 hashed. Source bank is never exposed.
 *         Deployed on Sepolia testnet (Phase 3 target: permissioned Hyperledger Fabric).
 */
contract RiskConsortium {
    // ─── Structs ───────────────────────────────────────────────────────────────

    struct RiskSignal {
        bytes32 vendorHash;         // SHA-256 of canonical vendor ID — identity never exposed
        string  signalType;         // CRITICAL_BREACH | REGULATORY_ACTION | CERT_IN_ADVISORY | SCORE_THRESHOLD
        string  riskDimension;      // cybersecurity | regulatory | operational | newsLegal | financialHealth | dataPrivacy | concentration | esg | fourthParty
        string  severity;           // CRITICAL | HIGH | WATCH
        bool    certInRelevant;     // triggers 6-hour CERT-In clock at receiving nodes
        string  recommendedAction;  // INITIATE_6HR_CLOCK | ESCALATE_CISO | REVIEW_CONTRACT | MONITOR
        uint256 timestamp;
        address broadcaster;        // node address (bank identity abstracted at app layer)
        string  aiAnalysis;         // 0G Compute inference result (risk narrative, max 512 chars)
    }

    // ─── State ─────────────────────────────────────────────────────────────────

    RiskSignal[] private _signals;

    mapping(bytes32 => uint256[]) private _vendorSignalIndices;
    mapping(address => bool)      public  authorizedBroadcasters;
    mapping(address => string)    public  broadcasterAlias;   // e.g., "SBI-NODE-1" — set by owner

    address public owner;
    uint256 public constant MAX_SIGNALS_PER_QUERY = 100;

    // ─── Events ────────────────────────────────────────────────────────────────

    event SignalBroadcast(
        bytes32 indexed vendorHash,
        string          signalType,
        string          severity,
        bool            certInRelevant,
        string          recommendedAction,
        uint256         timestamp,
        address indexed broadcaster
    );

    event BroadcasterAdded(address indexed broadcaster, string alias_);
    event BroadcasterRevoked(address indexed broadcaster);

    // ─── Modifiers ─────────────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "RiskConsortium: not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedBroadcasters[msg.sender], "RiskConsortium: not authorized broadcaster");
        _;
    }

    // ─── Constructor ───────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        authorizedBroadcasters[msg.sender] = true;
        broadcasterAlias[msg.sender] = "DEPLOYER";
    }

    // ─── Admin ─────────────────────────────────────────────────────────────────

    function addBroadcaster(address broadcaster, string calldata alias_) external onlyOwner {
        authorizedBroadcasters[broadcaster] = true;
        broadcasterAlias[broadcaster] = alias_;
        emit BroadcasterAdded(broadcaster, alias_);
    }

    function revokeBroadcaster(address broadcaster) external onlyOwner {
        authorizedBroadcasters[broadcaster] = false;
        emit BroadcasterRevoked(broadcaster);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "RiskConsortium: zero address");
        owner = newOwner;
    }

    // ─── Core: Broadcast ───────────────────────────────────────────────────────

    /**
     * @notice Broadcast an anonymized vendor risk signal to the consortium.
     * @param vendorHash         keccak256 or sha256 of the canonical vendor ID.
     * @param signalType         Short enum-style string identifying signal category.
     * @param riskDimension      Which of the 9 Third Eye risk dimensions is affected.
     * @param severity           CRITICAL | HIGH | WATCH
     * @param certInRelevant     Whether this triggers the 6-hour CERT-In reporting window.
     * @param recommendedAction  Action code for receiving bank nodes.
     * @param aiAnalysis         0G Compute inference result — risk narrative (may be empty).
     * @return signalIndex       Index in the global signals array.
     */
    function broadcastSignal(
        bytes32        vendorHash,
        string calldata signalType,
        string calldata riskDimension,
        string calldata severity,
        bool           certInRelevant,
        string calldata recommendedAction,
        string calldata aiAnalysis
    ) external onlyAuthorized returns (uint256 signalIndex) {
        signalIndex = _signals.length;

        _signals.push(RiskSignal({
            vendorHash:        vendorHash,
            signalType:        signalType,
            riskDimension:     riskDimension,
            severity:          severity,
            certInRelevant:    certInRelevant,
            recommendedAction: recommendedAction,
            timestamp:         block.timestamp,
            broadcaster:       msg.sender,
            aiAnalysis:        aiAnalysis
        }));

        _vendorSignalIndices[vendorHash].push(signalIndex);

        emit SignalBroadcast(
            vendorHash,
            signalType,
            severity,
            certInRelevant,
            recommendedAction,
            block.timestamp,
            msg.sender
        );
    }

    // ─── Read ──────────────────────────────────────────────────────────────────

    function totalSignals() external view returns (uint256) {
        return _signals.length;
    }

    function getSignal(uint256 index) external view returns (
        bytes32 vendorHash,
        string  memory signalType,
        string  memory riskDimension,
        string  memory severity,
        bool    certInRelevant,
        string  memory recommendedAction,
        uint256 timestamp,
        string  memory broadcasterAlias_,
        string  memory aiAnalysis
    ) {
        require(index < _signals.length, "RiskConsortium: index out of range");
        RiskSignal storage s = _signals[index];
        return (
            s.vendorHash,
            s.signalType,
            s.riskDimension,
            s.severity,
            s.certInRelevant,
            s.recommendedAction,
            s.timestamp,
            broadcasterAlias[s.broadcaster],
            s.aiAnalysis
        );
    }

    /**
     * @notice Get all signal indices for a specific vendor hash.
     */
    function getVendorSignalIndices(bytes32 vendorHash) external view returns (uint256[] memory) {
        return _vendorSignalIndices[vendorHash];
    }

    /**
     * @notice Get the N most recent signal indices (up to MAX_SIGNALS_PER_QUERY).
     */
    function getRecentSignalIndices(uint256 count) external view returns (uint256[] memory indices) {
        uint256 total = _signals.length;
        if (count > MAX_SIGNALS_PER_QUERY) count = MAX_SIGNALS_PER_QUERY;
        uint256 resultCount = count > total ? total : count;

        indices = new uint256[](resultCount);
        for (uint256 i = 0; i < resultCount; i++) {
            indices[i] = total - resultCount + i;
        }
    }

    /**
     * @notice Check whether a vendor hash has any CRITICAL signals within a time window.
     * @param vendorHash  Hashed vendor ID.
     * @param since       Unix timestamp lower bound.
     */
    function hasActiveCriticalSignal(bytes32 vendorHash, uint256 since) external view returns (bool) {
        uint256[] storage idxList = _vendorSignalIndices[vendorHash];
        for (uint256 i = idxList.length; i > 0; i--) {
            RiskSignal storage s = _signals[idxList[i - 1]];
            if (s.timestamp < since) break;
            if (keccak256(bytes(s.severity)) == keccak256(bytes("CRITICAL"))) return true;
        }
        return false;
    }
}
