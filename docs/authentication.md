# JWT Authentication System with FastAPI

## Overview

This project implements a JWT-based authentication system using **FastAPI**, **SQLAlchemy**, and **SQLite**. It is integrated into an expense management application and provides user registration, login, logout, token refresh, and authenticated access to expense endpoints.

The authentication system uses short-lived access tokens and long-lived refresh tokens stored in `HttpOnly` cookies.

## Features

- User registration and login
- JWT access and refresh token generation
- Short-lived access tokens and long-lived refresh tokens
- Secure cookie configuration
- Access token renewal without requiring the user to log in again
- Logout and token revocation using a token-version mechanism
- Validation of token signatures, expiration times, token types, and user identity
- Authentication-protected expense endpoints
- User-specific expense access
- SQLAlchemy database integration and Alembic migrations

## Technology Stack

- Python
- FastAPI
- PyJWT
- SQLAlchemy
- SQLite
- Alembic
- Pydantic Settings

## Token Configuration

| Token | Lifetime | Purpose |
|---|---|---|
| Access Token | 5 minutes | Authenticates requests to protected endpoints |
| Refresh Token | 24 hours | Obtains a new access token without logging in again |

Both tokens contain a user identifier, a token type, an issued-at timestamp, an expiration timestamp, and a token version.

Tokens are signed using the HS256 algorithm and a secret key configured through environment variables.

## Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Registers a new user |
| POST | `/auth/login` | Authenticates a user and sets authentication cookies |
| POST | `/auth/refresh-token` | Issues a new access token |
| POST | `/auth/logout` | Clears authentication cookies and revokes the current token version |

The application also provides protected expense endpoints. Authenticated users should only be able to access and modify their own expense records.

## Authentication Workflow

### 1. Registration

A user registers with a username and password. The password is stored as a password hash rather than as plaintext.

### 2. Login

The server verifies the submitted credentials. If they are valid, it generates an access token and a refresh token and sets them in cookies.

### 3. Accessing Protected Resources

The client sends the access-token cookie with requests to protected endpoints. The server validates the token and identifies the authenticated user before processing the request.

### 4. Refreshing the Access Token

When the access token expires, the client sends a request to `/auth/refresh-token`.

The server validates the refresh token, checks its expiration and token version, verifies that the user still exists, and issues a new access token.

The user can continue using the application without entering their credentials again, provided the refresh token remains valid.

### 5. Logout and Token Revocation

The logout endpoint clears the authentication cookies. The implementation also increments the user's token version when a valid refresh token is supplied.

Protected endpoints compare the token version against the current user record. A mismatch indicates that the token has been revoked.

## Cookie Security

The authentication cookies use the following settings:

- **HttpOnly:** Prevents client-side JavaScript from directly reading the cookie value.
- **Secure:** Ensures cookies are sent only over HTTPS when enabled.
- **SameSite:** Configured as `Lax` to reduce the risk of cross-site request forgery.
- **Path:** Set to `/` so that cookies are available to the application's endpoints.
- **Max-Age:** Limits how long cookies remain available in the browser.

For local development over HTTP, the `Secure` setting may be disabled. In production, it should be enabled and the application should be served over HTTPS.

## Why Use Cookies Instead of the Authorization Header?

JWTs can be transmitted through either cookies or an `Authorization: Bearer` header. Cookies offer some advantages, especially for browser-based applications, but they also introduce security considerations.

### Advantages

**Reduced exposure to JavaScript:** When a token is stored in an `HttpOnly` cookie, JavaScript cannot directly read its value. This reduces the risk of token theft through certain XSS attacks.

**Automatic transmission:** Browsers automatically attach eligible cookies to requests, reducing the need for application code to manage token headers.

**Centralized cookie controls:** Attributes such as `Secure`, `HttpOnly`, and `SameSite` provide browser-enforced controls over cookie handling.

### Security Considerations

**HttpOnly does not eliminate XSS:** Malicious JavaScript may still send authenticated requests from the affected page even if it cannot read the cookie.

**Cookies introduce CSRF considerations:** Since browsers attach cookies automatically, an attacker may attempt to trigger authenticated requests from another site. `SameSite` provides some protection, but sensitive applications may also require CSRF tokens and origin validation.

**Authorization headers have different trade-offs:** A bearer token explicitly attached by application code is not automatically included by the browser in the same way as a cookie. However, if stored in an unsafe location, such as accessible browser storage, it may be exposed to XSS.

The appropriate approach depends on the application architecture and threat model.

## JWT Validation and Error Handling

The authentication system validates incoming tokens before granting access.

Common failure conditions include:

| Condition | Expected response |
|---|---|
| Missing access token | `401 Unauthorized` |
| Invalid token signature or malformed token | `401 Unauthorized` |
| Expired access token | `401 Unauthorized` |
| Incorrect token type | `401 Unauthorized` |
| Missing or invalid user identifier | `401 Unauthorized` |
| User no longer exists | `401 Unauthorized` |
| Revoked token version | `401 Unauthorized` |
| Missing refresh token | `401 Unauthorized` |
| Expired or invalid refresh token | `401 Unauthorized` |

Clients should not treat an expired access token as proof that the user must log in again. They can attempt a refresh request when a valid refresh token is available.

## Environment Configuration

Create a `.env` file in the application's configuration directory and configure the required values:

```env
SQLALCHEMY_DATABASE_URL=sqlite:///./sqlite.db
JWT_SECRET_KEY=replace_with_a_strong_random_secret
COOKIE_SECURE=False
```

Use a strong, randomly generated secret for `JWT_SECRET_KEY`. Never commit real secrets or production credentials to version control.

For production deployments:

- Enable HTTPS.
- Set `COOKIE_SECURE=True`.
- Store secrets in an appropriate environment or secrets manager.
- Restrict database and application access.
- Configure suitable CSRF protections for cookie-authenticated requests.

The SQLite URL must be consistent with the application's configured database path. Ensure FastAPI and Alembic operate on the same database file.

## Database Migrations

Alembic manages database schema migrations.

From the repository root, apply existing migrations with:

```bash
alembic -c core/alembic.ini upgrade head
```

The command should be run against the database configured for the application.

## Running the Application

Activate the Python virtual environment and install the project's dependencies.

Start the development server from the repository root:

```bash
fastapi dev core/main.py
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

Use the actual host and port printed by the development server if they differ from the defaults.

## Testing the Authentication Flow

The following workflow can be tested through Swagger UI:

1. Register a user using `/auth/register`.
2. Log in using `/auth/login`.
3. Call a protected expense endpoint.
4. Call `/auth/refresh-token` and verify that the new access token works.
5. Call `/auth/logout`.
6. Verify that refresh and protected requests using the previous session are rejected.
7. Test missing, expired, malformed, and invalid tokens where applicable.

Swagger UI and browser cookie behavior can vary depending on the host, scheme, and cookie configuration. Confirm that cookies are actually being sent with requests when testing.

## Project Integration

The authentication system is integrated into the expense management application. Expense endpoints use the authenticated user's identity to restrict access to user-owned records.

This prevents one user from retrieving, updating, or deleting another user's expenses by changing an expense identifier.

## Security Notes and Limitations

- JWT payloads are signed, not encrypted. Do not store passwords or other secrets inside them.
- Access tokens should have a short lifetime.
- Refresh tokens must be validated independently from access tokens.
- Token-version revocation invalidates tokens whose version no longer matches the user's current version.
- Logout behavior should be tested for missing, invalid, and valid refresh cookies.
- Production systems may require refresh-token rotation, reuse detection, rate limiting, CSRF tokens, and stronger session-management controls.
- Password hashing should use an appropriate password-hashing algorithm.
- Never log raw authentication tokens or secrets.

## Conclusion

This project demonstrates JWT-based authentication in FastAPI, cookie-based token handling, access-token renewal, logout, token revocation, and authenticated integration with an expense management application.

It provides a practical foundation for understanding authentication workflows and the security trade-offs involved in browser-based JWT authentication.
