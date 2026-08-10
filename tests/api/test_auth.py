def _register_payload(email="recruiter@example.com", password="secret123", role=1):
    return {
        "email": email,
        "full_name": "Test Recruiter",
        "password": password,
        "role": role,
    }


def test_register_success(client):
    response = client.post("/api/auth/register", json=_register_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "recruiter@example.com"
    assert body["user"]["role"] == 1


def test_register_duplicate_email_conflict(client):
    client.post("/api/auth/register", json=_register_payload())
    response = client.post("/api/auth/register", json=_register_payload())
    assert response.status_code == 409


def test_register_weak_password_rejected(client):
    payload = _register_payload(password="123")
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json=_register_payload())
    response = client.post(
        "/api/auth/login",
        json={"email": "recruiter@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["role"] == 1


def test_login_wrong_password_unauthorized(client):
    client.post("/api/auth/register", json=_register_payload())
    response = client.post(
        "/api/auth/login",
        json={"email": "recruiter@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_login_unknown_email_unauthorized(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "secret123"},
    )
    assert response.status_code == 401
