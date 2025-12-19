// // PANEL SWITCH
// const signUpButton = document.getElementById('signUp');
// const signInButton = document.getElementById('signIn');
// const container = document.getElementById('container');

// function clearSessionCookie() {
//     document.cookie = "session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
// }

// signUpButton.addEventListener('click', () => {
//     container.classList.add("right-panel-active");
// });

// signInButton.addEventListener('click', () => {
//     container.classList.remove("right-panel-active");
// });

// // -------------------------------
// // EMAIL / PASSWORD SIGN UP
// // -------------------------------
// document.getElementById("signupForm").addEventListener("submit", function (e) {
//     e.preventDefault();

//     const name = e.target.name.value;
//     const email = e.target.email.value;
//     const password = e.target.password.value;

//     clearSessionCookie();

//     firebase.auth().createUserWithEmailAndPassword(email, password)
//         .then(async userCredential => {
//             const user = userCredential.user;
//             await user.updateProfile({ displayName: name });

//             const idToken = await user.getIdToken(true);

//             await fetch("/sessionLogin", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ idToken: idToken })
//             });

//             alert("Account created successfully!");
//             window.location.href = "/";
//         })
//         .catch(error => {
//             alert(error.message);
//         });
// });

// // -------------------------------
// // EMAIL / PASSWORD LOGIN
// // -------------------------------
// document.getElementById("loginForm").addEventListener("submit", function (e) {
//     e.preventDefault();

//     const email = e.target.email.value;
//     const password = e.target.password.value;

//     clearSessionCookie(); // remove old admin session

//     firebase.auth().signInWithEmailAndPassword(email, password)
//         .then(async (userCredential) => {
//             const user = userCredential.user;

//             // Force refresh ID token
//             const idToken = await user.getIdToken(true);

//             // Send token to Flask to create session cookie
//             await fetch("/sessionLogin", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ idToken: idToken })
//             });

//             alert("Login successful!");
//             window.location.href = "/";
//         })
//         .catch(error => {
//             alert(error.message);
//         });
// });


// // -------------------------------
// // CHECK LOGIN STATE
// // -------------------------------
// firebase.auth().onAuthStateChanged(user => {
//     if (user) {
//         console.log("Logged in:", user.email);
//     }
// });
// ===============================
// SLIDING PANEL LOGIC
// ===============================
const signUpButton = document.getElementById("signUp");
const signInButton = document.getElementById("signIn");
const container = document.getElementById("container");

// Clear old Flask session cookie
function clearSessionCookie() {
    document.cookie =
        "session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
}

// Slide to SIGN UP
signUpButton.addEventListener("click", () => {
    clearSessionCookie();
    container.classList.add("right-panel-active");
});

// Slide to SIGN IN
signInButton.addEventListener("click", () => {
    clearSessionCookie();
    container.classList.remove("right-panel-active");
});

// ===============================
// FIREBASE INIT (ONLY ONCE)
// ===============================
if (!firebase.apps.length) {
    firebase.initializeApp({
        apiKey: "AIzaSyDKW_hw5R3u-dOZDlLFe01pkG0nd85M7x4",
        authDomain: "circuit-sherlock.firebaseapp.com",
        projectId: "circuit-sherlock",
    });
}

const auth = firebase.auth();
const db = firebase.firestore();

// ===============================
// SIGN UP (AUTH + FIRESTORE + SESSION)
// ===============================
document.getElementById("signupForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = e.target.name.value.trim();
    const email = e.target.email.value.trim();
    const password = e.target.password.value;

    if (!name || !email || !password) {
        alert("All fields are required");
        return;
    }

    clearSessionCookie();

    try {
        // 1️⃣ Create Firebase Auth user
        const userCredential =
            await auth.createUserWithEmailAndPassword(email, password);

        const user = userCredential.user;

        // 2️⃣ Update display name
        await user.updateProfile({ displayName: name });

        // 3️⃣ Store user in Firestore (EXISTING CODE)
        await db.collection("users")
            .doc(user.uid)
            .set({
                username: name,
                email: email,
                role: "user",
                createdAt: firebase.firestore.FieldValue.serverTimestamp()
            });

        // ===============================
        // 🔥 ADDED CODE (USAGE LIMIT INIT)
        // ===============================
        await db.collection("login_details")
            .doc(user.uid)
            .set({
                email: email,
                role: "user",
                usageCount: 0,
                isPremium: false,
                createdAt: firebase.firestore.FieldValue.serverTimestamp()
            });

        // 4️⃣ Create Flask session cookie
        const idToken = await user.getIdToken(true);

        await fetch("/sessionLogin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idToken })
        });

        alert("Account created successfully!");
        window.location.href = "/";

    } catch (error) {
        console.error("Signup error:", error);
        alert(error.message);
    }
});

// ===============================
// SIGN IN (AUTH + SESSION)
// ===============================
document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = e.target.email.value.trim();
    const password = e.target.password.value;

    if (!email || !password) {
        alert("Email and password are required");
        return;
    }

    clearSessionCookie();

    try {
        // 1️⃣ Login
        const userCredential =
            await auth.signInWithEmailAndPassword(email, password);

        const user = userCredential.user;

        // 2️⃣ Refresh token
        const idToken = await user.getIdToken(true);

        // 3️⃣ Create Flask session
        await fetch("/sessionLogin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idToken })
        });

        alert("Login successful!");
        window.location.href = "/";

    } catch (error) {
        console.error("Login error:", error);
        alert(error.message);
    }
});

// ===============================
// AUTH STATE DEBUG (OPTIONAL)
// ===============================
auth.onAuthStateChanged((user) => {
    if (user) {
        console.log("Logged in:", user.uid, user.email);
    } else {
        console.log("No user logged in");
    }
});