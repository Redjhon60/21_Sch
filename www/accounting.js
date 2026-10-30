(() => {
    "use strict";

    const SUPABASE_URL = "https://rsyslzkzddqrktkivttj.supabase.co";
    const SUPABASE_KEY = "sb_publishable_kaQwfCNTwKhMR-vyrttg-g_weS7URLP";
    const $ = id => document.getElementById(id);

    const requiredIds = [
        "addExpenseBtn", "incomeTotal", "manualExpenseTotal",
        "salaryExpenseTotal", "balanceTotal", "monthFilter",
        "typeFilter", "categoryFilter", "searchInput", "refreshBtn",
        "message", "operationsTable", "expenseDialog", "expenseForm",
        "formTitle", "expenseId", "expenseDate", "category",
        "expenseType", "typeHelp", "description", "amount",
        "paymentMethod", "reference", "notes", "formMessage",
        "closeDialogBtn", "cancelBtn", "saveBtn"
    ];

    const missing = requiredIds.filter(id => !$(id));
    if (missing.length || !window.supabase) {
        console.error("Missing elements:", missing);
        if ($("message")) {
            $("message").textContent = "Erreur HTML/JS : " + missing.join(", ");
        }
        return;
    }

    const db = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

    const categoryTypes = {
        "Fournitures": "variable",
        "Entretien": "variable",
        "Loyer": "fixed",
        "Eau et electricite": "variable",
        "Transport": "variable",
        "Equipement": "variable",
        "Taxes": "variable",
        "CNSS": "variable",
        "Activite": "variable",
        "Autre": "variable"
    };

    let expenses = [];
    let transactions = [];
    let remunerations = [];
    let employeePeriods=[];let payrollEmployees=[];
    let teachers = [];
    let profile = null;
    let busy = false;

    const money = value => new Intl.NumberFormat("fr-MA", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(Number(value || 0)) + " MAD";

    function formatDate(value) {
        if (!value) return "—";
        const p = value.split("-");
        return p.length === 3 ? `${p[2]}/${p[1]}/${p[0]}` : value;
    }

    function methodLabel(value) {
        return {
            cash: "Especes",
            bank_transfer: "Virement",
            card: "Carte",
            cheque: "Cheque",
            other: "Autre"
        }[value] || "—";
    }

    function showMessage(value = "", type = "") {
        $("message").textContent = value;
        $("message").className = "message" + (type ? " " + type : "");
    }

    function showFormMessage(value = "", type = "") {
        $("formMessage").textContent = value;
        $("formMessage").className = "message" + (type ? " " + type : "");
    }

    function setBusy(value) {
        busy = value;
        ["addExpenseBtn", "refreshBtn", "saveBtn", "cancelBtn", "closeDialogBtn"]
            .forEach(id => $(id).disabled = value);
    }

    async function checkAccess() {
        const userResult = await db.auth.getUser();
        if (!userResult.data.user) throw new Error("Connexion requise.");

        const result = await db
            .from("profiles")
            .select("role, status, can_manage_finance")
            .eq("id", userResult.data.user.id)
            .maybeSingle();

        if (result.error) throw result.error;
        if (!result.data) throw new Error("Profil utilisateur introuvable.");

        profile = { ...result.data, id: userResult.data.user.id };
        const approved = String(profile.status || "").trim().toLowerCase() === "approved";
        const finance = String(profile.role || "").trim().toLowerCase() === "access total"
            || profile.can_manage_finance === true;

        if (!approved || !finance) throw new Error("Permission financiere requise.");
    }

    function currentMonthRange() {
        const month = $("monthFilter").value;
        if (!month) return null;

        const date = new Date(month + "-01T00:00:00Z");
        date.setUTCMonth(date.getUTCMonth() + 1);

        return {
            start: month + "-01",
            next: date.toISOString().slice(0, 10)
        };
    }

    function teacherName(id) {
        return teachers.find(item => item.id === id)?.full_name || "Professeur";
    }

    function buildOperations() {
        const monthlyIncome = new Map();
        for(const t of transactions){const key=String(t.payment_date||'').slice(0,7);if(!key)continue;if(!monthlyIncome.has(key))monthlyIncome.set(key,{id:'income-'+key,date:key+'-01',operation:'income',category:'Paiement eleve',type:'income',description:'Total paiements eleves - '+key,method:null,amount:0,editable:false});monthlyIncome.get(key).amount+=Number(t.amount_paid||0);}
        const incomes=[...monthlyIncome.values()];

        const manualExpenses = expenses.map(item => ({
            id: "expense-" + item.id,
            date: item.expense_date,
            operation: "expense",
            category: item.category,
            type: item.expense_type,
            description: item.description,
            method: item.payment_method,
            amount: Number(item.amount),
            editable: true,
            raw: item
        }));

        const salaryExpenses = remunerations.map(item => ({
            id: "salary-" + item.id,
            date: item.period_month,
            operation: "salary",
            category: "Salaires",
            type: "automatic",
            description: `${teacherName(item.teacher_id)} - ${item.payment_mode === "hourly" ? "horaire" : "mensuel"}`,
            method: null,
            amount: Number(item.calculated_amount || 0),
            editable: false
        }));

        const employeeCosts=employeePeriods.map(r=>({id:'employee-salary-'+r.id,date:r.period_month,operation:'salary',category:'Salaires',type:'automatic',description:payrollEmployees.find(e=>e.id===r.employee_id)?.first_name+' '+(payrollEmployees.find(e=>e.id===r.employee_id)?.last_name||''),method:null,amount:Number(r.total_due||0),editable:false}));return [...incomes, ...manualExpenses, ...salaryExpenses,...employeeCosts];
    }

    function populateCategoryFilter() {
        const selected = $("categoryFilter").value;
        const categories = [
            "Paiement eleve", "Salaires", ...Object.keys(categoryTypes)
        ];

        $("categoryFilter").innerHTML = '<option value="">Toutes les categories</option>';
        categories.forEach(category => {
            $("categoryFilter").add(new Option(category, category));
        });
        $("categoryFilter").value = selected;
    }

    function render() {
        populateCategoryFilter();

        const query = $("searchInput").value.trim().toLowerCase();
        const type = $("typeFilter").value;
        const category = $("categoryFilter").value;
        const range = currentMonthRange();

        const operations = buildOperations()
            .filter(item => {
                const inMonth = !range || (item.date >= range.start && item.date < range.next);
                const matchingType = !type || item.operation === type || item.type === type;
                const matchingCategory = !category || item.category === category;
                const searchable = [item.category, item.description, item.operation, item.type]
                    .join(" ").toLowerCase();
                return inMonth && matchingType && matchingCategory && searchable.includes(query);
            })
            .sort((a, b) => String(b.date).localeCompare(String(a.date)));

        const income = operations
            .filter(item => item.operation === "income")
            .reduce((total, item) => total + item.amount, 0);

        const manual = operations
            .filter(item => item.operation === "expense")
            .reduce((total, item) => total + item.amount, 0);

        const salaries = operations
            .filter(item => item.operation === "salary")
            .reduce((total, item) => total + item.amount, 0);

        $("incomeTotal").textContent = money(income);
        $("manualExpenseTotal").textContent = money(manual);
        $("salaryExpenseTotal").textContent = money(salaries);
        $("balanceTotal").textContent = money(income - manual - salaries);

        $("operationsTable").replaceChildren();

        if (!operations.length) {
            const row = $("operationsTable").insertRow();
            const cell = row.insertCell();
            cell.colSpan = 8;
            cell.className = "empty-state";
            cell.textContent = "Aucune operation pour cette selection.";
            return;
        }

        for (const item of operations) {
            const row = $("operationsTable").insertRow();
            row.insertCell().textContent = formatDate(item.date);

            const operationCell = row.insertCell();
            const operationBadge = document.createElement("span");
            operationBadge.className = "operation-badge operation-" + item.operation;
            operationBadge.textContent = {
                income: "Recette",
                expense: "Depense",
                salary: "Salaire auto"
            }[item.operation];
            operationCell.append(operationBadge);

            row.insertCell().textContent = item.category;

            const typeCell = row.insertCell();
            const typeBadge = document.createElement("span");
            typeBadge.className = "type-badge type-" + item.type;
            typeBadge.textContent = {
                income: "Automatique",
                fixed: "Fixe",
                variable: "Variable",
                automatic: "Automatique"
            }[item.type];
            typeCell.append(typeBadge);

            row.insertCell().textContent = item.description;
            row.insertCell().textContent = methodLabel(item.method);

            const amountCell = row.insertCell();
            amountCell.className = item.operation === "income" ? "amount-income" : "amount-expense";
            amountCell.textContent = (item.operation === "income" ? "+ " : "- ") + money(item.amount);

            const actions = row.insertCell();
            if (item.editable) {
                const edit = document.createElement("button");
                edit.type = "button";
                edit.className = "row-action";
                edit.textContent = "Modifier";
                edit.addEventListener("click", () => openExpense(item.raw));

                const remove = document.createElement("button");
                remove.type = "button";
                remove.className = "row-action delete";
                remove.textContent = "Supprimer";
                remove.addEventListener("click", () => deleteExpense(item.raw));

                actions.append(edit, remove);
            } else {
                actions.textContent = "Automatique";
            }
        }
    }

    async function loadData() {
        if (busy) return;
        setBusy(true);
        showMessage("Chargement...");

        try {
            await checkAccess();
            const [ep,ee]=await Promise.all([db.from('employee_salary_periods').select('*'),db.from('employees').select('id,first_name,last_name')]);if(ep.error)throw ep.error;if(ee.error)throw ee.error;employeePeriods=ep.data||[];payrollEmployees=ee.data||[];

            const [expenseResult, transactionResult, remunerationResult, teacherResult] = await Promise.all([
                db.from("expenses").select("*").order("expense_date", { ascending: false }),
                db.from("payment_transactions").select("id, amount_paid, payment_date, payment_method, reference"),
                db.from("teacher_remunerations").select("id, teacher_id, period_month, payment_mode, calculated_amount"),
                db.from("teachers").select("id, full_name")
            ]);

            for (const result of [expenseResult, transactionResult, remunerationResult, teacherResult]) {
                if (result.error) throw result.error;
            }

            expenses = expenseResult.data || [];
            transactions = transactionResult.data || [];
            remunerations = remunerationResult.data || [];
            teachers = teacherResult.data || [];

            render();
            showMessage("");
        } catch (error) {
            showMessage("Erreur : " + error.message, "error");
        } finally {
            setBusy(false);
        }
    }

    function applyCategoryType() {
        const category = $("category").value;
        const type = categoryTypes[category] || "variable";
        $("expenseType").value = type;

        if (category === "Loyer") {
            $("expenseType").disabled = true;
            $("typeHelp").textContent = "Le loyer est toujours classe comme depense fixe.";
        } else {
            $("expenseType").disabled = false;
            $("typeHelp").textContent = "Type propose automatiquement. Vous pouvez le modifier.";
        }
    }

    function openExpense(item = null) {
        $("expenseForm").reset();
        $("expenseId").value = item?.id || "";
        $("expenseDate").value = item?.expense_date || new Date().toISOString().slice(0, 10);
        $("category").value = item?.category || "";
        $("expenseType").value = item?.expense_type || "variable";
        $("description").value = item?.description || "";
        $("amount").value = item?.amount || "";
        $("paymentMethod").value = item?.payment_method || "";
        $("reference").value = item?.reference || "";
        $("notes").value = item?.notes || "";
        $("formTitle").textContent = item ? "Modifier la depense" : "Ajouter une depense";
        showFormMessage("");
        applyCategoryType();
        $("expenseDialog").showModal();
    }

    async function saveExpense(event) {
        event.preventDefault();
        if (busy) return;

        if (!$("expenseForm").reportValidity()) return;
        setBusy(true);

        try {
            await checkAccess();

            const record = {
                expense_date: $("expenseDate").value,
                category: $("category").value,
                expense_type: $("expenseType").value,
                description: $("description").value.trim(),
                amount: Number($("amount").value),
                payment_method: $("paymentMethod").value || null,
                reference: $("reference").value.trim() || null,
                notes: $("notes").value.trim() || null,
                created_by: profile.id,
                updated_at: new Date().toISOString()
            };

            const id = $("expenseId").value;
            const result = id
                ? await db.from("expenses").update(record).eq("id", id)
                : await db.from("expenses").insert(record);

            if (result.error) throw result.error;

            $("expenseDialog").close();
            setBusy(false);
            await loadData();
            showMessage("Depense enregistree.", "success");
        } catch (error) {
            showFormMessage("Erreur : " + error.message, "error");
            setBusy(false);
        }
    }

    async function deleteExpense(item) {
        if (!window.confirm("Supprimer cette depense ?")) return;

        setBusy(true);
        try {
            await checkAccess();
            const result = await db.from("expenses").delete().eq("id", item.id);
            if (result.error) throw result.error;
            setBusy(false);
            await loadData();
            showMessage("Depense supprimee.", "success");
        } catch (error) {
            showMessage("Erreur : " + error.message, "error");
            setBusy(false);
        }
    }

    function openMonthlyExpenses(){const month=$('monthFilter').value||new Date().toISOString().slice(0,7);$('expenseBatchMonth').value=month;$('expenseBatchRows').replaceChildren();for(const [category,type]of Object.entries(categoryTypes)){const row=document.createElement('div');row.className='expense-batch-row';const title=document.createElement('strong');title.textContent=category;const badge=document.createElement('span');badge.textContent=type==='fixed'?'Fixe':'Variable';const input=document.createElement('input');input.type='number';input.min='0';input.step='0.01';input.dataset.category=category;input.dataset.type=type;input.setAttribute('aria-label','Montant '+category);const existing=expenses.filter(e=>e.category===category&&String(e.expense_date).slice(0,7)===month);const latest=expenses.filter(e=>e.category===category&&e.expense_type==='fixed').sort((a,b)=>String(b.expense_date).localeCompare(String(a.expense_date)))[0];if(existing.length){input.disabled=true;input.placeholder='Deja enregistree ce mois';}else if(type==='fixed'&&latest){input.value=latest.amount;input.readOnly=true;}else input.placeholder=type==='fixed'?'Montant fixe a configurer':'Montant du mois';row.append(title,badge,input);$('expenseBatchRows').append(row);}$('expenseBatchMessage').textContent='';if(!$('expenseBatchDialog').open)$('expenseBatchDialog').showModal();}
    async function saveMonthlyExpenses(){if(busy)return;const month=$('expenseBatchMonth').value;if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(month)){$('expenseBatchMessage').textContent='Mois invalide';return;}const inputs=[...document.querySelectorAll('#expenseBatchRows input')].filter(i=>!i.disabled&&i.value!=='');if(!inputs.length)return;if(inputs.some(i=>!Number.isFinite(Number(i.value))||Number(i.value)<0)){$('expenseBatchMessage').textContent='Montant invalide';return;}setBusy(true);$('expenseBatchSave').disabled=true;let done=0;try{await checkAccess();for(const input of inputs){const check=await db.from('expenses').select('id,expense_date').eq('category',input.dataset.category);if(check.error)throw check.error;if((check.data||[]).some(e=>String(e.expense_date).slice(0,7)===month))throw Error(input.dataset.category+': deja enregistree ce mois');const record={expense_date:month+'-01',category:input.dataset.category,expense_type:input.dataset.type,description:input.dataset.category+' - '+month,amount:Number(input.value),payment_method:null,reference:null,notes:'Saisie mensuelle',created_by:profile.id,updated_at:new Date().toISOString()};const result=await db.from('expenses').insert(record);if(result.error)throw result.error;done++;}$('expenseBatchDialog').close();setBusy(false);await loadData();showMessage(done+' depense(s) enregistree(s).','success');}catch(e){$('expenseBatchMessage').textContent=done+' enregistree(s). '+e.message+' Verifier avant reprise.';}finally{setBusy(false);$('expenseBatchSave').disabled=false;}}
    $('expenseBatchSave').onclick=saveMonthlyExpenses;$('expenseBatchClose').onclick=()=>$('expenseBatchDialog').close();$('expenseBatchMonth').onchange=()=>{$('monthFilter').value=$('expenseBatchMonth').value;openMonthlyExpenses();};
    $("addExpenseBtn").addEventListener("click", openMonthlyExpenses);
    $("refreshBtn").addEventListener("click", loadData);
    $("monthFilter").addEventListener("change", render);
    $("typeFilter").addEventListener("change", render);
    $("categoryFilter").addEventListener("change", render);
    $("searchInput").addEventListener("input", render);
    $("category").addEventListener("change", applyCategoryType);
    $("expenseForm").addEventListener("submit", saveExpense);
    $("closeDialogBtn").addEventListener("click", () => $("expenseDialog").close());
    $("cancelBtn").addEventListener("click", () => $("expenseDialog").close());

    $("monthFilter").value = new Date().toISOString().slice(0, 7);
    window.addEventListener('le-schema-data-updated',loadData);window.addEventListener('focus',loadData);
    loadData();
})();
