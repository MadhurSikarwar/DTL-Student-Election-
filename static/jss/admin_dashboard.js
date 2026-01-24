async function confirmNewElection() {
    if (!confirm("⚠️ CRITICAL ACTION ⚠️\n\nAre you sure you want to END the current election and START A NEW one?\n\n- This will archive the current vote list.\n- All students will be allowed to vote again in the new cycle.\n- This action cannot be undone.")) {
        return;
    }

    const btn = document.getElementById("newElectionBtn");
    btn.disabled = true;
    btn.textContent = "Processing...";

    try {
        const response = await fetch('/admin/start-new-election', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert("✅ Success! New Election Cycle Started.");
            window.location.reload();
        } else {
            alert("Error: " + data.message);
            btn.disabled = false;
            btn.textContent = "⚠️ Start New Election";
        }
    } catch (e) {
        alert("Request Failed: " + e);
        btn.disabled = false;
        btn.textContent = "⚠️ Start New Election";
    }
}

// CANDIDATE MANAGEMENT LOGIC
document.getElementById("addCandidateForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    try {
        const response = await fetch('/admin/candidates/add', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
            alert("✅ Candidate Added Successfully!");
            window.location.reload();
        } else {
            alert("❌ Error: " + data.message);
        }
    } catch (err) {
        alert("Request Failed: " + err);
    }
});

// ELECTION CONTROL LOGIC
async function loadElectionStatus() {
    try {
        const response = await fetch('/admin/election/get-status');
        const data = await response.json();

        if (data.status === 'success') {
            // Update pause status display
            const statusDiv = document.getElementById('pauseStatusDisplay');
            if (data.is_paused) {
                statusDiv.style.background = 'rgba(255,0,0,0.1)';
                statusDiv.style.borderColor = 'var(--accent-red)';
                statusDiv.style.color = 'var(--accent-red)';
                statusDiv.textContent = '⏸️ Voting is PAUSED';
            } else {
                statusDiv.style.background = 'rgba(0,255,0,0.1)';
                statusDiv.style.borderColor = '#10b981';
                statusDiv.style.color = '#10b981';
                statusDiv.textContent = '▶️ Voting is ACTIVE';
            }

            // Update deadline display
            const deadlineDiv = document.getElementById('deadlineDisplay');
            if (data.deadline) {
                const dt = new Date(data.deadline);
                const options = {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                };
                deadlineDiv.textContent = `⏰ Ends: ${dt.toLocaleString('en-US', options)}`;
                deadlineDiv.style.color = 'var(--accent-blue)';
            } else {
                deadlineDiv.textContent = 'No deadline set';
                deadlineDiv.style.color = 'var(--text-muted)';
            }
        }
    } catch (err) {
        console.error("Failed to load election status:", err);
    }
}

async function pauseElection() {
    if (!confirm("Pause voting immediately?")) return;

    try {
        const response = await fetch('/admin/election/pause', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            alert("⏸️ Election PAUSED");
            loadElectionStatus();
        } else {
            alert("Error: " + data.message);
        }
    } catch (err) {
        alert("Request failed: " + err);
    }
}

async function resumeElection() {
    if (!confirm("Resume voting?")) return;

    try {
        const response = await fetch('/admin/election/resume', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            alert("▶️ Election RESUMED");
            loadElectionStatus();
        } else {
            alert("Error: " + data.message);
        }
    } catch (err) {
        alert("Request failed: " + err);
    }
}

async function setDeadline() {
    const deadlineInput = document.getElementById('deadlineInput').value;
    if (!deadlineInput) {
        alert("Please select a date and time");
        return;
    }

    // Convert to ISO format for backend
    const deadline = new Date(deadlineInput).toISOString();

    try {
        const response = await fetch('/admin/election/set-deadline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ deadline: deadline })
        });
        const data = await response.json();
        if (data.status === 'success') {
            alert("⏰ Deadline set successfully!");
            loadElectionStatus();
        } else {
            alert("Error: " + data.message);
        }
    } catch (err) {
        alert("Request failed: " + err);
    }
}

// Load status on page load
window.addEventListener('DOMContentLoaded', loadElectionStatus);

async function deleteCandidate(id) {
    if (!confirm("Are you sure you want to delete this candidate?")) return;

    const formData = new FormData();
    formData.append("id", id);

    try {
        const response = await fetch('/admin/candidates/delete', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
            alert("🗑️ Candidate Deleted.");
            window.location.reload();
        } else {
            alert("❌ Error: " + data.message);
        }
    } catch (err) {
        alert("Request Failed: " + err);
    }
}

// Manifesto Toggle Logic
function toggleManifestoInput(type) {
    const textGroup = document.getElementById('manifestoTextInput');
    const fileGroup = document.getElementById('manifestoFileInput');
    const textArea = document.getElementById('manifestoText');
    const fileInput = document.getElementById('manifestoFile');

    if (type === 'text') {
        textGroup.style.display = 'block';
        fileGroup.style.display = 'none';
        textArea.required = true;
        fileInput.required = false;
        fileInput.value = '';
    } else {
        textGroup.style.display = 'none';
        fileGroup.style.display = 'flex';
        textArea.required = false;
        fileInput.required = true;
    }
}
