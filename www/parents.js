/* =========================================================
   SUPABASE
========================================================= */

const SUPABASE_URL = "https://rsyslzkzddqrktkivttj.supabase.co";
const SUPABASE_KEY = "sb_publishable_kaQwfCNTwKhMR-vyrttg-g_weS7URLP";

const db = window.supabase.createClient(
    SUPABASE_URL,
    SUPABASE_KEY
);


/* =========================================================
   ELEMENTS HTML
========================================================= */

const table = document.getElementById("parentsTable");
const searchInput = document.getElementById("searchInput");
const message = document.getElementById("message");

const dialog = document.getElementById("parentDialog");
const parentForm = document.getElementById("parentForm");

const studentSelect = document.getElementById("studentId");
const relationshipSelect = document.getElementById("relationship");

const addParentBtn = document.getElementById("addParentBtn");
const refreshBtn = document.getElementById("refreshBtn");
const languageBtn = document.getElementById("languageBtn");
const closeDialogBtn = document.getElementById("closeDialogBtn");
const cancelBtn = document.getElementById("cancelBtn");
const saveBtn = document.getElementById("saveBtn");


/* =========================================================
   ETAT
========================================================= */

let parents = [];
let students = [];
let language = "fr";


/* =========================================================
   TRADUCTIONS
========================================================= */

const text = {
    fr: {
        back: "← Tableau de bord",
        eyebrow: "GESTION SCOLAIRE",
        title: "Gestion des parents",

        subtitle:
            "Consultez et gérez les informations des parents et leurs élèves associés.",

        add: "+ Ajouter un parent",

        totalParents: "Total des parents",
        linkedStudents: "Élèves associés",

        search:
            "Rechercher par nom, téléphone, CIN ou email...",

        refresh: "Actualiser",

        parentName: "Nom complet",
        cin: "CIN",
        phone: "Téléphone",
        email: "Email",
        students: "Élève(s)",
        relationship: "Lien",
        actions: "Actions",

        loading: "Chargement des parents...",
        empty: "Aucun parent trouvé.",

        formAdd: "Ajouter un parent",
        formEdit: "Modifier le parent",

        fullName: "Nom complet *",
        cinLabel: "CIN",
        phoneLabel: "Téléphone *",
        emailLabel: "Email",
        address: "Adresse",

        student: "Élève",
        relationshipLabel: "Lien avec l'élève",

        chooseStudent: "Choisir un élève",
        chooseRelationship: "Choisir",

        father: "Père",
        mother: "Mère",
        guardian: "Tuteur",
        femaleGuardian: "Tutrice",
        other: "Autre",

        cancel: "Annuler",
        save: "Enregistrer",

        edit: "Modifier",
        delete: "Supprimer",

        saved: "Parent enregistré avec succès.",
        deleted: "Parent supprimé avec succès.",

        confirmDelete:
            "Voulez-vous vraiment supprimer ce parent ?",

        login:
            "Veuillez vous connecter pour continuer.",

        denied:
            "Accès refusé : ce compte n'est pas une administration approuvée.",

        required:
            "Veuillez renseigner le nom complet et le téléphone.",

        error: "Une erreur est survenue : ",

        duplicateLink:
            "Ce parent est déjà associé à cet élève.",

        language: "العربية"
    },

    ar: {
        back: "← لوحة التحكم",
        eyebrow: "التسيير المدرسي",
        title: "تدبير أولياء الأمور",

        subtitle:
            "عرض وتدبير معلومات أولياء الأمور والتلاميذ المرتبطين بهم.",

        add: "+ إضافة ولي أمر",

        totalParents: "مجموع أولياء الأمور",
        linkedStudents: "التلاميذ المرتبطون",

        search:
            "البحث بالاسم أو الهاتف أو البطاقة الوطنية أو البريد الإلكتروني...",

        refresh: "تحديث",

        parentName: "الاسم الكامل",
        cin: "البطاقة الوطنية",
        phone: "الهاتف",
        email: "البريد الإلكتروني",
        students: "التلميذ",
        relationship: "صلة القرابة",
        actions: "الإجراءات",

        loading: "جاري تحميل أولياء الأمور...",
        empty: "لا يوجد أي ولي أمر.",

        formAdd: "إضافة ولي أمر",
        formEdit: "تعديل معلومات ولي الأمر",

        fullName: "الاسم الكامل *",
        cinLabel: "البطاقة الوطنية",
        phoneLabel: "الهاتف *",
        emailLabel: "البريد الإلكتروني",
        address: "العنوان",

        student: "التلميذ",
        relationshipLabel: "صلة القرابة",

        chooseStudent: "اختر التلميذ",
        chooseRelationship: "اختر",

        father: "الأب",
        mother: "الأم",
        guardian: "الولي",
        femaleGuardian: "الولية",
        other: "أخرى",

        cancel: "إلغاء",
        save: "حفظ",

        edit: "تعديل",
        delete: "حذف",

        saved: "تم تسجيل ولي الأمر بنجاح.",
        deleted: "تم حذف ولي الأمر بنجاح.",

        confirmDelete:
            "واش متأكد بغيتي تحذف ولي الأمر؟",

        login:
            "خاصك تسجل الدخول باش تكمل.",

        denied:
            "مرفوض: هاد الحساب ماشي إدارة معتمدة.",

        required:
            "خاصك تعمر الاسم الكامل والهاتف.",

        error: "وقع خطأ: ",

        duplicateLink:
            "ولي الأمر مرتبط مسبقاً بهذا التلميذ.",

        language: "Français"
    }
};


/* =========================================================
   HELPERS
========================================================= */

function tr(key) {
    return text[language][key] || key;
}


function showMessage(value, type = "") {
    message.textContent = value;
    message.className =
        "message" + (type ? " " + type : "");
}


function showFormMessage(value, type = "") {
    const element = document.getElementById("formMessage");

    if (!element) return;

    element.textContent = value;
    element.className =
        "message" + (type ? " " + type : "");
}


function cleanValue(id) {
    const element = document.getElementById(id);

    if (!element) return null;

    const value = element.value.trim();

    return value || null;
}


/* =========================================================
   CONTROLE D'ACCES
========================================================= */

async function checkAccess() {
    const {
        data: { user },
        error: userError
    } = await db.auth.getUser();

    if (userError || !user) {
        showMessage(tr("login"), "error");
        return false;
    }

    const { data: profile, error } = await db
        .from("profiles")
        .select("role, status")
        .eq("id", user.id)
        .maybeSingle();

    if (error) {
        showMessage(
            tr("error") + error.message,
            "error"
        );

        return false;
    }

    const normalizedRole =
        String(profile?.role || "")
            .trim()
            .toLowerCase();

    const normalizedStatus =
        String(profile?.status || "")
            .trim()
            .toLowerCase();

    const allowedRoles = [
        "access",
        "access total"
    ];

    if (
        !profile ||
        !allowedRoles.includes(normalizedRole) ||
        normalizedStatus !== "approved"
    ) {
        showMessage(
            tr("denied"),
            "error"
        );

        return false;
    }

    return true;
}


/* =========================================================
   TRADUCTION PAGE
========================================================= */

function translatePage() {
    const ids = {
        backLink: "back",
        eyebrow: "eyebrow",
        pageTitle: "title",
        pageSubtitle: "subtitle",
        addParentBtn: "add",

        totalParentsLabel: "totalParents",
        linkedStudentsLabel: "linkedStudents",

        refreshBtn: "refresh",

        parentNameHead: "parentName",
        cinHead: "cin",
        phoneHead: "phone",
        emailHead: "email",
        studentsHead: "students",
        relationshipHead: "relationship",
        actionsHead: "actions",

        fullNameLabel: "fullName",
        cinLabel: "cinLabel",
        phoneLabel: "phoneLabel",
        emailLabel: "emailLabel",
        addressLabel: "address",

        studentLabel: "student",
        relationshipLabel: "relationshipLabel",

        cancelBtn: "cancel",
        saveBtn: "save"
    };

    for (const [id, key] of Object.entries(ids)) {
        const element = document.getElementById(id);

        if (element) {
            element.textContent = tr(key);
        }
    }

    if (searchInput) {
        searchInput.placeholder = tr("search");
    }

    if (languageBtn) {
        languageBtn.textContent = tr("language");
    }

    document.documentElement.lang =
        language === "ar" ? "ar" : "fr";

    document.documentElement.dir =
        language === "ar" ? "rtl" : "ltr";

    updateSelectTexts();
    renderParents();
}


/* =========================================================
   CHARGEMENT DES ELEVES
========================================================= */

async function loadStudents() {
    const { data, error } = await db
        .from("students")
        .select(
            "id, student_number, first_name, last_name, class_name"
        )
        .order("last_name", {
            ascending: true
        });

    if (error) {
        students = [];

        showMessage(
            tr("error") + error.message,
            "error"
        );

        return false;
    }

    students = data || [];

    populateStudentSelect();

    return true;
}


/* =========================================================
   SELECT ELEVES
========================================================= */

function populateStudentSelect(selectedId = "") {
    if (!studentSelect) return;

    studentSelect.replaceChildren();

    const defaultOption =
        document.createElement("option");

    defaultOption.value = "";
    defaultOption.textContent =
        tr("chooseStudent");

    studentSelect.appendChild(defaultOption);

    for (const student of students) {
        const option =
            document.createElement("option");

        option.value = student.id;

        const fullName =
            `${student.first_name || ""} ${student.last_name || ""}`
                .trim();

        const details = [];

        if (student.student_number) {
            details.push(student.student_number);
        }

        if (student.class_name) {
            details.push(student.class_name);
        }

        option.textContent =
            details.length > 0
                ? `${fullName} — ${details.join(" / ")}`
                : fullName;

        if (student.id === selectedId) {
            option.selected = true;
        }

        studentSelect.appendChild(option);
    }
}


/* =========================================================
   SELECT RELATION
========================================================= */

function populateRelationshipSelect(
    selectedValue = ""
) {
    if (!relationshipSelect) return;

    relationshipSelect.replaceChildren();

    const defaultOption =
        document.createElement("option");

    defaultOption.value = "";
    defaultOption.textContent =
        tr("chooseRelationship");

    relationshipSelect.appendChild(
        defaultOption
    );

    const relations = [
        ["Père", "father"],
        ["Mère", "mother"],
        ["Tuteur", "guardian"],
        ["Tutrice", "femaleGuardian"],
        ["Autre", "other"]
    ];

    for (const [value, key] of relations) {
        const option =
            document.createElement("option");

        option.value = value;
        option.textContent = tr(key);

        if (value === selectedValue) {
            option.selected = true;
        }

        relationshipSelect.appendChild(option);
    }
}


function updateSelectTexts() {
    if (!studentSelect || !relationshipSelect) {
        return;
    }

    const selectedStudent =
        studentSelect.value;

    const selectedRelationship =
        relationshipSelect.value;

    populateStudentSelect(selectedStudent);

    populateRelationshipSelect(
        selectedRelationship
    );
}


/* =========================================================
   CHARGEMENT PARENTS ET LIENS
========================================================= */

async function loadParents() {
    showMessage(tr("loading"));

    const allowed = await checkAccess();

    if (!allowed) {
        parents = [];

        if (table) {
            table.replaceChildren();
        }

        return;
    }

    const { data: parentData, error: parentError } =
        await db
            .from("parents")
            .select(
                "id, full_name, cin, phone, email, address, created_at, updated_at"
            )
            .order("full_name", {
                ascending: true
            });

    if (parentError) {
        parents = [];
        renderParents();

        showMessage(
            tr("error") + parentError.message,
            "error"
        );

        return;
    }

    const { data: linkData, error: linkError } =
        await db
            .from("parent_students")
            .select(
                "id, parent_id, student_id, relationship, created_at"
            )
            .not("parent_id", "is", null);

    if (linkError) {
        parents = (parentData || []).map(parent => ({
            ...parent,
            links: []
        }));

        renderParents();

        showMessage(
            tr("error") + linkError.message,
            "error"
        );

        return;
    }

    const links = linkData || [];

    parents = (parentData || []).map(parent => ({
        ...parent,

        links: links.filter(
            link =>
                link.parent_id === parent.id
        )
    }));

    showMessage("");

    renderParents();
}


/* =========================================================
   STATISTIQUES
========================================================= */

function updateStats() {
    const totalParents =
        document.getElementById("totalParents");

    const totalLinkedStudents =
        document.getElementById(
            "totalLinkedStudents"
        );

    if (totalParents) {
        totalParents.textContent =
            parents.length;
    }

    const linkedStudents =
        new Set();

    for (const parent of parents) {
        for (const link of parent.links || []) {
            if (link.student_id) {
                linkedStudents.add(
                    link.student_id
                );
            }
        }
    }

    if (totalLinkedStudents) {
        totalLinkedStudents.textContent =
            linkedStudents.size;
    }
}


/* =========================================================
   HELPERS ELEVES
========================================================= */

function findStudent(studentId) {
    return students.find(
        student =>
            student.id === studentId
    );
}


function getStudentDisplayName(studentId) {
    const student =
        findStudent(studentId);

    if (!student) {
        return "—";
    }

    const fullName =
        `${student.first_name || ""} ${student.last_name || ""}`
            .trim();

    if (student.class_name) {
        return `${fullName} (${student.class_name})`;
    }

    return fullName || "—";
}


/* =========================================================
   AFFICHAGE DES PARENTS
========================================================= */

function renderParents() {
    if (!table || !searchInput) {
        return;
    }

    const query =
        searchInput.value
            .trim()
            .toLocaleLowerCase();

    const filtered =
        parents.filter(parent => {
            const studentNames =
                (parent.links || [])
                    .map(link =>
                        getStudentDisplayName(
                            link.student_id
                        )
                    )
                    .join(" ");

            const relationships =
                (parent.links || [])
                    .map(
                        link =>
                            link.relationship || ""
                    )
                    .join(" ");

            const searchable = [
                parent.full_name,
                parent.cin,
                parent.phone,
                parent.email,
                parent.address,
                studentNames,
                relationships
            ]
                .filter(Boolean)
                .join(" ")
                .toLocaleLowerCase();

            return searchable.includes(query);
        });

    table.replaceChildren();

    if (!filtered.length) {
        const row = table.insertRow();
        const cell = row.insertCell();

        cell.colSpan = 7;
        cell.className = "empty-state";
        cell.textContent = tr("empty");

        updateStats();

        return;
    }

    for (const parent of filtered) {
        const row = table.insertRow();

        const links =
            parent.links || [];

        const studentNames =
            links.length > 0
                ? links
                    .map(link =>
                        getStudentDisplayName(
                            link.student_id
                        )
                    )
                    .join(", ")
                : "—";

        const relationshipNames =
            links.length > 0
                ? links
                    .map(
                        link =>
                            link.relationship || "—"
                    )
                    .join(", ")
                : "—";

        const values = [
            parent.full_name || "—",
            parent.cin || "—",
            parent.phone || "—",
            parent.email || "—",
            studentNames,
            relationshipNames
        ];

        for (const value of values) {
            const cell = row.insertCell();
            cell.textContent = value;
        }

        const actions = row.insertCell();

        const editButton =
            document.createElement("button");

        editButton.type = "button";
        editButton.className =
            "row-action";

        editButton.textContent =
            tr("edit");

        editButton.addEventListener(
            "click",
            () => openEditForm(parent)
        );

        const deleteButton =
            document.createElement("button");

        deleteButton.type = "button";

        deleteButton.className =
            "row-action delete";

        deleteButton.textContent =
            tr("delete");

        deleteButton.addEventListener(
            "click",
            () => deleteParent(parent)
        );

        actions.append(
            editButton,
            deleteButton
        );
    }

    updateStats();
}


/* =========================================================
   AJOUTER PARENT
========================================================= */

function openAddForm() {
    parentForm.reset();

    document.getElementById(
        "parentId"
    ).value = "";

    populateStudentSelect();
    populateRelationshipSelect();

    document.getElementById(
        "formTitle"
    ).textContent =
        tr("formAdd");

    saveBtn.textContent =
        tr("save");

    showFormMessage("");

    dialog.showModal();
}


/* =========================================================
   MODIFIER PARENT
========================================================= */

function openEditForm(parent) {
    parentForm.reset();

    document.getElementById(
        "parentId"
    ).value =
        parent.id;

    document.getElementById(
        "fullName"
    ).value =
        parent.full_name || "";

    document.getElementById(
        "cin"
    ).value =
        parent.cin || "";

    document.getElementById(
        "phone"
    ).value =
        parent.phone || "";

    document.getElementById(
        "email"
    ).value =
        parent.email || "";

    document.getElementById(
        "address"
    ).value =
        parent.address || "";

    /*
       Pour l'instant le formulaire affiche
       le premier lien existant.

       Les autres liens ne seront PAS supprimés
       lors de la modification.
    */

    const firstLink =
        parent.links?.[0] || null;

    populateStudentSelect(
        firstLink?.student_id || ""
    );

    populateRelationshipSelect(
        firstLink?.relationship || ""
    );

    document.getElementById(
        "formTitle"
    ).textContent =
        tr("formEdit");

    saveBtn.textContent =
        tr("save");

    showFormMessage("");

    dialog.showModal();
}


/* =========================================================
   TROUVER UN LIEN
========================================================= */

function findExistingLink(
    parent,
    studentId
) {
    if (!parent || !studentId) {
        return null;
    }

    return (parent.links || []).find(
        link =>
            link.student_id === studentId
    ) || null;
}


/* =========================================================
   AJOUTER / METTRE A JOUR LE LIEN
========================================================= */

async function saveParentStudentLink(
    parentId,
    studentId,
    relationship
) {
    if (!studentId) {
        return { error: null };
    }

    const parent =
        parents.find(
            item =>
                item.id === parentId
        );

    const existingLink =
        findExistingLink(
            parent,
            studentId
        );

    /*
       Si le lien existe déjà, on met
       uniquement à jour la relation.
    */

    if (existingLink) {
        const { error } = await db
            .from("parent_students")
            .update({
                relationship:
                    relationship || null
            })
            .eq("id", existingLink.id);

        return { error };
    }

    /*
       Sinon on crée un nouveau lien.
       parent_user_id reste NULL.
    */

    const { error } = await db
        .from("parent_students")
        .insert({
            parent_id: parentId,
            student_id: studentId,
            relationship:
                relationship || null
        });

    return { error };
}


/* =========================================================
   SAUVEGARDE PARENT
========================================================= */

async function saveParent(event) {
    event.preventDefault();

    showFormMessage("");

    const allowed =
        await checkAccess();

    if (!allowed) {
        return;
    }

    const fullName =
        cleanValue("fullName");

    const phone =
        cleanValue("phone");

    if (!fullName || !phone) {
        showFormMessage(
            tr("required"),
            "error"
        );

        return;
    }

    const currentParentId =
        document.getElementById(
            "parentId"
        ).value;

    const studentId =
        studentSelect.value || null;

    const relationship =
        relationshipSelect.value || null;

    const record = {
        full_name: fullName,
        cin: cleanValue("cin"),
        phone: phone,
        email: cleanValue("email"),
        address: cleanValue("address"),
        updated_at:
            new Date().toISOString()
    };

    saveBtn.disabled = true;

    try {
        let savedParentId =
            currentParentId;

        /* ================================
           UPDATE
        ================================= */

        if (currentParentId) {
            const { error } = await db
                .from("parents")
                .update(record)
                .eq(
                    "id",
                    currentParentId
                );

            if (error) {
                showFormMessage(
                    tr("error") +
                    error.message,
                    "error"
                );

                return;
            }
        }

        /* ================================
           INSERT
        ================================= */

        else {
            const { data, error } = await db
                .from("parents")
                .insert(record)
                .select("id")
                .single();

            if (error) {
                showFormMessage(
                    tr("error") +
                    error.message,
                    "error"
                );

                return;
            }

            savedParentId =
                data.id;
        }

        /* ================================
           LIEN PARENT / ELEVE
        ================================= */

        if (studentId) {
            const { error: linkError } =
                await saveParentStudentLink(
                    savedParentId,
                    studentId,
                    relationship
                );

            if (linkError) {
                if (
                    linkError.code === "23505"
                ) {
                    showFormMessage(
                        tr("duplicateLink"),
                        "error"
                    );
                } else {
                    showFormMessage(
                        tr("error") +
                        linkError.message,
                        "error"
                    );
                }

                return;
            }
        }

        dialog.close();

        await loadParents();

        showMessage(
            tr("saved"),
            "success"
        );
    }

    catch (error) {
        showFormMessage(
            tr("error") +
            (
                error?.message ||
                String(error)
            ),
            "error"
        );
    }

    finally {
        saveBtn.disabled = false;
    }
}


/* =========================================================
   SUPPRIMER PARENT
========================================================= */

async function deleteParent(parent) {
    if (
        !window.confirm(
            tr("confirmDelete")
        )
    ) {
        return;
    }

    const allowed =
        await checkAccess();

    if (!allowed) {
        return;
    }

    const { error } = await db
        .from("parents")
        .delete()
        .eq("id", parent.id);

    /*
       parent_students.parent_id utilise
       ON DELETE CASCADE.

       PostgreSQL supprime donc les liens
       associés au dossier.
    */

    if (error) {
        showMessage(
            tr("error") +
            error.message,
            "error"
        );

        return;
    }

    await loadParents();

    showMessage(
        tr("deleted"),
        "success"
    );
}


/* =========================================================
   EVENEMENTS
========================================================= */

languageBtn.addEventListener(
    "click",
    () => {
        language =
            language === "fr"
                ? "ar"
                : "fr";

        translatePage();
    }
);


addParentBtn.addEventListener(
    "click",
    openAddForm
);


refreshBtn.addEventListener(
    "click",
    async () => {
        refreshBtn.disabled = true;

        try {
            await loadStudents();
            await loadParents();
        } finally {
            refreshBtn.disabled = false;
        }
    }
);


closeDialogBtn.addEventListener(
    "click",
    () => {
        dialog.close();
    }
);


cancelBtn.addEventListener(
    "click",
    () => {
        dialog.close();
    }
);


searchInput.addEventListener(
    "input",
    renderParents
);


parentForm.addEventListener(
    "submit",
    saveParent
);


/* =========================================================
   INITIALISATION
========================================================= */

async function initializePage() {
    translatePage();

    const allowed =
        await checkAccess();

    if (!allowed) {
        return;
    }

    const studentsLoaded =
        await loadStudents();

    if (!studentsLoaded) {
        return;
    }

    await loadParents();
}


initializePage();
