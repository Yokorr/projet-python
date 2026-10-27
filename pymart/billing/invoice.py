from ..inventory.stock import check_stock


def create_invoice(sku, quantity, price):
    total = quantity * price
    status = check_stock(sku, quantity)
    return f"Invoice {sku}: {total:.2f} EUR ({status})"