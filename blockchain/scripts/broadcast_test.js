/**
 * broadcast_test.js — smoke-test a deployed RiskConsortium on Sepolia.
 * Usage: npx hardhat run scripts/broadcast_test.js --network sepolia
 */
const hre = require("hardhat");
const crypto = require("crypto");

function vendorHash(vendorId) {
  return "0x" + crypto.createHash("sha256").update(vendorId).digest("hex");
}

async function main() {
  const fs = require("fs");
  const deployments = JSON.parse(fs.readFileSync("./deployments.json", "utf8"));

  const [signer] = await hre.ethers.getSigners();
  console.log("Broadcaster:", signer.address);
  console.log("Contract:   ", deployments.contractAddress);

  const contract = await hre.ethers.getContractAt(
    "RiskConsortium",
    deployments.contractAddress,
    signer
  );

  const vHash = vendorHash("ACME_PAYMENTS_LTD");
  console.log("\nVendor hash:", vHash);

  const tx = await contract.broadcastSignal(
    vHash,
    "CRITICAL_BREACH",
    "cybersecurity",
    "CRITICAL",
    true,
    "INITIATE_6HR_CLOCK",
    "Dark web credential dump detected (12,400 records). Cybersecurity posture dropped from 70 to 28. Immediate vendor notification required."
  );

  console.log("Tx sent:", tx.hash);
  const receipt = await tx.wait();
  console.log("✅ Confirmed in block:", receipt.blockNumber);

  const total = await contract.totalSignals();
  console.log("Total signals on-chain:", total.toString());
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
