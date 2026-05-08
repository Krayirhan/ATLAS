from app.execution.allowlist import ExecutionAllowlist


def test_pc_open_app_allowed() -> None:
    assert ExecutionAllowlist().is_action_allowed("pc.open_app") is True


def test_pc_system_info_allowed() -> None:
    assert ExecutionAllowlist().is_action_allowed("pc.system_info") is True


def test_shell_execute_unrestricted_blocked() -> None:
    assert ExecutionAllowlist().is_action_allowed("shell.execute_unrestricted") is False


def test_file_delete_blocked() -> None:
    assert ExecutionAllowlist().is_action_allowed("file.delete") is False


def test_registry_edit_blocked() -> None:
    assert ExecutionAllowlist().is_action_allowed("registry.edit") is False


def test_device_turn_on_not_pc_eligible() -> None:
    assert ExecutionAllowlist().is_action_allowed("device.turn_on") is False


def test_unknown_target_for_open_app_is_not_allowed() -> None:
    assert ExecutionAllowlist().is_target_allowed("pc.open_app", "Unknown App") is False

