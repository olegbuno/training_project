from app.database import Base, SessionLocal, engine
from app.models import Customer

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    if db.get(Customer, 1) is None:
        db.add(Customer(id=1, name="Ada Lovelace"))
        db.commit()
