// ===========================================================
// 1. FIREBASE CONFIG (Shared)
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

try {
    firebase.initializeApp(firebaseConfig);
}
catch (e) {
    if (!/already exists/.test(e.message)) {
        console.error('Firebase initialization error', e.stack);
    }
}
const auth = firebase.auth();

// ===========================================================
// 2. ADMIN LOGIN LOGIC
// ===========================================================
const form = document.getElementById("adminLoginForm");
const errEl = document.getElementById("err");
const loginBtn = document.getElementById("loginBtn");

// STRICT ADMIN EMAIL
const ALLOWED_ADMIN = "madhurrishis.is24@rvce.edu.in";

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errEl.style.display = 'none';
        loginBtn.textContent = "Verifying Credentials...";
        loginBtn.disabled = true;

        const email = document.getElementById("email").value.trim();
        const pw = document.getElementById("password").value;

        try {
            // 1. Check Email BEFORE Firebase Call
            if (email !== ALLOWED_ADMIN) {
                throw new Error("Access Denied: This account is not authorized for administration.");
            }

            // 2. Sign In with Firebase
            const userCredential = await auth.signInWithEmailAndPassword(email, pw);
            const user = userCredential.user;

            // 3. Get ID Token
            const idToken = await user.getIdToken();

            // 4. Send Token to Backend Admin Route
            const response = await fetch('/admin', {
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
                msg = "Invalid credentials.";
            }

            errEl.style.display = 'block';
            errEl.textContent = msg;
            loginBtn.textContent = "Authenticate";
            loginBtn.disabled = false;

            if (auth.currentUser) auth.signOut();
        }
    });
}
