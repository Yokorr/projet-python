import calendar
from datetime import datetime, timedelta
import os
import time


def generate_report() -> str:
    """Simule la génération d'un rapport avec une pause de 0,5 seconde."""
    time.sleep(0.5)
    return "done"


def main():
    # --- Étape 1 : Horodatage, création du dossier et écriture du fichier ---
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M%S")
    filename = f"report_{stamp}.txt"

    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", filename)
    print(path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"PyMart report generated {now:%d/%m/%Y %H:%M}\n")

    print(os.path.getsize(path), "bytes")

    # --- Étape 2 : Calcul de la prochaine date de revue (+30 jours) ---
    review = now + timedelta(days=30)
    print("Next review:", review.strftime("%Y-%m-%d"))
    print("Days left:", (review - now).days)

    # --- Étape 3 : Mesure du temps d'exécution de la tâche ---
    start = time.time()
    result = generate_report()
    elapsed = time.time() - start
    print(f"{result} in {elapsed:.1f} s")

    # --- Étape 4 : Vérification d'année bissextile et calendrier du mois ---
    year = now.year
    month = now.month
    print(year, "leap year:", calendar.isleap(year))
    print(calendar.month(year, month))


if __name__ == "__main__":
    main()