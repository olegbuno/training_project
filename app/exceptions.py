class AppError(Exception):
    status_code = 500
    message = "Internal error"


class CustomerNotFoundError(AppError):
    status_code = 404

    def __init__(self, customer_id: int) -> None:
        self.message = f"Customer {customer_id} not found"
        super().__init__(self.message)
