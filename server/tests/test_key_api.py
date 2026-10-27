"""Setting, checking and removing the Anthropic key from the app."""
import pytest


@pytest.fixture
def fake_check(monkeypatch, isolated_keys):
    calls = []

    def check(key, timeout=15.0):
        calls.append(key)
        if key.endswith("bad0"):
            raise ValueError("Anthropic rejected this key.")

    monkeypatch.setattr(isolated_keys, "check_key", check)
    return calls


def test_set_check_and_remove_key(client, fake_check, isolated_keys):
    st = client.get("/api/llm").json()
    assert not st["configured"] and st["key"]["source"] is None

    r = client.put("/api/llm/key", json={"key": "sk-ant-api03-good-1234", "remember": True})
    assert r.status_code == 200, r.text
    st = r.json()
    assert st["configured"] and st["key"]["source"] == "session" and st["key"]["hint"] == "…1234" and st["key"]["saved"]
    assert "good" not in r.text  # the key itself is never sent back
    assert fake_check == ["sk-ant-api03-good-1234"] and isolated_keys.key_file().exists()

    bad = client.put("/api/llm/key", json={"key": "sk-ant-api03-nope-bad0"})
    assert bad.status_code == 400 and "rejected" in bad.json()["detail"]
    assert client.get("/api/llm").json()["key"]["hint"] == "…1234"  # a rejected key changes nothing

    assert client.put("/api/llm/key", json={"key": "sk-ant has spaces in it"}).status_code == 400

    st = client.delete("/api/llm/key").json()
    assert not st["configured"] and not st["key"]["saved"] and not isolated_keys.key_file().exists()


def test_session_only_key_is_not_saved(client, fake_check, isolated_keys):
    st = client.put("/api/llm/key", json={"key": "sk-ant-api03-temp-7777", "remember": False}).json()
    assert st["configured"] and not st["key"]["saved"] and not isolated_keys.key_file().exists()


def test_key_cannot_be_changed_from_another_computer(client, fake_check, monkeypatch):
    from app.routers import ask
    monkeypatch.setattr(ask, "LOCAL", {"127.0.0.1"})  # the test client reports itself as "testclient"
    r = client.put("/api/llm/key", json={"key": "sk-ant-api03-good-1234"})
    assert r.status_code == 403 and client.delete("/api/llm/key").status_code == 403
