# FastAPI Auth Project

Monolithic FastAPI authentication service with:
- JWT Authentication (Access + Refresh Tokens)
- Token Families (Refresh Token Rotation & Reuse Detection)
- Token Blacklisting (Logout)
- User Management

## Structure

The project is organized into layers:
- **api**: Route handlers.
- **services**: Business logic.
- **repositories**: Database access.
- **models**: SQLAlchemy database models.
- **schemas**: Pydantic data transfer objects.
- **core**: Core infrastructure (security, config).

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   - Copy `.env.example` to `.env`
   - Update database credentials and secret keys.

4. Run migrations (once Alembic is configured):
   ```bash
   alembic upgrade head
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```