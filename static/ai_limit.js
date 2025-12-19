async function checkAILimit(userId) {
    const userRef = firebase.firestore().collection("users").doc(userId);
    const doc = await userRef.get();

    if (!doc.exists) {
        await userRef.set({
            ai_uses: 0,
            is_subscribed: false,
            plan: "free"
        });
        return true;
    }

    const data = doc.data();

    // Unlimited for subscribed users
    if (data.is_subscribed === true) {
        return true;
    }

    // Free trial limit = 5
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
