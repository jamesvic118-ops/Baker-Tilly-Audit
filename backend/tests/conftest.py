"""Test configuration and fixtures."""
import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.utils.auth import generate_token


@pytest.fixture(scope="function")
def app():
    """Create a test application instance."""
    app = create_app("testing")
    yield app


@pytest.fixture(scope="function")
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Create a test database."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        first_name="Admin",
        last_name="Tester",
        role="admin",
        department="Admin",
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def manager_user(db):
    """Create a manager user for testing."""
    user = User(
        email="manager@test.com",
        first_name="Manager",
        last_name="Tester",
        role="manager",
        department="Audit",
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def staff_user(db):
    """Create a staff user for testing."""
    user = User(
        email="staff@test.com",
        first_name="Staff",
        last_name="Tester",
        role="staff",
        department="Audit",
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_client(db):
    """Create a sample client."""
    c = Client(
        name="Test Corp",
        code="TCORP",
        industry="Finance",
        contact_person="John Doe",
        contact_email="john@testcorp.com",
        is_active=True,
    )
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture
def sample_project(db, sample_client, manager_user):
    """Create a sample project."""
    p = Project(
        name="Annual Audit 2024",
        code="AA2024",
        description="Annual audit engagement",
        client_id=sample_client.id,
        manager_id=manager_user.id,
        status="active",
        budget_hours=100.0,
        engagement_type="audit",
        is_billable=True,
    )
    db.session.add(p)
    db.session.commit()
    return p


@pytest.fixture
def admin_token(app, admin_user):
    """Generate a JWT token for the admin user."""
    with app.app_context():
        return generate_token(admin_user.id)


@pytest.fixture
def manager_token(app, manager_user):
    """Generate a JWT token for the manager user."""
    with app.app_context():
        return generate_token(manager_user.id)


@pytest.fixture
def staff_token(app, staff_user):
    """Generate a JWT token for the staff user."""
    with app.app_context():
        return generate_token(staff_user.id)


@pytest.fixture
def auth_headers(admin_token):
    """Return authorization headers for admin."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
