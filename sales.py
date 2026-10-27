raw_records = [
    "SKU100, Apples ,40, 2.50",
    "SKU200,Wireless Mouse,  15 , 19.99",
    "SKU300 , USB-C Charger,30,12.00",
]


records = []
for line in raw_records:
    fields = [f.strip() for f in line.split(",")]
    sku, name, qty, price = fields
    records.append([sku, name, int(qty), float(price)])


records.sort(key=lambda row: row[3])


print(" | ".join(["SKU", "Product", "Qty", "Price"]))
for sku, name, qty, price in records:
    cells = [sku, name, str(qty), f"{price:.2f}"]
    print(" | ".join(cells))


total = sum(r[2] * r[3] for r in records)
print(f"Total value: {total:.2f} EUR")