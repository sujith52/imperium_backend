import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ NOW import your app and test client
from fastapi.testclient import TestClient
from app.main import app  # now Python can find 'app'

client = TestClient(app)
# or some invalid user_id



def test_get_existing_user():
    response = client.get("/profiles/users/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_get_nonexistent_user():
    response = client.get("/profiles/users/99999")
    assert response.status_code == 404

def test_get_existing_user():
    response = client.get("/profiles/users/1")
    assert response.status_code == 200
    data = response.json()
    assert "user_name" in data
    assert "total_interactions" in data
    assert "unique_items_viewed" in data
    assert "recommendations" in data


def test_get_nonexistent_item():
    response = client.get("/profiles/items/99999")
    assert response.status_code == 404



def test_user_not_found(client):
    response = client.get("/profiles/users/999")
    assert response.status_code == 404

def test_item_not_found(client):
    response = client.get("/profiles/items/999")
    assert response.status_code == 404

def test_empty_recommendations(client):
    response = client.get("/recommendations/999?limit=5&offset=0")
    assert response.status_code == 404 or response.json() == []
 # or whatever your logic returns




