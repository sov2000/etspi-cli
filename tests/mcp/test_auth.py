"""
Tests for ETSPI MCP authentication manager
"""
import pytest
from pathlib import Path
from etspi.mcp.auth import EtspiAuthManager, AuthenticationError


def test_auth_manager_requires_auth_file(tmp_path, monkeypatch):
    """Test that AuthManager requires auth.env file"""
    # Point home to non-existent directory
    fake_home = tmp_path / "fake_home"
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    with pytest.raises(AuthenticationError) as exc_info:
        EtspiAuthManager()

    assert "Auth directory not found" in str(exc_info.value)


def test_auth_manager_loads_valid_config(tmp_path, monkeypatch):
    """Test that AuthManager loads valid configuration"""
    # Create fake auth directory and file
    fake_home = tmp_path / "fake_home"
    etspi_dir = fake_home / ".etspi"
    etspi_dir.mkdir(parents=True)

    auth_file = etspi_dir / "auth.env"
    auth_file.write_text(
        "key=test_api_key\n"
        "token=test_token\n"
        "refresh_token=test_refresh\n"
        "expiry=9999999999\n"
    )

    monkeypatch.setattr(Path, "home", lambda: fake_home)

    # Should not raise
    auth_manager = EtspiAuthManager()
    config = auth_manager.get_auth_config()

    assert config['key'] == 'test_api_key'
    assert config['token'] == 'test_token'
    assert config['refresh_token'] == 'test_refresh'
    assert config['expiry'] == 9999999999


def test_auth_manager_detects_missing_keys(tmp_path, monkeypatch):
    """Test that AuthManager detects missing required keys"""
    fake_home = tmp_path / "fake_home"
    etspi_dir = fake_home / ".etspi"
    etspi_dir.mkdir(parents=True)

    auth_file = etspi_dir / "auth.env"
    auth_file.write_text(
        "key=test_api_key\n"
        "token=test_token\n"
        # Missing refresh_token and expiry
    )

    monkeypatch.setattr(Path, "home", lambda: fake_home)

    auth_manager = EtspiAuthManager()

    with pytest.raises(AuthenticationError) as exc_info:
        auth_manager.get_auth_config()

    assert "missing required keys" in str(exc_info.value)


def test_auth_manager_validates_token(tmp_path, monkeypatch):
    """Test token validation"""
    import time

    fake_home = tmp_path / "fake_home"
    etspi_dir = fake_home / ".etspi"
    etspi_dir.mkdir(parents=True)

    # Expired token
    auth_file = etspi_dir / "auth.env"
    auth_file.write_text(
        "key=test_api_key\n"
        "token=test_token\n"
        "refresh_token=test_refresh\n"
        f"expiry={int(time.time()) - 3600}\n"  # 1 hour ago
    )

    monkeypatch.setattr(Path, "home", lambda: fake_home)

    auth_manager = EtspiAuthManager()
    assert not auth_manager.is_token_valid()

    # Valid token
    auth_file.write_text(
        "key=test_api_key\n"
        "token=test_token\n"
        "refresh_token=test_refresh\n"
        f"expiry={int(time.time()) + 3600}\n"  # 1 hour from now
    )

    auth_manager = EtspiAuthManager()
    assert auth_manager.is_token_valid()


def test_auth_manager_saves_tokens(tmp_path, monkeypatch):
    """Test saving refreshed tokens"""
    import time

    fake_home = tmp_path / "fake_home"
    etspi_dir = fake_home / ".etspi"
    etspi_dir.mkdir(parents=True)

    auth_file = etspi_dir / "auth.env"
    auth_file.write_text(
        "key=test_api_key\n"
        "token=old_token\n"
        "refresh_token=old_refresh\n"
        "expiry=1234567890\n"
    )

    monkeypatch.setattr(Path, "home", lambda: fake_home)

    auth_manager = EtspiAuthManager()

    # Save new tokens
    new_expiry = int(time.time()) + 3600
    auth_manager.save_tokens("new_token", "new_refresh", new_expiry)

    # Reload and verify
    config = auth_manager.get_auth_config()
    assert config['token'] == 'new_token'
    assert config['refresh_token'] == 'new_refresh'
    assert config['expiry'] == new_expiry
