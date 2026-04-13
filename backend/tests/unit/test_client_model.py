"""Tests for the Client model."""
from app.models.client import Client


class TestClientModel:
    """Test suite for the Client model."""

    def test_create_client(self, db):
        """Test creating a new client."""
        client = Client(
            name="Acme Corp",
            code="ACME",
            industry="Mining",
            contact_person="Jane Doe",
            contact_email="jane@acme.com",
        )
        db.session.add(client)
        db.session.commit()

        assert client.id is not None
        assert client.name == "Acme Corp"
        assert client.code == "ACME"

    def test_validate_code_valid(self):
        """Test valid client code."""
        valid, result = Client.validate_code("ABC123")
        assert valid is True
        assert result == "ABC123"

    def test_validate_code_lowercase(self):
        """Test that code is uppercased."""
        valid, result = Client.validate_code("abc")
        assert valid is True
        assert result == "ABC"

    def test_validate_code_empty(self):
        """Test empty client code."""
        valid, result = Client.validate_code("")
        assert valid is False

    def test_validate_code_too_short(self):
        """Test code that is too short."""
        valid, result = Client.validate_code("AB")
        assert valid is False

    def test_validate_code_special_chars(self):
        """Test code with special characters."""
        valid, result = Client.validate_code("AB-C")
        assert valid is False

    def test_to_dict(self, sample_client):
        """Test serialization to dictionary."""
        d = sample_client.to_dict()
        assert d["name"] == "Test Corp"
        assert d["code"] == "TCORP"
        assert d["industry"] == "Finance"
        assert d["is_active"] is True
