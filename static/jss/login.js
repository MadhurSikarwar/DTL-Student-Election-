// ===========================================================
// 1. PASTE YOUR FIREBASE WEB CONFIG HERE
// ===========================================================
const firebaseConfig = {
    apiKey: "AIzaSyAq4oLBEpx4uYwMlhAG0hFG_RdFmZEaEA0",
    authDomain: "rvce-voting-system.firebaseapp.com",
    projectId: "rvce-voting-system",
    storageBucket: "rvce-voting-system.firebasestorage.app",
    messagingSenderId: "461777093514",
    appId: "1:461777093514:web:4838fda3bc935db2e67e73",
    measurementId: "G-YQTTLVDD76"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// ===========================================================
// 2. LOGIN LOGIC
// ===========================================================
const form = document.getElementById("loginForm");
const errEl = document.getElementById("err");
const loginBtn = document.getElementById("loginBtn");

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (errEl) errEl.style.display = 'none';
        if (loginBtn) {
            loginBtn.textContent = "Verifying...";
            loginBtn.disabled = true;
        }

        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");

        const email = emailInput ? emailInput.value.trim() : "";
        const pw = passwordInput ? passwordInput.value : "";

        try {
            // 1. Sign In with Firebase
            const userCredential = await auth.signInWithEmailAndPassword(email, pw);
            const user = userCredential.user;

            // 2. Check 2FA (Email Verification)
            if (!user.emailVerified) {
                throw new Error("Please verify your email address first.");
            }

            // 3. Domain Check (Extra Layer)
            if (!user.email.endsWith("@rvce.edu.in")) {
                throw new Error("Unauthorized domain.");
            }

            // 4. Get ID Token to send to Backend
            const idToken = await user.getIdToken();

            // 5. Send Token to Python Backend
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ idToken: idToken })
            });

            const data = await response.json();

            if (data.status === 'success') {
                window.location.href = data.redirect;
            } else {
                throw new Error(data.message);
            }

        } catch (error) {
            console.error(error);
            let msg = error.message;
            if (error.code === 'auth/wrong-password' || error.code === 'auth/user-not-found') {
                msg = "Invalid email or password.";
            }

            if (errEl) {
                errEl.style.display = 'block';
                errEl.textContent = msg;
            }
            if (loginBtn) {
                loginBtn.textContent = "Login";
                loginBtn.disabled = false;
            }

            // If email isn't verified, log them out immediately from Firebase
            if (msg.includes("verify")) {
                auth.signOut();
            }
        }
    });
}

// ===========================================================
// 3. FORGOT PASSWORD LOGIC
// ===========================================================
const forgotPasswordModal = document.getElementById('forgotPasswordModal');
const resetEmailInput = document.getElementById('resetEmail');
const sendResetBtn = document.getElementById('sendResetBtn');
const cancelResetBtn = document.getElementById('cancelResetBtn');
const resetMsg = document.getElementById('resetMsg');
const forgotPasswordBtn = document.getElementById('forgotPasswordBtn');

if (forgotPasswordBtn && forgotPasswordModal) {
    // Show modal
    forgotPasswordBtn.addEventListener('click', (e) => {
        e.preventDefault();
        forgotPasswordModal.style.display = 'flex';
        if (resetEmailInput) resetEmailInput.value = '';
        if (resetMsg) resetMsg.style.display = 'none';
    });

    // Close modal
    if (cancelResetBtn) {
        cancelResetBtn.addEventListener('click', () => {
            forgotPasswordModal.style.display = 'none';
        });
    }

    // Close on outside click
    forgotPasswordModal.addEventListener('click', (e) => {
        if (e.target === forgotPasswordModal) {
            forgotPasswordModal.style.display = 'none';
        }
    });

    // Send reset email
    if (sendResetBtn) {
        sendResetBtn.addEventListener('click', async () => {
            const email = resetEmailInput ? resetEmailInput.value.trim() : "";

            if (!email) {
                showResetError('Please enter your email address.');
                return;
            }

            if (!email.endsWith('@rvce.edu.in')) {
                showResetError('Please use your RVCE email address.');
                return;
            }

            sendResetBtn.textContent = 'Sending...';
            sendResetBtn.disabled = true;

            try {
                await auth.sendPasswordResetEmail(email);

                if (resetMsg) {
                    resetMsg.style.display = 'block';
                    resetMsg.style.background = '#e8f5e9';
                    resetMsg.style.color = '#2e7d32';
                    resetMsg.textContent = '✅ Password reset email sent! Check your inbox.';
                }

                if (resetEmailInput) resetEmailInput.value = '';

                // Close modal after 3 seconds
                setTimeout(() => {
                    forgotPasswordModal.style.display = 'none';
                    if (resetMsg) resetMsg.style.display = 'none';
                }, 3000);

            } catch (error) {
                console.error('Password reset error:', error);

                let errorMessage = 'Failed to send reset email. Please try again.';
                if (error.code === 'auth/user-not-found') {
                    errorMessage = 'No account found with this email address.';
                } else if (error.code === 'auth/invalid-email') {
                    errorMessage = 'Invalid email address.';
                } else if (error.code === 'auth/too-many-requests') {
                    errorMessage = 'Too many requests. Please try again later.';
                }

                showResetError(errorMessage);
            } finally {
                sendResetBtn.textContent = 'Send Reset Link';
                sendResetBtn.disabled = false;
            }
        });
    }

    // Allow Enter key to send reset email
    if (resetEmailInput) {
        resetEmailInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendResetBtn.click();
            }
        });
    }
}

function showResetError(msg) {
    if (resetMsg) {
        resetMsg.style.display = 'block';
        resetMsg.style.background = '#ffebee';
        resetMsg.style.color = '#c62828';
        resetMsg.textContent = msg;
    }
}
