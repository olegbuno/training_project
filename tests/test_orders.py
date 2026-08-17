from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Customer, Order


def test_create_order_returns_created_order(
    client: TestClient, customer: Customer, db_session: Session
) -> None:
    # Arrange
    payload = {"customer_id": customer.id, "item_count": 3}

    # Act
    response = client.post("/orders", json=payload)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer.id
    assert body["item_count"] == 3
    assert db_session.get(Order, body["id"]) is not None


def test_create_order_unknown_customer_returns_404(client: TestClient) -> None:
    # Arrange
    payload = {"customer_id": 999, "item_count": 1}

    # Act
    response = client.post("/orders", json=payload)

    # Assert
    assert response.status_code == 404
    assert "999" in response.json()["error"]


def test_create_order_rejects_non_positive_item_count(
    client: TestClient, customer: Customer
) -> None:
    # Arrange
    payload = {"customer_id": customer.id, "item_count": 0}

    # Act
    response = client.post("/orders", json=payload)

    # Assert
    assert response.status_code == 422
