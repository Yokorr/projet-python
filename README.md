# PyMart — Outil de gestion back-office en ligne de commande

Application en ligne de commande (CLI) modulaire développée pour automatiser la gestion des opérations de vente de PyMart : importation et validation des exports de caisse, suivi des stocks, traitement des commandes et génération de rapports opérationnels horodatés.

---

## 1. Correspondance des fichiers avec le rendu final

L'architecture du projet sépare strictement les responsabilités au sein d'un package Python modulaire `pymart/`, sans dépendance externe :

* **`pymart/models.py`** : Modélisation métier (POO).
  * `Product` : Gestion du catalogue, des stocks et encapsulation des prix par propriété.
  * `PerishableProduct` : Hérite de `Product` et applique le polymorphisme sur la méthode `describe()` avec la date d'expiration.
  * `Customer` : Validation du format des adresses e-mail par accesseur (`@property`).
  * `Order` : Assemblage du panier client, décrémentation automatique du stock et calcul du montant total.
* **`pymart/exceptions.py`** : Hiérarchie d'exceptions personnalisées.
  * `PyMartError` : Classe de base de toutes les erreurs de l'application.
  * `DataValidationError` : Exception enrichie avec le fichier source et le numéro de ligne pour un diagnostic précis.
  * `InsufficientStockError` : Erreur levée si une commande dépasse les quantités en réserve.
  * `InvalidDiscountError` : Erreur levée si un pourcentage de remise sort de l'intervalle [0, 100].
* **`pymart/parsers.py`** : Traitement et nettoyage des données en flux (*streaming*).
  * Fonctions génératrices utilisant `yield` pour analyser les fichiers volumineux ligne par ligne sans saturer la mémoire vive.
  * Validation stricte des types de données, des colonnes obligatoires et normalisation des chaînes.
* **`pymart/reports.py`** : Moteur de génération des rapports.
  * Création automatique des répertoires sur le disque (`os.makedirs`).
  * Calcul d'échéance à 30 jours avec `datetime` et `timedelta`.
  * Intégration du calendrier mensuel textuel dynamique avec `calendar`.
* **`pymart/cli.py`** : Point d'entrée de l'application.
  * Analyse des arguments en ligne de commande (`argparse`) pour les sous-commandes `import` et `report`.
  * Capture des exceptions pour afficher des messages d'erreur clairs sans arrêt brutal du programme.
* **`data/`** : Répertoire contenant les fichiers de test (`products.txt`, `customers.txt`, `orders.txt`).
* **`reports/`** : Dossier de sortie généré à l'exécution contenant les fichiers de rapport écrits sur le disque.
* **`requirements.txt`** : Déclaration des dépendances (projet autonome reposant uniquement sur la bibliothèque standard Python).

---

## 2. Ce qui a été réalisé étape par étape

1. **Modélisation orientée objet et polymorphisme** :
   * Création des classes métiers avec contrôle des types et valeurs positives.
   * Utilisation de `super().__init__()` pour spécialiser `PerishableProduct`.
   * Surcharge polymorphique de `describe()` appelée de façon uniforme sur les collections de produits.
2. **Arborescence d'exceptions métier** :
   * Définition d'erreurs spécialisées dérivées d'une classe parente commune.
   * Protection de l'état des objets : rejet des ventes impossibles et des remises invalides.
3. **Traitement par générateurs (*data streaming*)** :
   * Lecture paresseuse (*lazy evaluation*) via `yield` pour traiter les exports de vente volumineux sans chargement intégral en RAM.
4. **Gestion du système de fichiers et des dates** :
   * Chemins d'accès portables multiplateformes avec `os.path.join`.
   * Horodatage normé des fichiers et calculs calendaires automatiques.
5. **Interface en ligne de commande (CLI)** :
   * Implémentation complète des commandes `import` et `report` (`daily` et `monthly`).
   * Gestion d'erreurs globale garantissant une exécution résiliente.

---

## 3. Guide d'exécution

### 3.1. Afficher l'aide de la commande
```bash
python -m pymart.cli --help
```

### 3.2. Importer et valider les fichiers de données
```bash
python -m pymart.cli import --products data/products.txt --customers data/customers.txt --orders data/orders.txt
```

### 3.3. Générer le rapport journalier (avec échéance à +30 jours)
```bash
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
```

### 3.4. Générer le rapport mensuel (avec calendrier textuel intégré)
```bash
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

---

## 4. Exemple d'exécution en console

```text
$ python -m pymart.cli import --products data/products.txt --customers data/customers.txt --orders data/orders.txt
Donnees importees avec succes :
- Produits  : 5
- Clients   : 3
- Commandes : 3

$ python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
Rapport journalier genere : reports/report_daily_2026-06-30.txt
PyMart Daily Sales Report - 2026-06-30
Generated at: 2026-10-27 10:30:17
========================================
Total orders : 2
Total revenue: 27.79 EUR
Next review  : 2026-07-30
========================================
Orders detail:
- Order ORD001 | Customer CUST001 | Total: 22.99 EUR
- Order ORD002 | Customer CUST002 | Total: 4.80 EUR

$ python -m pymart.cli report --type monthly --month 2026-06 --out reports/
Rapport mensuel genere : reports/report_monthly_2026-06.txt
PyMart Monthly Sales Report - 2026-06
Generated at: 2026-10-27 10:30:17
========================================
Month days   : 30
Total orders : 3
Total revenue: 426.79 EUR
========================================
Month calendar:
June 2026
Mo Tu We Th Fr Sa Su
 1  2  3  4  5  6  7
 8  9 10 11 12 13 14
15 16 17 18 19 20 21
22 23 24 25 26 27 28
29 30
========================================
Orders detail:
- 2026-06-30 | Order ORD001 | Customer CUST001 | 22.99 EUR
- 2026-06-30 | Order ORD002 | Customer CUST002 | 4.80 EUR
- 2026-06-15 | Order ORD003 | Customer CUST003 | 399.00 EUR
```