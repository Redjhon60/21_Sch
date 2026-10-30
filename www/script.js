// =====================================
// 1. CONFIGURATION SUPABASE
// =====================================

const SUPABASE_URL = "https://rsyslzkzddqrktkivttj.supabase.co";
const SUPABASE_KEY = "sb_publishable_kaQwfCNTwKhMR-vyrttg-g_weS7URLP";

const db = window.supabase.createClient(
  SUPABASE_URL,
  SUPABASE_KEY
);

// =====================================
// 2. ÉLÉMENTS HTML
// =====================================

const tabs = document.querySelectorAll(".tab");
const forms = document.querySelectorAll(".auth-form");
const message = document.getElementById("message");

function showForm(name) {
  forms.forEach(form => {
    form.classList.toggle("hidden", form.id !== name);
  });

  tabs.forEach(tab => {
    tab.classList.toggle("active", tab.dataset.tab === name);
    tab.setAttribute(
      "aria-selected",
      String(tab.dataset.tab === name)
    );
  });

  message.className = "message";
  message.textContent = "";
}

tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    showForm(tab.dataset.tab);
  });
});

document.querySelectorAll("[data-switch]").forEach(link => {
  link.addEventListener("click", event => {
    event.preventDefault();
    showForm(link.dataset.switch);
  });
});

function showMessage(text, type) {
  message.textContent = text;
  message.className = "message " + type;
}

function setLoading(form, loading, loadingText) {
  const button = form.querySelector('button[type="submit"]');

  if (!button) return;

  if (loading) {
    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
    button.disabled = true;
  } else {
    button.textContent =
      button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

// =====================================
// 3. CRÉATION D'UN COMPTE
// =====================================

const registerForm = document.getElementById("register");

registerForm.addEventListener("submit", async event => {
  event.preventDefault();

  const name = document.getElementById("fullName").value.trim();
  const email = document.getElementById("registerEmail")
    .value.trim().toLowerCase();
  const phone = document.getElementById("phone").value.trim();
  const password = document.getElementById("registerPassword").value;
  const confirm = document.getElementById("confirmPassword").value;
  const terms = document.getElementById("terms").checked;

  if (!name || !email || !phone) {
    showMessage("Veuillez remplir tous les champs.", "error");
    return;
  }

  if (password.length < 8) {
    showMessage(
      "Le mot de passe doit contenir au moins 8 caractères.",
      "error"
    );
    return;
  }

  if (password !== confirm) {
    showMessage(
      "Les deux mots de passe ne correspondent pas.",
      "error"
    );
    return;
  }

  if (!terms) {
    showMessage(
      "Veuillez accepter les conditions d'utilisation.",
      "error"
    );
    return;
  }

  setLoading(registerForm, true, "Création du compte...");

  try {
    const { data, error } = await db.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: name,
          phone: phone
        }
      }
    });

    if (error) throw error;

    registerForm.reset();

    if (data.session) {
      await db.auth.signOut();
    }

    document.getElementById("loginEmail").value = email;
    showForm("login");

    showMessage(
      data.session
        ? "Compte créé ! Votre demande est en attente de validation par l'administration. Vous pourrez vous connecter après approbation."
        : "Demande créée ! Vérifiez votre boîte e-mail pour confirmer votre adresse si nécessaire. Votre compte restera en attente d'approbation.",
      "success"
    );

  } catch (error) {
    console.error("Erreur inscription :", error);
    showMessage(
      error.message || "Impossible de créer le compte.",
      "error"
    );
  } finally {
    setLoading(registerForm, false);
  }
});

// =====================================
// 4. CONNEXION
// =====================================

const loginForm = document.getElementById("login");

loginForm.addEventListener("submit", async event => {
  event.preventDefault();

  const email = document.getElementById("loginEmail")
    .value.trim().toLowerCase();
  const password = document.getElementById("loginPassword").value;

  if (!email || !password) {
    showMessage(
      "Veuillez saisir votre e-mail et votre mot de passe.",
      "error"
    );
    return;
  }

  setLoading(loginForm, true, "Connexion...");

  try {
    const { data, error } = await db.auth.signInWithPassword({
      email,
      password
    });

    if (error) throw error;

    const user = data.user;

    const { data: profile, error: profileError } = await db
      .from("profiles")
      .select("full_name, role, status")
      .eq("id", user.id)
      .single();

    if (profileError || !profile) {
      await db.auth.signOut();

      showMessage(
        "Profil introuvable. Veuillez contacter l'administration.",
        "error"
      );
      return;
    }

    if (String(profile.status || "").trim().toLowerCase() !== "approved") {
      await db.auth.signOut();

      const messages = {
        Pending: "Votre compte est en attente d'approbation par l'administration.",
        Rejected: "Votre demande de compte a été refusée. Contactez l'administration.",
        Suspended: "Votre compte est suspendu. Contactez l'administration."
      };

      showMessage(
        messages[profile.status] || messages[String(profile.status || "").trim()] ||
        "Votre compte n'est pas autorisé à accéder à la plateforme.",
        "error"
      );
      return;
    }

    // Accès autorisé : ouvrir le tableau de bord
    window.location.href = "dashboard.html";

  } catch (error) {
    console.error("Erreur connexion :", error);

    showMessage(
      error.message || "Échec de la connexion. Vérifiez vos informations.",
      "error"
    );
  } finally {
    setLoading(loginForm, false);
  }
});

// =====================================
// 5. MOT DE PASSE OUBLIÉ
// =====================================

document.getElementById("forgot").addEventListener(
  "click",
  async event => {
    event.preventDefault();

    const email = document.getElementById("loginEmail")
      .value.trim().toLowerCase();

    if (!email) {
      showMessage(
        "Saisissez d'abord votre adresse e-mail dans le champ de connexion.",
        "error"
      );
      document.getElementById("loginEmail").focus();
      return;
    }

    try {
      const { error } = await db.auth.resetPasswordForEmail(email, {
        redirectTo: window.location.origin + "/reset-password.html"
      });

      if (error) throw error;

      showMessage(
        "Si cette adresse est enregistrée, vous recevrez un e-mail de réinitialisation. Vérifiez également vos spams.",
        "success"
      );

    } catch (error) {
      console.error("Erreur récupération :", error);

      showMessage(
        error.message || "Impossible d'envoyer l'e-mail de récupération.",
        "error"
      );
    }
  }
);

// UI helpers
document.querySelectorAll("[data-password]").forEach(button => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.password);
    if (!input) return;
    const visible = input.type === "text";
    input.type = visible ? "password" : "text";
    button.textContent = visible ? "Afficher" : "Masquer";
    button.setAttribute("aria-label", visible ? "Afficher le mot de passe" : "Masquer le mot de passe");
  });
});
const yearElement = document.getElementById("year");
if (yearElement) yearElement.textContent = new Date().getFullYear();
