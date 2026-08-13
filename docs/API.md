# API Contract

Base URL: `http://localhost:8000/api/v1` (dev: `http://localhost:8000/api`)

## Health

```
GET /health
```
```json
{ "status": "ok" }
```

## Auth

### Register — `POST /auth/register`

Request:
```json
{
  "email": "recruiter@example.com",
  "full_name": "Jane Wright",
  "password": "secret123",
  "role": 1
}
```
Role `1` = Recruiter, role `2` = Customer (default: `2`).

`201 Created`:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "recruiter@example.com",
    "full_name": "Jane Wright",
    "role": 1,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

Errors: `409` duplicate email, `422` validation.

### Login — `POST /auth/login`

Request:
```json
{ "email": "recruiter@example.com", "password": "secret123" }
```

`200 OK` — same shape as register response.
`401` — invalid email or password.

## Authentication

Send the token on protected routes:

```
Authorization: Bearer <access_token>
```