## Architecture & Deployment

### Database
- **Development/Testing**: SQLite (`sqlite:///./nimshop.db`) is used for local iteration and CI/CD tests due to its zero-configuration nature.
- **Production**: **PostgreSQL is strictly required**. The application utilizes `with_for_update()` for row-level locking to prevent inventory race conditions, a feature fully supported and optimized in PostgreSQL. Set `DATABASE_URL=postgresql://user:pass@host:5432/db` in production.

### Inventory Reservation (Lazy Expiry)
To prevent overselling without introducing complex background worker infrastructure (e.g., Celery), NimShop employs a **lazy reservation expiry** pattern:
1. When an order is created, inventory is immediately deducted, and a 15-minute `expires_at` timestamp is set.
2. If the user does not complete the Nimiq Pay transaction within 15 minutes, the *next* interaction with that order (e.g., a delayed verification request) will trigger the expiry check.
3. The order status is atomically transitioned to `cancelled`, and the inventory is restored exactly once.
4. Once `cancelled` or `failed`, an order cannot be retroactively marked as `paid`, ensuring state machine integrity.