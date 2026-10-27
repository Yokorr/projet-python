import calendar
from datetime import datetime, timedelta
import os


def ensure_directory(path: str):
  os.makedirs(path, exist_ok=True)


def generate_daily_report(orders: list, target_date: str, out_dir: str):
  ensure_directory(out_dir)
  daily_orders = [o for o in orders if o.order_date == target_date]
  total_revenue = sum(o.total_amount for o in daily_orders)
  filename = f"report_daily_{target_date}.txt"
  filepath = os.path.join(out_dir, filename)

  next_review = datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=30)

  lines = [
      f"PyMart Daily Sales Report - {target_date}",
      f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      "=" * 40,
      f"Total orders : {len(daily_orders)}",
      f"Total revenue: {total_revenue:.2f} EUR",
      f"Next review  : {next_review.strftime('%Y-%m-%d')}",
      "=" * 40,
      "Orders detail:",
  ]
  if not daily_orders:
    lines.append("No orders for this date.")
  else:
    for order in daily_orders:
      lines.append(
          f"- Order {order.order_id} | Customer {order.customer_id} | Total:"
          f" {order.total_amount:.2f} EUR"
      )

  content = "\n".join(lines) + "\n"
  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
  return filepath, content


def generate_monthly_report(orders: list, target_month: str, out_dir: str):
  ensure_directory(out_dir)
  year_str, month_str = target_month.split("-")
  year = int(year_str)
  month = int(month_str)

  first_weekday, num_days = calendar.monthrange(year, month)
  month_orders = [o for o in orders if o.order_date.startswith(target_month)]
  total_revenue = sum(o.total_amount for o in month_orders)
  filename = f"report_monthly_{target_month}.txt"
  filepath = os.path.join(out_dir, filename)

  cal_text = calendar.month(year, month).strip()

  lines = [
      f"PyMart Monthly Sales Report - {target_month}",
      f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      "=" * 40,
      f"Month days   : {num_days}",
      f"Total orders : {len(month_orders)}",
      f"Total revenue: {total_revenue:.2f} EUR",
      "=" * 40,
      "Month calendar:",
      cal_text,
      "=" * 40,
      "Orders detail:",
  ]
  if not month_orders:
    lines.append("No orders for this month.")
  else:
    for order in month_orders:
      lines.append(
          f"- {order.order_date} | Order {order.order_id} | Customer"
          f" {order.customer_id} | {order.total_amount:.2f} EUR"
      )

  content = "\n".join(lines) + "\n"
  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
  return filepath, content