def fake_sales(count: int):
    """Générateur simulant un flux de lignes de vente brutes."""
    for i in range(count):
        qty = 1 + i % 5
        price = 5 + (i * 7) % 95
        yield f"SKU{i:05d}, Item {i} ,{qty}, {price}.50"