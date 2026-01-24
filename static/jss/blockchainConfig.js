// ===============================
// CONTRACT ADDRESS (SEPOLIA)
// ===============================
// Use injected address from backend if available, else fallback (fallback should ideally be avoided)
window.CONTRACT_ADDRESS = window.CONTRACT_ADDRESS || "0xa98820b2572F5c963192c4065995ba88EBbaf4B9";

// ===============================
// CONTRACT ABI
// ===============================
window.CONTRACT_ABI = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "candidateId",
                "type": "uint256"
            }
        ],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "candidateId",
                "type": "uint256"
            }
        ],
        "name": "getVotes",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "hasVoted",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
];

