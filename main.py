from pymart_classes import Product
from pymart_errors import InsufficientStockError, InvalidDiscountError

# Objet de test : 15 unités en stock initial
mouse = Product("SKU200", "Wireless Mouse", 19.99, 15)

# Test 1 : tentative de vente de 20 unités sur 15 disponibles
try:
    mouse.sell(20)
except InsufficientStockError as error:
    print("Stock problem:", error)
    print("Missing:", error.requested - error.available)

# Test 2 : tentative d'application d'une remise hors limite (150 %)
try:
    mouse.apply_discount(150)
except InvalidDiscountError as error:
    print("Discount problem:", error)