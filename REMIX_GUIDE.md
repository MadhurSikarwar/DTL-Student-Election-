# How to Deploy Your Smart Contract using Remix IDE

Since the website is showing a lot of UI, follow these exact steps to deploy `Election.sol`.

## Phase 1: Setup
1.  Open **[Remix IDE](https://remix.ethereum.org/)** in your browser.
2.  On the left sidebar, click the **File Explorer** icon (top icon, looks like two papers).
3.  Click the **"Create New File"** icon (tiny document with a +).
4.  Name the file: `Election.sol`.
5.  **Copy & Paste** the code below into that new file:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Election {
    mapping(uint256 => uint256) public votes;
    uint256 public totalVotes;
    event Voted(uint256 indexed candidateId);

    function vote(uint256 candidateId) public {
        require(candidateId > 0, "Invalid Candidate ID");
        votes[candidateId] += 1;
        totalVotes += 1;
        emit Voted(candidateId);
    }

    function getVotes(uint256 candidateId) public view returns (uint256) {
        return votes[candidateId];
    }
}
```

## Phase 2: Compile
1.  Click the **Solidity Compiler** icon on the left sidebar (looks like an "S" shape).
2.  Ensure "Compiler" is set to version `0.8.x` (or newer).
3.  Click the big blue button: **"Compile Election.sol"**.
4.  You should see a green checkmark appear on the sidebar icon.

## Phase 3: Deploy
1.  Click the **Deploy & Run Transactions** icon on the left sidebar (ethereum logo).
2.  **CRITICAL**: Under **"Environment"**, change the dropdown from "Remix VM" to **"Injected Provider - MetaMask"**.
    *   *MetaMask will pop up. Confirm the connection.*
    *   *Make sure your MetaMask is on the "Sepolia" network.*
3.  Ensure the "Contract" dropdown says `Election - Election.sol`.
4.  Click the orange **"Deploy"** button.
    *   *MetaMask will pop up again for the transaction fee.*
    *   *Click "Confirm".*

## Phase 4: Get Address
1.  Wait a few seconds for the transaction to finish.
2.  Look at the bottom of the left panel under **"Deployed Contracts"**.
3.  You will see `ELECTION AT 0x...`.
4.  Click the generic **Copy Icon** (two overlapping squares) next to the name to copy the address.

## Phase 5: Connect to Website
1.  Go back to your VS Code project.
2.  Open the `.env` file.
3.  Replace the old address with the new one you just copied:
    ```
    CONTRACT_ADDRESS=0xYourNewAddressHere
    ```
4.  **Restart your Python server** (Ctrl+C in terminal, then run `python app.py`).
