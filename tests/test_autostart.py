import pytest

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


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (0, autostart.Status(False)),
        (1, autostart.Status(False, False, "autostart.blocked_user")),
        (2, autostart.Status(True)),
        (3, autostart.Status(False, False, "autostart.blocked_policy")),
        (4, autostart.Status(True, False, "autostart.managed_policy")),
    ],
)
def test_startup_task_states(state, expected):
    assert autostart._state_to_status(state) == expected
