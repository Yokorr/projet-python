class PyMartError(Exception):
    """Classe de base pour toutes les erreurs métier de PyMart."""

    pass


class InsufficientStockError(PyMartError):
    def __init__(self, sku: str, requested: int, available: int) -> None:
        self.sku = sku
        self.requested = requested
        self.available = available
        msg = f"{sku}: asked {requested}, have {available}"
        super().__init__(msg)


class InvalidDiscountError(PyMartError):
    def __init__(self, sku: str, percentage: float) -> None:
        self.sku = sku
        self.percentage = percentage
        msg = f"{sku}: invalid discount {percentage}%"
        super().__init__(msg)