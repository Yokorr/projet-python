import sys
from sales_data import fake_sales


# Étape 1 : Générateur de nettoyage et de parsing (yield ligne par ligne)
def read_sales_records(lines):
    for line in lines:
        fields = [f.strip() for f in line.split(",")]
        sku, name, qty, price = fields
        yield [sku, int(qty), float(price)]


# Étape 4 : Closure pour configurer dynamiquement le filtre
def make_threshold_filter(min_amount: float):
    def keep(record):
        # record[1] = quantity, record[2] = unit_price
        return record[1] * record[2] >= min_amount

    return keep


def main():
    print("--- Étape 1 : Lecture en flux ---")
    records = read_sales_records(fake_sales(100000))
    print(next(records))
    print(next(records))

    print("\n--- Étape 2 : Filtrage paresseux (>= 90 EUR) ---")
    big_sales = (
        r for r in read_sales_records(fake_sales(100000)) if r[2] >= 90
    )
    print(next(big_sales))
    print(sum(1 for _ in big_sales))

    print("\n--- Étape 3 : Comparaison mémoire (Liste vs Générateur) ---")
    as_list = list(read_sales_records(fake_sales(100000)))
    as_stream = read_sales_records(fake_sales(100000))
    print("Taille liste :", len(as_list))
    print(
        "as_list prend plus de mémoire qu'as_stream :",
        sys.getsizeof(as_list) > sys.getsizeof(as_stream),
    )

    print("\n--- Étape 4 : Test de la closure (seuil 400 EUR sur 50 lignes) ---")
    big_orders = make_threshold_filter(400)
    stream_small = read_sales_records(fake_sales(50))
    print(next(filter(big_orders, stream_small)))

    print("\n--- Étape 5 : Pipeline complet chaîné (100 000 lignes) ---")
    stream = read_sales_records(fake_sales(100000))
    keep_big = make_threshold_filter(400)
    big = (r for r in stream if keep_big(r))

    total = sum(r[1] * r[2] for r in big)
    print(f"Big orders value: {total:.2f}")


if __name__ == "__main__":
    main()