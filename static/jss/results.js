// =====================================================
// PROVIDER (PUBLIC SEPOLIA RPC)
// =====================================================
// =====================================================
// PROVIDER (PUBLIC SEPOLIA RPC)
// =====================================================
// Use a robust public node to avoid Alchemy key issues
const RPC_URL = "https://ethereum-sepolia.publicnode.com";

let provider;
try {
    // Ethers v6
    if (ethers.JsonRpcProvider) {
        provider = new ethers.JsonRpcProvider(RPC_URL);
    }
    // Ethers v5
    else if (ethers.providers && ethers.providers.JsonRpcProvider) {
        provider = new ethers.providers.JsonRpcProvider(RPC_URL);
    } else {
        console.error("Ethers.js not loaded or incompatible version.");
    }
} catch (e) {
    console.error("Provider Init Error:", e);
}


// =====================================================
// ELEMENT REFERENCES
// =====================================================
const v1 = document.getElementById("v1");
const v2 = document.getElementById("v2");
const v3 = document.getElementById("v3");
const v4 = document.getElementById("v4");
const v5 = document.getElementById("v5");
const v6 = document.getElementById("v6");

const card1 = document.getElementById("card1");
const card2 = document.getElementById("card2");
const card3 = document.getElementById("card3");
const card4 = document.getElementById("card4");
const card5 = document.getElementById("card5");
const card6 = document.getElementById("card6");

const winnerText = document.getElementById("winnerText");

// =====================================================
// FETCH VOTES
// =====================================================
async function fetchVotes() {
    try {
        // 1. Get Offsets from Backend
        const offsetRes = await fetch('/api/offsets');
        const offsetData = await offsetRes.json();
        const offsets = offsetData.offsets || [0, 0, 0, 0, 0, 0];

        // 2. Get Total Votes from Blockchain
        const contract = new ethers.Contract(
            window.CONTRACT_ADDRESS,
            window.CONTRACT_ABI,
            provider
        );

        const rawVotes = await Promise.all([
            contract.getVotes(1),
            contract.getVotes(2),
            contract.getVotes(3),
            contract.getVotes(4),
            contract.getVotes(5),
            contract.getVotes(6)
        ]);

        // 3. Subtract Offsets
        const finalVotes = rawVotes.map((v, i) => {
            const val = Number(v) - (offsets[i] || 0);
            return val < 0 ? 0 : val; // Safety check
        });

        return finalVotes;

    } catch (err) {
        console.error("Blockchain Fetch Error:", err);
        return null;
    }
}

// =====================================================
// UPDATE UI
// =====================================================
function updateUI(votes) {
    if (!votes) return;

    const total = votes.reduce((a, b) => a + b, 0);

    [v1, v2, v3, v4, v5, v6].forEach((el, i) => {
        el.textContent = votes[i];
    });

    const cards = [card1, card2, card3, card4, card5, card6];
    cards.forEach((card, i) => {
        const percent = total ? Math.round((votes[i] / total) * 100) : 0;
        const fill = card.querySelector(".fill");
        if (fill) fill.style.width = percent + "%";
    });

    determineWinner(votes);
}

// =====================================================
// WINNER LOGIC
// =====================================================
function determineWinner(votes) {
    const max = Math.max(...votes);

    const cards = [card1, card2, card3, card4, card5, card6];
    const names = [
        "Candidate One",
        "Candidate Two",
        "Candidate Three",
        "Candidate Four",
        "Candidate Five",
        "Candidate Six"
    ];

    cards.forEach(c => c.classList.remove("leader"));

    if (max === 0) {
        winnerText.textContent = "Waiting for votes...";
        return;
    }

    const winners = votes
        .map((v, i) => (v === max ? { name: names[i], el: cards[i] } : null))
        .filter(Boolean);

    if (winners.length > 1) {
        winnerText.textContent = "Current Tie!";
        winners.forEach(w => w.el.classList.add("leader"));
    } else {
        winnerText.textContent = "Winner: " + winners[0].name;
        winners[0].el.classList.add("leader");
    }
}

// =====================================================
// AUTO REFRESH
// =====================================================
async function refresh() {
    const votes = await fetchVotes();
    if (votes) updateUI(votes);
}

refresh();
setInterval(refresh, 7000);

// =====================================================
// CSV EXPORT LOGIC
// =====================================================
function downloadCSV() {
    // 1. Get Data
    const rows = [
        ["Candidate Name", "Position", "Total Votes"]
    ];

    const names = [
        "Candidate One", "Candidate Two", "Candidate Three",
        "Candidate Four", "Candidate Five", "Candidate Six"
    ];

    // Grab current values from DOM
    names.forEach((name, i) => {
        const count = document.getElementById(`v${i + 1}`).textContent;
        rows.push([name, "Class Rep", count]);
    });

    // 2. Convert to CSV String
    let csvContent = "data:text/csv;charset=utf-8,"
        + rows.map(e => e.join(",")).join("\n");

    // 3. Trigger Download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "election_results_2025.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

