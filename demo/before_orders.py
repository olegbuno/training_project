# Illustrative "before" example — typical output WITHOUT the CLAUDE.md rules in place.
# Not wired into the app; kept only for comparison against demo/after_orders.py.

from fastapi import FastAPI

app = FastAPI()

orders = []


@app.post("/orders")
async def create_order(payload: dict):
    try:
        customer_id = payload["customer_id"]
        item_count = payload["item_count"]
        order = {"id": len(orders) + 1, "customer_id": customer_id, "item_count": item_count}
        orders.append(order)
        print(f"created order {order['id']}")
        return order
    except:
        return {"error": "something went wrong"}
