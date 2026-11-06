from unittest.mock import MagicMock

import pytest
from django.db.utils import ProgrammingError

import dropdb


@pytest.fixture
def database_connection(monkeypatch):
    connection = MagicMock()
    connection.is_usable.return_value = True
    connection.ops.quote_name.return_value = '"eph_123"'
    monkeypatch.setattr(dropdb, "connections", {"postgres": connection})
    monkeypatch.setattr(dropdb.django, "setup", MagicMock())
    return connection


def test_handler_skips_permanent_database_without_connecting(monkeypatch, database_connection):
    monkeypatch.setenv("DB_NAME", "dev")

    result = dropdb.handler({}, None)

    assert result == {"database": "dev", "status": "skipped"}
    database_connection.connect.assert_not_called()


def test_handler_rejects_non_generated_database_name(monkeypatch, database_connection):
    monkeypatch.setenv("DB_NAME", "customer_database")

    with pytest.raises(ValueError, match="generated ephemeral database name"):
        dropdb.handler({}, None)

    database_connection.connect.assert_not_called()


def test_handler_treats_missing_database_as_success(monkeypatch, database_connection):
    monkeypatch.setenv("DB_NAME", "eph_123")
    cursor = database_connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = None

    result = dropdb.handler({}, None)

    assert result == {"database": "eph_123", "status": "already_absent"}
    cursor.execute.assert_called_once_with(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        ("eph_123",),
    )


def test_handler_deletes_and_verifies_ephemeral_database(monkeypatch, database_connection):
    monkeypatch.setenv("DB_NAME", "eph_123")
    cursor = database_connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.side_effect = [(1,), None]

    result = dropdb.handler({}, None)

    assert result == {"database": "eph_123", "status": "deleted"}
    assert cursor.execute.call_args_list[1].args == (
        "SELECT pg_terminate_backend(pid) "
        "FROM pg_stat_activity "
        "WHERE pid <> pg_backend_pid() AND datname = %s",
        ("eph_123",),
    )
    assert cursor.execute.call_args_list[2].args == (
        'DROP DATABASE "eph_123" WITH ( FORCE )',
    )


def test_handler_propagates_database_deletion_errors(monkeypatch, database_connection):
    monkeypatch.setenv("DB_NAME", "eph_123")
    cursor = database_connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1,)
    cursor.execute.side_effect = [None, None, ProgrammingError("permission denied")]

    with pytest.raises(ProgrammingError, match="permission denied"):
        dropdb.handler({}, None)
