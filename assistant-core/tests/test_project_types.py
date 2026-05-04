import pytest

from app.projects.types import validate_project_type


def test_validate_project_type_ok() -> None:
    assert validate_project_type("  mlops-python  ") == "mlops-python"


def test_validate_python_cli_ok() -> None:
    assert validate_project_type("python-cli") == "python-cli"


def test_validate_project_type_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="Unsupported project type"):
        validate_project_type("unknown-stack")
