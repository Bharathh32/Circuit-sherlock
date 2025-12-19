async function checkAILimit(userId) {
    const userRef = firebase.firestore().collection("users").doc(userId);
    const doc = await userRef.get({ source: "server" });

    // First time user
    if (!doc.exists) {
        await userRef.set({
            ai_uses: 0,
            is_subscribed: false,
            plan: "free",
            role: "user"
        });
        return true;
    }

    const data = doc.data();

    // Admin → unlimited
    if (data.role === "admin") return true;

    // Subscription expiry check
    if (data.is_subscribed === true && data.subscription_end) {
        const now = new Date();
        const expiry = data.subscription_end.toDate();

        if (now < expiry) {
            return true; // still active
        } else {
            // expired
            await userRef.update({
                is_subscribed: false,
                plan: "expired"
            });
            showLimitPopup();
            return false;
        }
    }

    // Free trial limit
    if (data.ai_uses >= 5) {
        showLimitPopup();
        return false;
    }

    return true;
}

async function incrementAIUse(userId) {
    const userRef = firebase.firestore().collection("users").doc(userId);
    await userRef.update({
        ai_uses: firebase.firestore.FieldValue.increment(1)
    });
}
