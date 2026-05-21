# Le Schéma — Système de Gestion Scolaire

## Lancement
```bash
python3 main.py
```

## Identifiants par défaut
| Rôle | Utilisateur | Mot de passe |
|------|------------|--------------|
| Admin | admin | admin123 |
| Comptable | comptable | compta123 |
| Secrétaire | secretaire | secr123 |

## Modules
- 🏠 Tableau de bord avec statistiques et graphiques
- 🎓 Gestion des élèves (ajout, modification, photos)
- 💳 Paiements avec génération automatique de reçus PDF
- 👥 Personnel & Enseignants avec gestion des salaires
- 💸 Gestion des dépenses (fixes et variables)
- 🚌 Transport (bus, chauffeurs, abonnés)
- 📅 Emploi du temps hebdomadaire
- 📊 Rapports PDF & exports Excel
- ⚙️ Paramètres de l'école

## Structure
```
school_app/
├── main.py              # Point d'entrée
├── assets/              # Logo école
├── database/            # SQLite DB
├── receipts/            # Reçus PDF générés
├── backups/             # Sauvegardes DB
├── models/              # Modèles SQLAlchemy
├── ui/                  # Interfaces PySide6
├── services/            # Services (reçus, rapports)
└── themes/              # Style et constantes
```
