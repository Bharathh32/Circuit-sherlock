// nav_auth.js (updated for user-specific menu + profile + results)

(async function () {
  function $(id) { return document.getElementById(id); }
  function safeHtml(text) {
    return text ? String(text)
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;") : "";
  }

  /* ------------------------
     LOGGED OUT MENU
  -------------------------*/
  function renderLoggedOut() {
    const icon = $('navProfileIcon');
    const hello = $('navHello');
    const controls = $('navControls');

    if (icon) icon.classList.add('text-white');
    if (hello) {
      hello.classList.add('d-none');
      hello.textContent = '';
      hello.classList.add('text-white');
    }

    if (controls) {
      controls.innerHTML = `
        <a href="/auth" class="btn btn-outline-light me-2 fw-bold">Login</a>
        <a href="/auth#signup" class="btn fw-bold text-white" style="background:#ff3b3b;">Sign Up</a>
      `;
    }
  }

  /* ------------------------
     LOGGED IN MENU
  -------------------------*/
  function renderLoggedIn(username, isAdmin) {
    const icon = $('navProfileIcon');
    const hello = $('navHello');
    const controls = $('navControls');

    if (icon) icon.classList.add('text-white');

    if (hello) {
      hello.classList.remove('d-none');
      hello.textContent = `Hello, ${safeHtml(username)}`;
      hello.classList.add('text-white');
    }

    /* ⭐ ADMIN MENU = ONLY PROFILE */
    const adminMenu = `
      <li><a class="dropdown-item text-white bg-dark" href="/admin/profile">👤 Profile</a></li>
      <li><hr class="dropdown-divider text-white"></li>
    `;

    /* ⭐ USER MENU = PROFILE + MY RESULTS */
    const userMenu = `
      <li><a class="dropdown-item text-white bg-dark" href="/profile">👤 Profile</a></li>
      <li><hr class="dropdown-divider text-white"></li>
    `;

    const finalMenu = isAdmin ? adminMenu : userMenu;

    controls.innerHTML = `
      <div class="dropdown">
        <button class="btn btn-sm dropdown-toggle"
           
            type="button" id="navMenuBtn" data-bs-toggle="dropdown">
          <i id="navProfileIcon" class="bi bi-person-circle fs-2 text-white"></i>
        </button>

        <ul class="dropdown-menu dropdown-menu-end bg-dark" aria-labelledby="navMenuBtn">
            ${finalMenu}
            <li><button id="logoutBtn" class="dropdown-item text-danger bg-dark">Logout</button></li>
        </ul>
      </div>
    `;

    setTimeout(() => {
      const logoutBtn = $('logoutBtn');
      if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
          await firebase.auth().signOut();
          window.location.href = "/";
        });
      }
    }, 80);
  }

  /* ------------------------
     WAIT FOR FIREBASE
  -------------------------*/
  function waitForFirebase(ms = 3000) {
    return new Promise((resolve, reject) => {
      const start = Date.now();
      (function check() {
        if (window.firebase && firebase.apps !== undefined) return resolve();
        if (Date.now() - start > ms) return reject("firebase not loaded");
        setTimeout(check, 50);
      })();
    });
  }

  /* ------------------------
     MAIN
  -------------------------*/
  try {
    await waitForFirebase();

    firebase.auth().onAuthStateChanged(async (user) => {
      if (!$('navAuth') || !$('navProfileIcon') || !$('navHello') || !$('navControls'))
        return console.warn("Navbar IDs missing");

      if (!user) return renderLoggedOut();

      const username = user.displayName || user.email.split("@")[0];

      let isAdmin = false;
      try {
        const adminDoc = await firebase.firestore().collection("admins").doc(user.uid).get();
        isAdmin = adminDoc.exists;
      } catch {}

      renderLoggedIn(username, isAdmin);
    });

  } catch (err) {
    console.error("nav_auth init error:", err);
    renderLoggedOut();
  }

})();
