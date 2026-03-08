require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const SEPOLIA_RPC_URL   = process.env.SEPOLIA_RPC_URL   || "";
const DEPLOYER_PRIVKEY  = process.env.DEPLOYER_PRIVKEY  || "";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },

  networks: {
    hardhat: {},

    localhost: {
      url: "http://127.0.0.1:8545",
    },

    sepolia: {
      url: SEPOLIA_RPC_URL,
      accounts: DEPLOYER_PRIVKEY ? [DEPLOYER_PRIVKEY] : [],
      chainId: 11155111,
    },
  },

  etherscan: {
    apiKey: ETHERSCAN_API_KEY,
  },

  paths: {
    sources:   "./contracts",
    tests:     "./test",
    cache:     "./cache",
    artifacts: "./artifacts",
  },
};
