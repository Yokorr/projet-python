# Preuves d'exécution du projet PyMart

Ce document consigne les tests de bon fonctionnement de l'application en ligne de commande conformes au barème d'évaluation.

---

## 1. Menu d'aide de la CLI
Affichage des options et des sous-commandes disponibles :
![CLI Help](screenshots/01_cli_help.png)

---

## 2. Importation et validation des données
Lecture en streaming des fichiers et chargement sans erreur :
![Import Success](screenshots/02_import_success.png)

---

## 3. Rapport journalier
Génération sur disque avec calcul de l'échéance à +30 jours :
![Daily Report](screenshots/03_daily_report.png)

---

## 4. Rapport mensuel
Génération sur disque avec intégration du calendrier textuel :
![Monthly Report](screenshots/04_monthly_report.png)

---

## 5. Gestion robuste des erreurs
Interception d'une anomalie (prix négatif) avec indication du fichier et de la ligne, sans plantage du terminal :
![Error Handling](screenshots/05_error_handling.png)
