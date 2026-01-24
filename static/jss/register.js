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
// 2. REGISTRATION LOGIC
// ===========================================================
const form = document.getElementById("registerForm");
const errEl = document.getElementById("err");
const successEl = document.getElementById("successMsg");
const regBtn = document.getElementById("regBtn");

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errEl.style.display = 'none';
        successEl.style.display = 'none';
        regBtn.disabled = true;
        regBtn.textContent = "Processing...";

        const email = document.getElementById("email").value.trim();
        const pw = document.getElementById("password").value;
        const cpw = document.getElementById("confirm_password").value;

        // 1. Local Validation
        if (!email.endsWith("@rvce.edu.in")) {
            showError("Only @rvce.edu.in emails are allowed.");
            resetBtn();
            return;
        }
        if (pw !== cpw) {
            showError("Passwords do not match.");
            resetBtn();
            return;
        }

        try {
            // 2. Create User in Firebase
            const userCredential = await auth.createUserWithEmailAndPassword(email, pw);
            const user = userCredential.user;

            // 3. Send Verification Email
            await user.sendEmailVerification();

            // 4. Success UI
            successEl.style.display = 'block';
            regBtn.textContent = "Email Sent ✓";

            await auth.signOut();

        } catch (error) {
            console.error(error);
            if (error.code === 'auth/email-already-in-use') {
                showError("This email is already registered.");
            } else if (error.code === 'auth/weak-password') {
                showError("Password should be at least 6 characters.");
            } else {
                showError(error.message);
            }
            resetBtn();
        }
    });
}

function showError(msg) {
    if (errEl) {
        errEl.style.display = 'block';
        errEl.textContent = msg;
    }
}

function resetBtn() {
    if (regBtn) {
        regBtn.disabled = false;
        regBtn.textContent = "Register Account";
    }
}
