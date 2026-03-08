const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying RiskConsortium with account:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH");

  const RiskConsortium = await hre.ethers.getContractFactory("RiskConsortium");
  const contract = await RiskConsortium.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("\n✅ RiskConsortium deployed to:", address);
  console.log("Network:", hre.network.name);
  console.log("Block:", await hre.ethers.provider.getBlockNumber());

  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\nVerify with:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${address}`);
  }

  // Write deployment info to a JSON file so mcp-server can pick it up
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    contractAddress: address,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber(),
  };

  fs.writeFileSync(
    "./deployments.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\nDeployment info saved to blockchain/deployments.json");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
