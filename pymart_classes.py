from pymart_errors import InsufficientStockError, InvalidDiscountError


class Product:
    def __init__(
        self, sku: str, name: str, price: float, quantity: int
    ) -> None:
        self.sku = sku
        self.name = name
        self.price = price
        self.quantity = quantity

    def sell(self, quantity: int) -> None:
        """Décrémente le stock ou lève une exception si stock insuffisant."""
        if quantity > self.quantity:
            raise InsufficientStockError(self.sku, quantity, self.quantity)
        self.quantity -= quantity

    def apply_discount(self, percentage: float) -> None:
        """Applique une réduction en pourcentage (0 à 100 %)."""
        if not 0 <= percentage <= 100:
            raise InvalidDiscountError(self.sku, percentage)
        factor = 1 - percentage / 100
        self.price = round(self.price * factor, 2)

    def describe(self) -> str:
        return f"{self.name}: {self.price:.2f} EUR"


class PerishableProduct(Product):
    def __init__(
        self,
        sku: str,
        name: str,
        price: float,
        quantity: int,
        expiry_date: str,
    ) -> None:
        super().__init__(sku, name, price, quantity)
        self.expiry_date = expiry_date

    def describe(self) -> str:
        base = super().describe()
        return f"{base}, expires {self.expiry_date}"


class ElectronicProduct(Product):
    def __init__(
        self,
        sku: str,
        name: str,
        price: float,
        quantity: int,
        warranty_months: int,
    ) -> None:
        super().__init__(sku, name, price, quantity)
        self.warranty_months = warranty_months

    def describe(self) -> str:
        base = super().describe()
        return f"{base}, {self.warranty_months} months warranty"