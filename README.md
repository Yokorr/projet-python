# PyMart — Back-Office Toolkit & Dashboard Opérationnel

Application de gestion commerciale et back-office développée en pur Python. Le projet répond à 100 % des exigences académiques (zéro dépendance externe, programmation orientée objet, polymorphisme, lecture par flux/générateurs, hiérarchie d'exceptions) tout en intégrant un tableau de bord web interactif propulsé par le module natif `http.server`.

---

## 1. Architecture du projet et rôle des fichiers

Le code est organisé sous la forme d'un package modulaire étanche garantissant la séparation des responsabilités :

```text
.
├── data/
│   ├── customers.txt          # Répertoire des comptes clients
│   ├── orders.txt             # Registre des commandes facturées
│   └── products.txt           # Catalogue des stocks et denrées périssables
├── docs/
│   ├── EVIDENCE.md            # Preuves d'exécution pour la notation
│   ├── presentation.html      # Présentation visuelle interactive du projet
│   └── screenshots/           # Captures d'écran de l'environnement CLI
├── pymart/
│   ├── __init__.py            # Initialisation du package
│   ├── cli.py                 # Interface terminal (argparse) : import, report, serve
│   ├── exceptions.py          # Hiérarchie des exceptions métier spécialisées
│   ├── models.py              # Modèles métier (Product, PerishableProduct, Customer, Order)
│   ├── parsers.py             # Parsers fainéants en streaming (générateurs yield)
│   ├── reports.py             # Moteur de génération des rapports (datetime, calendar, os)
│   └── server.py              # Serveur web natif http.server, API REST & dashboard UI
├── reports/                   # Dossier de persistance automatique des rapports
├── .gitignore
├── requirements.txt           # Fichier de dépendances (vide : standard library uniquement)
└── README.md                  # Documentation technique complète
```

---

## 2. Conformité aux exigences techniques (Socle académique)

### 2.1. Programmation orientée objet & polymorphisme
* **Classes de domaine (`pymart/models.py`)** : modélisation des entités avec attributs protégés et accesseurs `@property` (rejet strict des prix négatifs et contrôle du format de l'e-mail client).
* **Héritage et surcharge** : la classe `PerishableProduct` hérite de `Product` via `super().__init__()`.
* **Polymorphisme** : la méthode `describe()` adapte dynamiquement sa restitution textuelle selon la nature périssable ou standard du produit.

### 2.2. Exceptions métier contextualisées
* **Arborescence dédiée (`pymart/exceptions.py`)** : classe mère `PyMartError` dont dérivent `InsufficientStockError`, `InvalidDiscountError` et `DataValidationError`.
* **Traçabilité** : `DataValidationError` encapsule explicitement le chemin du fichier source et le numéro de ligne fautif, permettant un diagnostic immédiat sans crash de l'interpréteur.

### 2.3. Traitement par flux continu (Streaming)
* **Générateurs Python (`pymart/parsers.py`)** : la fonction `stream_file_lines` et les parsers associés exploitent `yield`. Les fichiers sont parcourus ligne par ligne, assurant une empreinte mémoire constante quel que soit le volume de données.

### 2.4. Manipulation des dates, calendriers et système de fichiers
* **Module `datetime`** : horodatage à la seconde des synthèses et calcul d'échéance à 30 jours via `timedelta`.
* **Module `calendar`** : calcul dynamique de la longueur des mois et intégration de la grille calendaire textuelle (`calendar.month`).
* **Module `os`** : création idempotente des dossiers (`os.makedirs(..., exist_ok=True)`) et concaténation sécurisée des chemins (`os.path.join`).

---

## 3. Extension bonus : Dashboard web & API native

En complément de la CLI, le module `pymart/server.py` met à disposition un back-office web complet sans aucun framework externe :
* **Serveur HTTP autonome** : sous-classe de `http.server.BaseHTTPRequestHandler` traitant les requêtes `GET` et `POST`.
* **API REST JSON** :
  * `GET /api/data` : extraction en mémoire des articles, clients et commandes.
  * `GET /api/audit` : audit en temps réel de la conformité de tous les fichiers textes.
  * `GET /api/reports/view?file=...` : consultation des rapports sauvegardés.
  * `POST /api/products` : ajout d'un article avec validation POO et écriture dans `data/products.txt`.
  * `POST /api/customers` : ajout d'un client avec vérification de l'e-mail dans `data/customers.txt`.
  * `POST /api/orders` : déduction atomique du stock avec levée d'erreur si stock insuffisant et écriture dans `data/orders.txt`.
  * `POST /api/reports` : génération synchrone des rapports journaliers ou mensuels.
* **Interface soignée** : design monopage épuré, navigation par onglets, modales de saisie et indicateurs de stock critique.

---

## 4. Guide d'exécution

### 4.1. Commandes CLI

```bash
# Afficher l'aide générale
python -m pymart.cli --help

# Importer et auditer les fichiers de données
python -m pymart.cli import --products data/products.txt --customers data/customers.txt --orders data/orders.txt

# Générer un rapport journalier (échéance à +30 jours)
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/

# Générer un rapport mensuel (avec calendrier textuel)
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

### 4.2. Lancer l'interface web locale

```bash
python -m pymart.cli serve --port 8000
```
L'interface est accessible depuis n'importe quel navigateur à l'adresse suivante : **http://localhost:8000**.

---

## 5. Preuves d'exécution et validation

Les captures d'écran attestant du bon fonctionnement de chaque commande et de l'interception gracieuse des erreurs sont documentées dans le fichier [`docs/EVIDENCE.md`](docs/EVIDENCE.md).