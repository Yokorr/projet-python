def check_stock(sku, quantity):
    return f"{sku}: {quantity} unit(s) in stock"


def restock(sku, amount):
    return f"{sku}: restocked +{amount}"