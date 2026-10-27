import os
from pymart.exceptions import DataValidationError, InsufficientStockError
from pymart.models import Customer, Order, PerishableProduct, Product


def stream_file_lines(filepath: str):
  if not os.path.exists(filepath):
    raise FileNotFoundError(f"Fichier introuvable : {filepath}")
  with open(filepath, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, start=1):
      clean = line.strip()
      if clean and not clean.startswith("#"):
        yield line_num, clean


def parse_products(filepath: str):
  for line_num, line in stream_file_lines(filepath):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 4:
      raise DataValidationError(
          "Format de produit invalide (colonnes manquantes)", line_num, filepath
      )
    sku = parts[0].upper()
    name = parts[1]
    try:
      price = float(parts[2])
      quantity = int(parts[3])
    except ValueError:
      raise DataValidationError(
          "Prix ou quantite non numerique", line_num, filepath
      )
    if price < 0 or quantity < 0:
      raise DataValidationError(
          "Valeur negative interdite pour prix ou quantite", line_num, filepath
      )
    if len(parts) >= 5 and parts[4]:
      yield PerishableProduct(sku, name, price, quantity, parts[4])
    else:
      yield Product(sku, name, price, quantity)


def parse_customers(filepath: str):
  for line_num, line in stream_file_lines(filepath):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 3:
      raise DataValidationError(
          "Format de client invalide (colonnes manquantes)", line_num, filepath
      )
    customer_id = parts[0].upper()
    name = parts[1]
    email = parts[2]
    loyalty_points = 0
    if len(parts) >= 4 and parts[3]:
      try:
        loyalty_points = int(parts[3])
      except ValueError:
        raise DataValidationError(
            "Points de fidelite invalides", line_num, filepath
        )
    try:
      yield Customer(customer_id, name, email, loyalty_points)
    except ValueError as err:
      raise DataValidationError(str(err), line_num, filepath)


def parse_orders(filepath: str, products_repo: dict):
  orders_map = {}
  for line_num, line in stream_file_lines(filepath):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 5:
      raise DataValidationError(
          "Format de commande invalide (colonnes manquantes)",
          line_num,
          filepath,
      )
    order_id, customer_id, order_date, sku, qty_str = parts[:5]
    sku = sku.upper()
    try:
      qty = int(qty_str)
      if qty <= 0:
        raise ValueError()
    except ValueError:
      raise DataValidationError(
          "Quantite commandee invalide", line_num, filepath
      )
    if sku not in products_repo:
      raise DataValidationError(f"Produit inconnu {sku}", line_num, filepath)
    product = products_repo[sku]
    if order_id not in orders_map:
      orders_map[order_id] = Order(order_id, customer_id, order_date)
    try:
      orders_map[order_id].add_item(product, qty)
    except InsufficientStockError as err:
      raise DataValidationError(str(err), line_num, filepath)

  for order in orders_map.values():
    yield order