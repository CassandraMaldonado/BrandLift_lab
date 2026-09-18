from fastapi.testclient import TestClient
from brandlift_lab.api import app

client = TestClient(app)

def test_api_contract_and_validation():
    assert client.get("/api/health").json() == {"status": "ok"}
    result = client.get("/api/brief?seed=17&budget=1000000")
    assert result.status_code == 200
    assert result.json()["campaign"]["budget"] == 1_000_000
    assert client.get("/api/brief?budget=10").status_code == 422
