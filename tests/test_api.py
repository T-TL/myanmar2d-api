
from fastapi.testclient import TestClient
import app.main as main


def test_api_endpoints(tmp_path):
    # Use a temporary database for testing
    main.DATABASE_PATH = tmp_path / "test.db"

    with TestClient(main.app) as client:

        # Test homepage
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

        # Test health endpoint
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        # Test live endpoint with empty database
        response = client.get("/api/v1/live")
        assert response.status_code == 200
        assert response.json()["data_available"] is False

        # Test history endpoint
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        assert response.json()["count"] == 0

        # Test market status
        response = client.get("/api/v1/market/status")
        assert response.status_code == 200
        assert response.json()["market_status"] == "UNKNOWN"
