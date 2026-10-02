# Système de Gestion des Factures (Django Invoice System)

Application de facturation et de gestion des clients avec génération et téléchargement de factures en format PDF sous Django.

## Accès rapide
- **Documentation complète :** Voir le fichier détaillé [DOCUMENTATION.md](file:///c:/FACTURATION_DJANGO/DOCUMENTATION.md)
- **Application :** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Administration Django :** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Lancer le projet
```powershell
# 1. Activer l'environnement virtuel
.\monenv\Scripts\Activate.ps1

# 2. Lancer le serveur de développement
python manage.py runserver 127.0.0.1:8000

# 3. Lancer les tests unitaires
python manage.py test
```

## Fonctionnalités principales
- Enregistrement des clients et suivi des coordonnées.
- Création de factures avec lignes d'articles dynamiques et calcul automatique des totaux.
- Téléchargement automatique ou à la demande des factures au format PDF (via `xhtml2pdf`).
- Modification rapide du statut (Payé / Impayé) et suppression sécurisée.
- Recherche en direct et pagination.
