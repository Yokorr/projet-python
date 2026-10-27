from pymart.exceptions import InsufficientStockError, InvalidDiscountError


class Product:

  def __init__(self, sku: str, name: str, price: float, quantity: int = 0):
    self.sku = sku
    self.name = name
    self.quantity = quantity
    self.price = price

  @property
  def price(self) -> float:
    return self._price

  @price.setter
  def price(self, value: float):
    if not isinstance(value, (int, float)):
      raise TypeError("Price must be a number")
    if value < 0:
      raise ValueError("Price cannot be negative")
    self._price = float(value)

  def apply_discount(self, percentage: float):
    if not 0 <= percentage <= 100:
      raise InvalidDiscountError(self.sku, percentage)
    factor = 1 - percentage / 100
    self.price = round(self.price * factor, 2)

  def sell(self, quantity: int):
    if quantity > self.quantity:
      raise InsufficientStockError(self.sku, quantity, self.quantity)
    self.quantity -= quantity

  def describe(self) -> str:
    return f"{self.name}: {self.price:.2f} EUR"

  def __repr__(self) -> str:
    return (
        f"Product(sku={self.sku!r}, name={self.name!r}, price={self.price:.2f},"
        f" quantity={self.quantity})"
    )


class PerishableProduct(Product):

  def __init__(
      self,
      sku: str,
      name: str,
      price: float,
      quantity: int,
      expiry_date: str,
  ):
    super().__init__(sku, name, price, quantity)
    self.expiry_date = expiry_date

  def describe(self) -> str:
    base = super().describe()
    return f"{base}, expires {self.expiry_date}"

  def __repr__(self) -> str:
    return (
        f"PerishableProduct(sku={self.sku!r}, name={self.name!r},"
        f" price={self.price:.2f}, quantity={self.quantity},"
        f" expiry_date={self.expiry_date!r})"
    )


class Customer:

  def __init__(
      self, customer_id: str, name: str, email: str, loyalty_points: int = 0
  ):
    self.customer_id = customer_id
    self.name = name
    self.loyalty_points = loyalty_points
    self.email = email

  @property
  def email(self) -> str:
    return self._email

  @email.setter
  def email(self, value: str):
    if not Customer.is_valid_email(value):
      raise ValueError(f"Invalid email: {value}")
    self._email = value

  @staticmethod
  def is_valid_email(email: str) -> bool:
    if not isinstance(email, str):
      return False
    clean = email.strip()
    if "@" not in clean:
      return False
    local, _, domain = clean.partition("@")
    if not local or not domain:
      return False
    if domain.startswith(".") or domain.endswith("."):
      return False
    return "." in domain

  def add_loyalty_points(self, amount: int):
    self.loyalty_points += amount

  def __repr__(self) -> str:
    return (
        f"Customer(customer_id={self.customer_id!r}, name={self.name!r},"
        f" email={self.email!r}, loyalty_points={self.loyalty_points})"
    )


class Order:

  def __init__(self, order_id: str, customer_id: str, order_date: str):
    self.order_id = order_id
    self.customer_id = customer_id
    self.order_date = order_date
    self.items = []

  def add_item(self, product: Product, quantity: int):
    product.sell(quantity)
    self.items.append((product, quantity, product.price))

  @property
  def total_amount(self) -> float:
    return round(sum(price * qty for _, qty, price in self.items), 2)

  def __repr__(self) -> str:
    return (
        f"Order(order_id={self.order_id!r}, customer_id={self.customer_id!r},"
        f" date={self.order_date!r}, total={self.total_amount:.2f})"
    )