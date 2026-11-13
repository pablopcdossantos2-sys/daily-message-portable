from dailymessage import autostart, winapi


def test_autostart_is_store_only_outside_package(monkeypatch):
    monkeypatch.setattr(winapi, "IS_WINDOWS", True)
    monkeypatch.setattr(winapi, "is_packaged", lambda: False)
    status = autostart.get_status()
    assert status.enabled is False
    assert status.can_change is False
    assert status.note_key == "autostart.store_only"
    assert autostart.set_enabled(True) == status


def test_autostart_unavailable_off_windows(monkeypatch):
    monkeypatch.setattr(winapi, "IS_WINDOWS", False)
    status = autostart.get_status()
    assert status.enabled is False
    assert status.can_change is False
    assert status.note_key == "autostart.unsupported"
