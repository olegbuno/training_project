import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import CustomerNotFoundError
from app.models import Customer, Order
from app.schemas import OrderCreate, OrderRead

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/orders", response_model=OrderRead, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderRead:
    customer = db.get(Customer, payload.customer_id)
    if customer is None:
        raise CustomerNotFoundError(payload.customer_id)

    order = Order(customer_id=payload.customer_id, item_count=payload.item_count)
    db.add(order)
    db.commit()
    db.refresh(order)

    logger.info(
        "order_created",
        extra={"order_id": order.id, "customer_id": order.customer_id},
    )

    return OrderRead.model_validate(order)
