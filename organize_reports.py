import os
import shutil


def main():
    # --- Étape 1 : Création de l'arborescence des dossiers ---
    print("--- Étape 1 : Création des dossiers ---")
    for year in ("2025", "2026"):
        os.makedirs(os.path.join("reports", year), exist_ok=True)

    print(sorted(os.listdir("reports")))

    # --- Étape 2 : Écriture des rapports de test ---
    print("\n--- Étape 2 : Écriture des fichiers ---")
    reports = {
        os.path.join("reports", "2025", "sales_q4.txt"): "Q4 2025 total: 1200",
        os.path.join("reports", "2026", "sales_q1.txt"): "Q1 2026 total: 950",
        os.path.join("reports", "2026", "draft.txt"): "TODO",
    }

    for path, text in reports.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")

    print(len(reports), "files written")

    # --- Étape 3 : Parcours complet avec os.walk ---
    print("\n--- Étape 3 : Liste des fichiers (os.walk) ---")
    for folder, subfolders, files in os.walk("reports"):
        subfolders.sort()
        for name in sorted(files):
            print(os.path.join(folder, name))

    # --- Étape 4 : Déplacement sous condition vers archive ---
    print("\n--- Étape 4 : Archivage des ventes 2025 ---")
    archive_dir = os.path.join("reports", "archive")
    os.makedirs(archive_dir, exist_ok=True)

    dir_2025 = os.path.join("reports", "2025")
    for name in os.listdir(dir_2025):
        if name.startswith("sales_"):
            shutil.move(
                os.path.join(dir_2025, name), os.path.join(archive_dir, name)
            )

    print(os.listdir(archive_dir))

    # --- Étape 5 : Nettoyage du brouillon et du dossier vide ---
    print("\n--- Étape 5 : Nettoyage ---")
    os.remove(os.path.join("reports", "2026", "draft.txt"))
    os.rmdir(dir_2025)  # Fonctionne uniquement car le dossier 2025 est vide

    print(sorted(os.listdir("reports")))


if __name__ == "__main__":
    main()