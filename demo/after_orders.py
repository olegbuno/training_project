# "After" example — actual output from a fresh agent given the same task
# ("add a POST /orders endpoint") but pointed at CLAUDE.md first.
# This is a copy of the real generated code for side-by-side comparison
# against demo/before_orders.py; the live version that's actually wired
# into the app lives in app/schemas.py and app/orders.py.

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import CustomerNotFoundError
from app.models import Customer, Order


class OrderCreate(BaseModel):
    customer_id: int
    item_count: int = Field(gt=0)


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    item_count: int


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

    return OrderRead.model_validate(order)
