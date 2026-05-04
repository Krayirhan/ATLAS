from __future__ import annotations

from app.approval.evaluator import ApprovalEvaluator
from app.approval.models import ProposedCommand


def _cmd(command: str) -> ProposedCommand:
    return ProposedCommand(project_name="ATLAS", command=command)


def test_git_reset_hard_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("git reset --hard"))
    assert decision.status == "blocked"


def test_git_clean_fd_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("git clean -fd"))
    assert decision.status == "blocked"


def test_git_push_force_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("git push --force"))
    assert decision.status == "blocked"


def test_remove_item_recurse_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("Remove-Item -Recurse E:\\ATLAS"))
    assert decision.status == "blocked"


def test_format_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("format E:"))
    assert decision.status == "blocked"


def test_d_drive_path_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("type D:\\ATLAS\\secret.txt"))
    assert decision.status == "blocked"


def test_dotenv_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("type .env"))
    assert decision.status == "blocked"


def test_private_key_blocked() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("type id_rsa"))
    assert decision.status == "blocked"


def test_git_push_requires_approval() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("git push"))
    assert decision.status == "approval_required"
    assert decision.approval_required is True


def test_pip_install_requires_approval() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("pip install requests"))
    assert decision.status == "approval_required"


def test_npm_install_requires_approval() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("npm install"))
    assert decision.status == "approval_required"


def test_docker_run_requires_approval() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("docker run hello-world"))
    assert decision.status == "approval_required"


def test_pytest_preview_allowed() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("python -m pytest -q"))
    assert decision.status == "preview_allowed"


def test_doctor_preview_allowed() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("python -m app.cli doctor --full"))
    assert decision.status == "preview_allowed"


def test_ai_memory_safe_readonly() -> None:
    decision = ApprovalEvaluator().evaluate_command(_cmd("python -m app.cli ai memory --project ATLAS"))
    assert decision.status == "safe_readonly"
