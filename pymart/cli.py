import argparse
from datetime import datetime
import sys
from pymart.exceptions import DataValidationError, PyMartError
from pymart.parsers import parse_customers, parse_orders, parse_products
from pymart.reports import generate_daily_report, generate_monthly_report
from pymart.server import run_server


def handle_import(args):
  try:
    products = {p.sku: p for p in parse_products(args.products)}
    customers = {c.customer_id: c for c in parse_customers(args.customers)}
    orders = list(parse_orders(args.orders, products))

    print("Donnees importees avec succes :")
    print(f"- Produits  : {len(products)}")
    print(f"- Clients   : {len(customers)}")
    print(f"- Commandes : {len(orders)}")
    return 0
  except (DataValidationError, FileNotFoundError, PyMartError) as err:
    print(f"Erreur d'importation : {err}", file=sys.stderr)
    return 1


def handle_report(args):
  try:
    products = {p.sku: p for p in parse_products(args.products)}
    orders = list(parse_orders(args.orders, products))

    out_dir = args.out or "reports"

    if args.type == "daily":
      target_date = args.date or datetime.now().strftime("%Y-%m-%d")
      path, content = generate_daily_report(orders, target_date, out_dir)
      print(f"Rapport journalier genere : {path}")
      print(content)
    elif args.type == "monthly":
      target_month = args.month or datetime.now().strftime("%Y-%m")
      path, content = generate_monthly_report(orders, target_month, out_dir)
      print(f"Rapport mensuel genere : {path}")
      print(content)
    return 0
  except (DataValidationError, FileNotFoundError, PyMartError) as err:
    print(f"Erreur lors du rapport : {err}", file=sys.stderr)
    return 1


def handle_serve(args):
  try:
    run_server(
        port=args.port,
        products_path=args.products,
        customers_path=args.customers,
        orders_path=args.orders,
        reports_dir=args.out,
    )
    return 0
  except Exception as err:
    print(f"Erreur serveur : {err}", file=sys.stderr)
    return 1


def build_parser():
  parser = argparse.ArgumentParser(
      prog="pymart", description="PyMart Back-Office Management Toolkit"
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  import_parser = subparsers.add_parser(
      "import", help="Importer et valider les fichiers de donnees"
  )
  import_parser.add_argument(
      "--products", default="data/products.txt", help="Chemin vers products.txt"
  )
  import_parser.add_argument(
      "--customers",
      default="data/customers.txt",
      help="Chemin vers customers.txt",
  )
  import_parser.add_argument(
      "--orders", default="data/orders.txt", help="Chemin vers orders.txt"
  )

  report_parser = subparsers.add_parser(
      "report", help="Generer des rapports d'activite"
  )
  report_parser.add_argument(
      "--type",
      choices=["daily", "monthly"],
      required=True,
      help="Type de rapport",
  )
  report_parser.add_argument(
      "--date", help="Date cible pour le rapport journalier (YYYY-MM-DD)"
  )
  report_parser.add_argument(
      "--month", help="Mois cible pour le rapport mensuel (YYYY-MM)"
  )
  report_parser.add_argument(
      "--out", default="reports", help="Dossier de destination"
  )
  report_parser.add_argument(
      "--products", default="data/products.txt", help="Chemin vers products.txt"
  )
  report_parser.add_argument(
      "--customers",
      default="data/customers.txt",
      help="Chemin vers customers.txt",
  )
  report_parser.add_argument(
      "--orders", default="data/orders.txt", help="Chemin vers orders.txt"
  )

  serve_parser = subparsers.add_parser(
      "serve", help="Lancer l'interface web locale du back-office"
  )
  serve_parser.add_argument(
      "--port", type=int, default=8000, help="Port d'ecoute HTTP (defaut: 8000)"
  )
  serve_parser.add_argument(
      "--products", default="data/products.txt", help="Chemin vers products.txt"
  )
  serve_parser.add_argument(
      "--customers",
      default="data/customers.txt",
      help="Chemin vers customers.txt",
  )
  serve_parser.add_argument(
      "--orders", default="data/orders.txt", help="Chemin vers orders.txt"
  )
  serve_parser.add_argument(
      "--out", default="reports", help="Dossier de destination des rapports"
  )

  return parser


def main():
  parser = build_parser()
  args = parser.parse_args()

  if args.command == "import":
    sys.exit(handle_import(args))
  elif args.command == "report":
    sys.exit(handle_report(args))
  elif args.command == "serve":
    sys.exit(handle_serve(args))


if __name__ == "__main__":
  main()