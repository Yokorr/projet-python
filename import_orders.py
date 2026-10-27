from dataclasses import dataclass, field
from typing import Any, Dict, List


class ValidationError(Exception):
    """Exception métier pour signaler une ligne rejetée sans interrompre l'import."""

    pass


@dataclass
class ImportSummary:
    total: int = 0
    imported: int = 0
    rejected: int = 0
    failed: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)


def parse_and_validate_line(line: str) -> dict:
    cleaned_line = line.strip()
    if not cleaned_line:
        raise ValidationError("Ligne vide")

    parts = [p.strip() for p in cleaned_line.split("|")]
    if len(parts) < 4:
        raise ValidationError(
            f"Champs manquants ({len(parts)}/4 trouvés, attendu order_id|sku|qty|price)"
        )

    # Conversion de l'identifiant
    try:
        order_id = int(parts[0])
    except ValueError:
        raise ValidationError(f"order_id invalide : '{parts[0]}'")

    sku = parts[1]
    if not sku:
        raise ValidationError("SKU vide")

    # Conversion de la quantité
    try:
        quantity = int(parts[2])
    except ValueError:
        raise ValidationError(f"quantité invalide (entier requis) : '{parts[2]}'")

    # Conversion du prix unitaire
    try:
        unit_price = float(parts[3])
    except ValueError:
        raise ValidationError(f"prix unitaire invalide (nombre requis) : '{parts[3]}'")

    # Règles de cohérence métier
    if quantity <= 0:
        raise ValidationError(f"quantité non positive : {quantity}")
    if unit_price < 0:
        raise ValidationError(f"prix négatif : {unit_price}")

    return {
        "order_id": order_id,
        "sku": sku,
        "quantity": quantity,
        "unit_price": unit_price,
        "line_total": round(quantity * unit_price, 2),
    }


def import_orders(raw_lines: List[str]):
    summary = ImportSummary()
    imported_orders = []

    print("=== Démarrage de l'import ===")

    for index, line in enumerate(raw_lines, start=1):
        summary.total += 1
        try:
            # Bloc surveillé : conversion et validation ciblée
            order = parse_and_validate_line(line)

        except ValidationError as err:
            # Donnée invalide attendue -> on rejette et on continue
            summary.rejected += 1
            summary.errors.append({
                "row": index,
                "kind": "REJECTED",
                "message": str(err),
                "data": line,
            })

        except Exception as err:
            # Erreur technique ou bug imprévu -> tracé pour diagnostic
            summary.failed += 1
            summary.errors.append({
                "row": index,
                "kind": "FAILED",
                "message": f"Bug inattendu ({type(err).__name__}): {err}",
                "data": line,
            })

        else:
            # Exécuté UNIQUEMENT si aucune exception n'a été levée
            summary.imported += 1
            imported_orders.append(order)

    return imported_orders, summary


# Données de test contenant des lignes valides et des anomalies
raw_lines = [
    "1001|SKU-RED-CHAIR|2|39.99",
    "1002|SKU-BLUE-DESK|1|129.50",
    "1003|SKU-GREEN-LAMP|3",  # Champ manquant (IndexError / len < 4)
    "1004|SKU-WHITE-RUG|two|89.00",  # Entier invalide (ValueError)
    "1005|SKU-BLACK-SHELF|1|9.9x",  # Float invalide (ValueError)
    "oops-not-even-delimited",  # Format incorrect
    "",  # Ligne vide
]

orders, summary = import_orders(raw_lines)

# Affichage des commandes importées avec succès
print(f"\nCommandes importées ({len(orders)}) :")
for o in orders:
    print(
        f"  - Ordre #{o['order_id']} : {o['sku']} x{o['quantity']} = {o['line_total']} EUR"
    )

# Affichage du récapitulatif
print("\n=== Synthèse de l'import ===")
print(
    f"Total : {summary.total} | Importées : {summary.imported} | Rejetées : {summary.rejected} | Échecs critiques : {summary.failed}"
)

print("\nDétail des anomalies :")
for err in summary.errors:
    print(f"  Ligne {err['row']} [{err['kind']}] : {err['message']} (brut: '{err['data']}')")