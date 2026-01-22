// =====================================================================
// GLOBAL VARIABLES
// =====================================================================
const connectBtn = document.getElementById("connectWalletBtn");
const walletDisplay = document.getElementById("walletDisplay");
const submitVoteBtn = document.getElementById("submitVoteBtn");

// =====================================================================
// POPUP SYSTEM
// =====================================================================
// =====================================================================
// POPUP SYSTEM
// =====================================================================
function showPopup(title, msg, link = null, actionBtn = null) {
    const overlay = document.getElementById("popupOverlay");
    const container = document.querySelector(".popup-content");

    document.getElementById("popupTitle").textContent = title;
    document.getElementById("popupMsg").textContent = msg; // Text content for safety

    const linkContainer = document.getElementById("popupLinkContainer");

    // Clear previous dynamic elements (links/buttons)
    if (linkContainer) {
        linkContainer.innerHTML = "";

        // Add Etherscan Link
        if (link) {
            const a = document.createElement("a");
            a.href = link;
            a.target = "_blank";
            a.textContent = "View on Etherscan ↗️";
            a.className = "etherscan-link";
            linkContainer.appendChild(a);
            linkContainer.appendChild(document.createElement("br")); // Spacing
        }

        // Add Custom Action Button (e.g. Go to Results)
        if (actionBtn) {
            const btn = document.createElement("button");
            btn.textContent = actionBtn.text;
            btn.className = "action-btn"; // New class in CSS
            btn.onclick = actionBtn.onClick;
            linkContainer.appendChild(btn);

            // Hide standard Close button if we have a primary action? 
            // User requested explicit "Go to Results". 
            // We can keep the close button as an alternative or hide it.
            // Let's keep close button for "Already Voted" but maybe hide it for success to force flow?
            // User didn't specify hiding close, so we keep it.
        }
    }

    overlay.classList.remove("hidden");
}

document.getElementById("popupClose").onclick = () => {
    document.getElementById("popupOverlay").classList.add("hidden");
};

// =====================================================================
// INIT (Make it look connected)
// =====================================================================
window.addEventListener('DOMContentLoaded', () => {
    walletDisplay.innerHTML = `
        <span class="dot green"></span>
        Authenticated
    `;
    walletDisplay.style.borderColor = "#10b981";

    connectBtn.textContent = "System Ready";
    connectBtn.disabled = true;
    connectBtn.style.opacity = "0.7";
});

// =====================================================================
// CARD SELECTION
// =====================================================================
document.querySelectorAll(".candidate-card").forEach(card => {
    card.addEventListener("click", () => {
        document.querySelectorAll(".candidate-card").forEach(c => {
            c.classList.remove("selected");
            const ind = c.querySelector(".selection-indicator");
            if (ind) ind.innerHTML = '<span class="circle"></span> Select';
        });

        card.classList.add("selected");
        const radio = card.querySelector(".hidden-radio");
        if (radio) radio.checked = true;

        const indicator = card.querySelector(".selection-indicator");
        if (indicator) indicator.innerHTML = "✅ Selected";
    });
});

// =====================================================================
// SUBMIT VOTE (SMART POPUPS)
// =====================================================================
submitVoteBtn.addEventListener("click", async () => {

    const selected = document.querySelector('input[name="candidate"]:checked');

    if (!selected) {
        showPopup("No Selection", "Please select a candidate.");
        return;
    }

    const candidateId = parseInt(selected.value);

    // UI Feedback
    submitVoteBtn.textContent = "Encrypting & Submitting...";
    submitVoteBtn.disabled = true;

    try {
        const response = await fetch('/submit_vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidateId: candidateId })
        });

        const data = await response.json();

        if (data.status === "success") {
            // ✅ SUCCESS POPUP (UPDATED FLOW)
            const txHash = data.tx_hash;
            const etherscanLink = `https://sepolia.etherscan.io/tx/${txHash}`;

            showPopup(
                "Vote Successful 🎉",
                "Vote casted on blockchain successfully!",
                etherscanLink,
                {
                    text: "Go to Results →",
                    onClick: () => {
                        window.location.href = "/results";
                    }
                }
            );

            // Remove the close button to force them to go to results? 
            // Or just hide it. The user said "add a button with go to results and redirect".
            document.getElementById("popupClose").style.display = 'none';

        } else {
            // ❌ HANDLE ERRORS
            const msg = data.message || "Unknown error";

            if (msg.toLowerCase().includes("already voted")) {
                showPopup(
                    "⚠️ Already Voted",
                    "You have already voted! You cannot vote twice."
                );
            } else {
                showPopup("Submission Failed", msg);
            }
            // Ensure close button is visible for errors
            document.getElementById("popupClose").style.display = 'inline-block';

            submitVoteBtn.textContent = "Confirm & Submit Vote →";
            submitVoteBtn.disabled = false;
        }

    } catch (err) {
        console.error("Vote error:", err);
        submitVoteBtn.textContent = "Confirm & Submit Vote →";
        submitVoteBtn.disabled = false;

        showPopup("Submission Failed", err.message);
        document.getElementById("popupClose").style.display = 'inline-block';
    }
});