import os
import pytest
import db

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Fixture para aislar cada test en un archivo temporal de base de datos."""
    test_file = tmp_path / "test_data.txt"
    monkeypatch.setattr(db, "DB_FILE", str(test_file))
    db.INDEX.clear()
    yield
    db.INDEX.clear()


def test_set_and_get(temp_db):
    """Comprueba que se puede insertar una clave y leerla correctamente."""
    db.set("greeting", "Hello")
    assert db.get("greeting") == "Hello"


def test_update_value(temp_db):
    """Comprueba que al modificar una clave se obtiene el valor más reciente."""
    db.set("status", "active")
    db.set("status", "updated")
    assert db.get("status") == "updated"


def test_delete_with_tombstone(temp_db):
    """Comprueba que el borrado lógico (tombstone) elimina la clave del índice."""
    db.set("temp", "data")
    assert db.get("temp") == "data"
    
    db.delete("temp")
    assert db.get("temp") is None


def test_utf8_encoding_and_cyrillic(temp_db):
    """Comprueba el soporte robusto de UTF-8 con caracteres internacionales (ej. ruso)."""
    db.set("cliente_Москва", "Привет, мир")
    assert db.get("cliente_Москва") == "Привет, мир"


def test_non_existent_key(temp_db):
    """Comprueba que buscar una clave que no existe devuelve None."""
    assert db.get("key_que_no_existe") is None