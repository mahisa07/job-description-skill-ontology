from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Checking FastAPI App Endpoints:")
r1 = client.get("/")
print(f"GET / -> Status {r1.status_code}")
assert r1.status_code == 200, "Root route failed"
assert "<title>" in r1.text, "Index HTML not returned"

r2 = client.get("/api/jobs/published/list")
print(f"GET /api/jobs/published/list -> Status {r2.status_code}")
assert r2.status_code == 200

r3 = client.get("/api/jobs/notifications/list")
print(f"GET /api/jobs/notifications/list -> Status {r3.status_code}")
assert r3.status_code == 200

r4 = client.post("/api/auth/login", json={"email": "hr@skillontology.com", "password": "Hr@123"})
print(f"POST /api/auth/login (HR) -> Status {r4.status_code}")
assert r4.status_code == 200

r5 = client.post("/api/auth/login", json={"email": "user@skillontology.com", "password": "User@123"})
print(f"POST /api/auth/login (User) -> Status {r5.status_code}")
assert r5.status_code == 200

print("\nALL FASTAPI ENDPOINTS & HTML LOADING VERIFIED CLEANLY!")
