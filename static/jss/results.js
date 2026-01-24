// =====================================================
// PROVIDER (PUBLIC SEPOLIA RPC)
// =====================================================
const RPC_URL = "https://ethereum-sepolia.publicnode.com";
let provider;

try {
    if (ethers.JsonRpcProvider) {
        provider = new ethers.JsonRpcProvider(RPC_URL);
    } else if (ethers.providers && ethers.providers.JsonRpcProvider) {
        provider = new ethers.providers.JsonRpcProvider(RPC_URL);
    } else {
        console.error("Ethers.js not loaded.");
    }
} catch (e) {
    console.error("Provider Init Error:", e);
}

// =====================================================
// CHART JS SETUP
// =====================================================
let voteChart;

function initChart(candidates) {
    const ctx = document.getElementById('voteChart');
    if (!ctx) return;

    voteChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: candidates.map(c => c.name),
            datasets: [{
                label: 'Votes Cast',
                data: candidates.map(() => 0),
                backgroundColor: 'rgba(99, 102, 241, 0.5)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: {
                        color: '#94a3b8',
                        stepSize: 1,
                        precision: 0
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: { labels: { color: '#e2e8f0' } }
            }
        }
    });
}

// =====================================================
// FETCH VOTES (DYNAMIC)
// =====================================================
async function fetchVotes() {
    try {
        const candidates = window.ALL_CANDIDATES || [];
        if (candidates.length === 0) return null;

        // 1. Get Offsets
        const offsetRes = await fetch('/api/offsets');
        const offsetData = await offsetRes.json();
        // Assuming offsets are stored by ID or index. 
        // Backend `get_current_offsets` logic returns array [0,0,0,0,0,0] (fixed size 6 currently).
        // WARNING: If we have >6 candidates, offsets logic in backend needs fix.
        // For now, we'll map offsets safely.
        const offsets = offsetData.offsets || [];

        // 2. Blockchain Call
        const contract = new ethers.Contract(window.CONTRACT_ADDRESS, window.CONTRACT_ABI, provider);

        // Map candidates to promises with error handling
        const votePromises = candidates.map(async c => {
            try {
                const v = await contract.getVotes(c.id);
                return v;
            } catch (e) {
                console.warn(`Failed to fetch votes for candidate ${c.id} (likely contract limit):`, e);
                return 0; // Return 0 if contract doesn't recognize ID
            }
        });

        const rawVotes = await Promise.all(votePromises);

        // 3. Process Votes
        return candidates.map((c, i) => {
            const raw = Number(rawVotes[i]);
            const offset = offsets[i] || 0;
            const final = raw - offset;
            return Math.max(0, final);
        });

    } catch (err) {
        console.error("Blockchain Fetch Error:", err);
        return null; // Keep OLD data on error
    }
}

// =====================================================
// UPDATE UI
// =====================================================
function updateUI(votes) {
    if (!votes) return;

    const candidates = window.ALL_CANDIDATES || [];
    const total = votes.reduce((a, b) => a + b, 0);

    // Update Cards
    candidates.forEach((c, i) => {
        const voteCount = votes[i];

        // Update Number
        const countSpan = document.getElementById(`v${c.id}`);
        if (countSpan) countSpan.textContent = voteCount;

        // Update Bar
        const card = document.getElementById(`card${c.id}`);
        if (card) {
            const percent = total ? Math.round((voteCount / total) * 100) : 0;
            const fill = card.querySelector(".fill");
            if (fill) fill.style.width = percent + "%";
        }
    });

    // Update Chart
    if (voteChart) {
        voteChart.data.datasets[0].data = votes;
        voteChart.update();
    }

    determineWinner(votes, candidates);
}

// =====================================================
// WINNER LOGIC
// =====================================================
function determineWinner(votes, candidates) {
    const winnerText = document.getElementById("winnerText");
    const max = Math.max(...votes);

    // Reset styles
    candidates.forEach(c => {
        const card = document.getElementById(`card${c.id}`);
        if (card) card.classList.remove("leader");
    });

    if (max === 0) {
        winnerText.textContent = "Waiting for votes...";
        return;
    }

    // Find winners
    const winners = candidates.filter((_, i) => votes[i] === max);

    if (winners.length > 1) {
        winnerText.textContent = "Current Tie: " + winners.map(w => w.name).join(" & ");
        winners.forEach(w => {
            const card = document.getElementById(`card${w.id}`);
            if (card) card.classList.add("leader");
        });
    } else {
        winnerText.textContent = "Winner: " + winners[0].name;
        const card = document.getElementById(`card${winners[0].id}`);
        if (card) card.classList.add("leader");
    }
}

// =====================================================
// AUTO REFRESH
// =====================================================
async function refresh() {
    const votes = await fetchVotes();
    if (votes) updateUI(votes);
}

// Initialize
if (window.ALL_CANDIDATES) {
    initChart(window.ALL_CANDIDATES);
    refresh();
    setInterval(refresh, 5000);
}

// =====================================================
// CSV EXPORT LOGIC
// =====================================================
function downloadCSV() {
    const candidates = window.ALL_CANDIDATES || [];
    const rows = [["Candidate Name", "Position", "Total Votes"]];

    candidates.forEach(c => {
        const countSpan = document.getElementById(`v${c.id}`);
        const count = countSpan ? countSpan.textContent : "0";
        rows.push([c.name, c.position, count]);
    });

    let csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "election_results_2025.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Winner Background Script
const box = document.getElementById("winnerBox");
if (box) {
    box.style.backgroundImage = `url('/static/images/winner-bg-premium.png')`;
}

