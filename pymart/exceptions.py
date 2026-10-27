class PyMartError(Exception):
    pass


class DataValidationError(PyMartError):
    def __init__(self, message, line_number=None, source_file=None):
        self.line_number = line_number
        self.source_file = source_file
        context = []
        if source_file:
            context.append(f"file: {source_file}")
        if line_number is not None:
            context.append(f"line: {line_number}")
        prefix = f"[{', '.join(context)}] " if context else ""
        super().__init__(f"{prefix}{message}")


class InsufficientStockError(PyMartError):
    def __init__(self, sku, requested, available):
        self.sku = sku
        self.requested = requested
        self.available = available
        super().__init__(f"{sku}: asked {requested}, have {available}")


class InvalidDiscountError(PyMartError):
    def __init__(self, sku, percentage):
        self.sku = sku
        self.percentage = percentage
        super().__init__(f"{sku}: invalid discount {percentage}%")