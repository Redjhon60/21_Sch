(() => {
    "use strict";

    const SUPABASE_URL = "https://rsyslzkzddqrktkivttj.supabase.co";
    const SUPABASE_KEY = "sb_publishable_kaQwfCNTwKhMR-vyrttg-g_weS7URLP";
    const $ = id => document.getElementById(id);
    const db = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

    let school = null;
    let years = [];
    let users = [];
    let currentUser = null;
    let saving = false;

    function message(text = "", type = "") {
        $("message").textContent = text;
        $("message").className = "message" + (type ? " " + type : "");
    }

    function yearMessage(text = "", type = "") {
        $("yearMessage").textContent = text;
        $("yearMessage").className = "message" + (type ? " " + type : "");
    }

    function setSaving(value) {
        saving = value;
        document.querySelectorAll("button").forEach(button => {
            button.disabled = value;
        });
    }

    async function loadCurrentUser() {
        const authResult = await db.auth.getUser();
        if (authResult.error) throw authResult.error;
        if (!authResult.data.user) throw new Error("Connexion requise.");

        const profileResult = await db
            .from("profiles")
            .select("*")
            .eq("id", authResult.data.user.id)
            .maybeSingle();

        if (profileResult.error) throw profileResult.error;
        if (!profileResult.data) throw new Error("Profil utilisateur introuvable.");

        currentUser = {
            ...profileResult.data,
            id: authResult.data.user.id,
            auth_email: authResult.data.user.email || ""
        };

        const approved = String(currentUser.status || "").trim().toLowerCase() === "approved";
        const totalAccess = String(currentUser.role || "").trim().toLowerCase() === "access total";

        if (!approved || !totalAccess) {
            throw new Error("Access total requis pour modifier les parametres.");
        }
    }

    async function loadSchoolSettings() {
        const result = await db
            .from("school_settings")
            .select("*")
            .order("updated_at", { ascending: false })
            .limit(1)
            .maybeSingle();

        if (result.error) throw result.error;
        school = result.data || null;
    }

    async function loadAcademicYears() {
        const result = await db
            .from("academic_years")
            .select("*")
            .order("start_date", { ascending: false });

        if (result.error) throw result.error;
        years = result.data || [];
    }

    async function loadUsersSafely() {
        const result = await db.from("profiles").select("*");
        if (result.error) {
            console.warn("Utilisateurs non charges:", result.error);
            users = [];
            return;
        }

        users = (result.data || []).sort((a, b) => {
            const aName = String(a.full_name || a.name || a.email || "");
            const bName = String(b.full_name || b.name || b.email || "");
            return aName.localeCompare(bName, "fr");
        });
    }

    function fillSchoolForm() {
        const value = school || {};
        $("schoolId").value = value.id || "";
        $("schoolName").value = value.school_name || "Etablissement Le Schema";
        $("schoolNameAr").value = value.school_name_ar || "";
        $("directorName").value = value.director_name || "";
        $("city").value = value.city || "";
        $("phone").value = value.phone || "";
        $("email").value = value.email || "";
        $("website").value = value.website || "";
        $("address").value = value.address || "";
        $("studentPrefix").value = value.student_prefix || "ELV";
        $("receiptPrefix").value = value.receipt_prefix || "REC";
    }

    function renderYears() {
        $("yearsTable").replaceChildren();

        if (!years.length) {
            const row = $("yearsTable").insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.className = "empty-state";
            cell.textContent = "Aucune annee scolaire configuree.";
            return;
        }

        for (const year of years) {
            const row = $("yearsTable").insertRow();
            row.insertCell().textContent = year.label;
            row.insertCell().textContent = year.start_date;
            row.insertCell().textContent = year.end_date;

            const statusCell = row.insertCell();
            const badge = document.createElement("span");
            badge.className = year.active ? "active-badge" : "inactive-badge";
            badge.textContent = year.active ? "Active" : "Inactive";
            statusCell.append(badge);

            const actionCell = row.insertCell();
            if (year.active) {
                actionCell.textContent = "—";
            } else {
                const activateButton = document.createElement("button");
                activateButton.type = "button";
                activateButton.className = "row-action";
                activateButton.textContent = "Activer";
                activateButton.addEventListener("click", () => activateYear(year.id));
                actionCell.append(activateButton);
            }
        }
    }

    function option(value, label, selected) {
        const item = document.createElement("option");
        item.value = value;
        item.textContent = label;
        item.selected = value === selected;
        return item;
    }

    function renderUsers() {
        $("usersTable").replaceChildren();
        if (!users.length) {
            const row = $("usersTable").insertRow();
            const cell = row.insertCell();
            cell.colSpan = 6;
            cell.className = "empty-state";
            cell.textContent = "Aucune demande d'acces.";
            return;
        }
        const sorted = [...users].sort((a,b) => {
            const pendingA = String(a.status).toLowerCase() === "pending" ? 0 : 1;
            const pendingB = String(b.status).toLowerCase() === "pending" ? 0 : 1;
            return pendingA - pendingB || String(a.full_name||"").localeCompare(String(b.full_name||""),"fr");
        });
        for (const user of sorted) {
            const row = $("usersTable").insertRow();
            const identity = row.insertCell();
            const name = document.createElement("strong");
            name.textContent = user.full_name || "Utilisateur";
            const id = document.createElement("small");
            id.textContent = user.id;
            identity.append(name, document.createElement("br"), id);
            row.insertCell().textContent = user.phone || "—";

            const roleSelect = document.createElement("select");
            ["Parent","Professeur","Administrative","Access total"].forEach(v => roleSelect.append(option(v,v,user.role)));
            row.insertCell().append(roleSelect);

            const statusSelect = document.createElement("select");
            ["Pending","Approved","Rejected","Suspended"].forEach(v => statusSelect.append(option(v,v,user.status)));
            row.insertCell().append(statusSelect);

            const finance = document.createElement("input");
            finance.type = "checkbox";
            finance.className = "toggle";
            finance.checked = user.can_manage_finance === true;
            const financeCell = row.insertCell();
            financeCell.append(finance);

            const save = document.createElement("button");
            save.type = "button";
            save.className = "primary-btn row-action";
            save.textContent = String(user.status).toLowerCase() === "pending" ? "Valider la demande" : "Mettre a jour";
            const locked = user.id === currentUser.id;
            roleSelect.disabled = statusSelect.disabled = finance.disabled = save.disabled = locked;
            if (locked) save.textContent = "Votre compte";
            save.onclick = async () => {
                save.disabled = true;
                try {
                    await loadCurrentUser();
                    const role = roleSelect.value;
                    const status = statusSelect.value;
                    const canFinance = role === "Access total" ? true : finance.checked;
                    const result = await db.rpc("admin_review_access_request", {
                        p_target_user: user.id,
                        p_role: role,
                        p_status: status,
                        p_can_manage_finance: canFinance
                    });
                    if (result.error) throw result.error;
                    user.role = role; user.status = status; user.can_manage_finance = canFinance;
                    message("Acces utilisateur mis a jour.", "success");
                    renderUsers();
                } catch (error) {
                    message("Erreur : " + error.message, "error");
                    save.disabled = false;
                }
            };
            row.insertCell().append(save);
        }
    }

    function renderAll() {
        fillSchoolForm();
        renderYears();
        renderUsers();
    }

    async function loadAll() {
        message("Chargement...");
        try {
            await loadCurrentUser();
            await Promise.all([
                loadSchoolSettings(),
                loadAcademicYears(),
                loadUsersSafely()
            ]);
            renderAll();
            message("");
        } catch (error) {
            console.error(error);
            message("Erreur : " + error.message, "error");
        }
    }

    async function saveSchool(event) {
        event.preventDefault();
        if (saving) return;
        setSaving(true);
        message("Enregistrement...");

        try {
            await loadCurrentUser();

            const record = {
                school_name: $("schoolName").value.trim(),
                school_name_ar: $("schoolNameAr").value.trim() || null,
                director_name: $("directorName").value.trim() || null,
                city: $("city").value.trim() || null,
                phone: $("phone").value.trim() || null,
                email: $("email").value.trim() || null,
                website: $("website").value.trim() || null,
                address: $("address").value.trim() || null,
                student_prefix: $("studentPrefix").value.trim().toUpperCase() || "ELV",
                receipt_prefix: $("receiptPrefix").value.trim().toUpperCase() || "REC",
                updated_by: currentUser.id,
                updated_at: new Date().toISOString()
            };

            if (!record.school_name) throw new Error("Le nom de l'etablissement est obligatoire.");

            let result;
            if ($("schoolId").value) {
                result = await db
                    .from("school_settings")
                    .update(record)
                    .eq("id", $("schoolId").value)
                    .select("*")
                    .maybeSingle();
            } else {
                result = await db
                    .from("school_settings")
                    .insert(record)
                    .select("*")
                    .maybeSingle();
            }

            if (result.error) throw result.error;
            if (!result.data) {
                throw new Error("Aucune ligne enregistree. Verifiez les policies school_settings.");
            }

            school = result.data;
            fillSchoolForm();
            message("Parametres de l'etablissement enregistres.", "success");
        } catch (error) {
            console.error(error);
            message("Erreur : " + error.message, "error");
        } finally {
            setSaving(false);
        }
    }

    async function activateYear(id) {
        if (saving) return;
        setSaving(true);
        message("Activation de l'annee scolaire...");

        try {
            await loadCurrentUser();

            const deactivateResult = await db
                .from("academic_years")
                .update({ active: false })
                .eq("active", true);

            if (deactivateResult.error) throw deactivateResult.error;

            const activateResult = await db
                .from("academic_years")
                .update({ active: true })
                .eq("id", id)
                .select("id")
                .maybeSingle();

            if (activateResult.error) throw activateResult.error;
            if (!activateResult.data) throw new Error("L'annee scolaire n'a pas ete activee.");

            await loadAcademicYears();
            renderYears();
            message("Annee scolaire activee.", "success");
        } catch (error) {
            console.error(error);
            message("Erreur : " + error.message, "error");
        } finally {
            setSaving(false);
        }
    }

    function openResetDataDialog() {
        $("resetDataForm").reset();
        $("resetDataMessage").textContent = "";
        $("resetDataDialog").showModal();
    }

    async function resetApplicationData(event) {
        event.preventDefault();
        const phrase = $("resetDataConfirmation").value.trim();
        if (phrase !== "VIDER LES DONNEES") {
            $("resetDataMessage").textContent = "Phrase de confirmation incorrecte.";
            return;
        }
        const button = $("confirmResetDataBtn");
        button.disabled = true;
        button.textContent = "Suppression...";
        try {
            await loadCurrentUser();
            const result = await db.rpc("admin_reset_application_data", { p_confirmation: phrase });
            if (result.error) throw result.error;
            if(result.data?.status!=="completed"||!Number.isInteger(result.data.tables_cleared)||result.data.tables_cleared<=0||!Number.isInteger(result.data.accounts_preserved)||result.data.accounts_preserved<1)throw Error("Suppression non confirmee par le serveur");
            $("resetDataMessage").textContent = `Termine. ${result.data?.tables_cleared || 0} table(s) videe(s). Comptes conserves: ${result.data?.accounts_preserved || 0}.`;
            $("resetDataMessage").className = "message success";
            setTimeout(() => location.href = "dashboard.html", 1800);
        } catch (error) {
            $("resetDataMessage").textContent = "Erreur : " + error.message;
            $("resetDataMessage").className = "message error";
            button.disabled = false;
            button.textContent = "Supprimer les donnees";
        }
    }

    async function updateFinancePermission(id, value, input) {
        input.disabled = true;
        try {
            await loadCurrentUser();
            const result = await db
                .from("profiles")
                .update({ can_manage_finance: value })
                .eq("id", id)
                .select("id, can_manage_finance")
                .maybeSingle();

            if (result.error) throw result.error;
            if (!result.data) throw new Error("Permission non modifiee.");
            message("Permission finance mise a jour.", "success");
        } catch (error) {
            input.checked = !value;
            message("Erreur : " + error.message, "error");
        } finally {
            input.disabled = false;
        }
    }

    async function saveYear(event) {
        event.preventDefault();
        if (saving) return;
        setSaving(true);
        yearMessage("");

        try {
            await loadCurrentUser();
            const active = $("yearActive").value === "true";
            const startDate = $("yearStart").value;
            const endDate = $("yearEnd").value;

            if (endDate <= startDate) throw new Error("La date de fin doit etre apres la date de debut.");

            if (active) {
                const deactivateResult = await db
                    .from("academic_years")
                    .update({ active: false })
                    .eq("active", true);
                if (deactivateResult.error) throw deactivateResult.error;
            }

            const result = await db
                .from("academic_years")
                .insert({
                    label: $("yearLabel").value.trim(),
                    start_date: startDate,
                    end_date: endDate,
                    active
                })
                .select("*")
                .maybeSingle();

            if (result.error) throw result.error;
            if (!result.data) throw new Error("L'annee scolaire n'a pas ete creee.");

            $("yearDialog").close();
            await loadAcademicYears();
            renderYears();
            message("Annee scolaire enregistree.", "success");
        } catch (error) {
            console.error(error);
            yearMessage("Erreur : " + error.message, "error");
        } finally {
            setSaving(false);
        }
    }

    $("schoolForm").addEventListener("submit", saveSchool);
    $("addYearBtn").addEventListener("click", () => {
        $("yearForm").reset();
        const currentYear = new Date().getFullYear();
        $("yearLabel").value = currentYear + "-" + (currentYear + 1);
        $("yearStart").value = currentYear + "-09-01";
        $("yearEnd").value = (currentYear + 1) + "-06-30";
        $("yearActive").value = years.some(year => year.active) ? "false" : "true";
        yearMessage("");
        $("yearDialog").showModal();
    });
    $("yearForm").addEventListener("submit", saveYear);
    $("closeYearBtn").addEventListener("click", () => $("yearDialog").close());
    $("cancelYearBtn").addEventListener("click", () => $("yearDialog").close());

    $("openResetDataBtn").addEventListener("click", openResetDataDialog);
    $("closeResetDataBtn").addEventListener("click", () => $("resetDataDialog").close());
    $("cancelResetDataBtn").addEventListener("click", () => $("resetDataDialog").close());
    $("resetDataForm").addEventListener("submit", resetApplicationData);

    loadAll();
})();
