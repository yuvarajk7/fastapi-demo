# app/tests/test_inventory.py

from fastapi.testclient import TestClient

from app.dependencies.auth import get_authenticated_user
from app.main import app
from app.middlewares.authentication import AuthenticatedUser
from app.tests.test_session import initialize_test_db, get_test_db
from app.tests.test_session import get_test_db
from app.db.session import get_db

# Initialize the test database (drop + create + seed)
initialize_test_db()

mock_admin = AuthenticatedUser(id="1", email="admin@test.com", roles=["admin"])
# since we mock the auth user no need to generate token
app.dependency_overrides[get_authenticated_user] = lambda : mock_admin

app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)

def get_token(email: str, password: str) -> str:
    """Helper to login and return access token for auth headers."""
    response = client.post("/auth/token", json={"email": email, "password": password})
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


def test_inventory_update_add_stock():
    """Test adding stock with a valid admin user."""
    #token = get_token("admintest@globomantics.com", "password")

    payload = {
        "product_id": 1,
        "location_id": 1,
        "quantity_change": 5,
        "reorder_point": 3
    }

    response = client.put(
        "/inventory/",
        json=payload
        #headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == 1
    assert data["location_id"] == 1
    assert data["quantity"] >= 5


def test_inventory_update_insufficient_stock():
    """Test removing too much stock, should trigger 400 error."""
    token = get_token("admintest@globomantics.com", "password")

    payload = {
        "product_id": 1,
        "location_id": 1,
        "quantity_change": -999,
        "reorder_point": 5,
        "reason": "Unit test simulating stock depletion"
    }

    response = client.put(
        "/inventory/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] is True
    assert "Insufficient stock" in body["message"]
    assert body["details"]["product_id"] == 1
    assert body["details"]["location_id"] == 1
