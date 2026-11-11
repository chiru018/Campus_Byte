# Campus Byte – Architectural Decision Records (ADRs)

This document records the critical architectural and security decisions made during the development of Campus Byte.

---

## ADR 1: Primary Key Strategy – UUIDv4

- **Status:** Accepted
- **Context:** Deciding between sequential auto-incrementing integers (`BIGSERIAL`) versus 128-bit Universally Unique Identifiers (`UUIDv4`).
- **Decision:** Use UUIDv4 consistently across all entities.
- **Consequences:**
  - *Pros:* Eliminates Insecure Direct Object Reference (IDOR) enumeration attacks; allows client-safe IDs before database persistence; enables distributed multi-region replication.
  - *Cons:* Slightly larger index footprint compared to 4-byte integers (mitigated by B-Tree indexing).

---

## ADR 2: Password Hashing Algorithm – Argon2id

- **Status:** Accepted
- **Context:** Selecting an OWASP-compliant password hashing standard.
- **Decision:** Adopt `Argon2id` (winner of the Password Hashing Competition) via `argon2-cffi`, with backwards-compatible verification for legacy PBKDF2 hashes.
- **Consequences:**
  - *Pros:* Exceptional resistance against both GPU-based brute force and side-channel timing attacks through configurable memory and computational cost parameters.

---

## ADR 3: Stateless JWT with Server-Side Revocation Denylist

- **Status:** Accepted
- **Context:** Handling user logout in stateless JWT architectures without relying solely on client-side token deletion.
- **Decision:** Implement a `revoked_tokens` table in PostgreSQL storing the unique token identifier (`jti`) and token expiration date.
- **Consequences:**
  - *Pros:* Guarantees that logged-out tokens cannot access protected resources even before their natural 30-minute expiration.
  - *Pros:* Automatic cleanup query purges entries whose natural expiration has elapsed, preventing unbounded table growth.

---

## ADR 4: Role-Explicit Registration Endpoints

- **Status:** Accepted
- **Context:** Preventing privilege escalation where malicious users inject a privileged role (e.g. `role: "RESTAURANT_OWNER"`) into public customer sign-up forms.
- **Decision:** Provide discrete, controlled endpoints (`/api/auth/register/customer`, `/api/auth/register/restaurant-owner`, `/api/auth/register/delivery-partner`). The role is hardcoded on the backend service handler, never read from client input.
- **Consequences:**
  - *Pros:* Enforces structural validation and atomic provisioning (e.g. creating the restaurant profile or fleet record during the transaction).
  - *Pros:* Completely eliminates client-side role forgery.

---

## ADR 5: Dual-Mode Token Transport (Bearer & HttpOnly Cookie)

- **Status:** Accepted
- **Context:** Balancing seamless API testing/automation with browser XSS protection.
- **Decision:** Support both `Authorization: Bearer <token>` and `campus_byte_access_token` HttpOnly cookie.
- **Consequences:**
  - *Pros:* Web browsers enjoy HttpOnly protection from JavaScript cookie extraction, while API clients and automated tests can pass standard Bearer headers.
