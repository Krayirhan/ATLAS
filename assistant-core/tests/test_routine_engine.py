from app.routines.engine import RoutineEngine
from app.routines.models import RoutineCategory, RoutineDefinition, RoutineSource, RoutineStatus, RoutineStep


def test_routine_engine_list():
    engine = RoutineEngine()
    templates = engine.list_templates()
    assert len(templates) >= 6
    names = [template.name for template in templates]
    assert "çalışma modu" in names
    assert "oyun modu" in names
    assert "uyku modu" in names
    assert "toplantı modu" in names
    assert "eve geldim" in names
    assert "evden çıkıyorum" in names


def test_routine_engine_preview_work_requires_confirmation():
    engine = RoutineEngine()
    preview = engine.preview_routine("çalışma modunu başlat")
    assert preview.routine_name == "çalışma modu"
    assert preview.risk_level == "medium"
    assert preview.requires_confirmation is True
    assert preview.blocked is False
    assert len(preview.permission_decisions) == 3


def test_routine_engine_preview_sleep():
    engine = RoutineEngine()
    preview = engine.preview_routine("uyku modu")
    assert preview.requires_confirmation is True
    assert preview.risk_level == "medium"


def test_routine_engine_preview_leaving_home():
    engine = RoutineEngine()
    preview = engine.preview_routine("evden çıkıyorum")
    assert preview.risk_level == "high"
    assert preview.requires_confirmation is True


def test_routine_engine_run_dry_run():
    engine = RoutineEngine()
    result = engine.run_routine("çalışma modu")
    assert result.status == RoutineStatus.AWAITING_CONFIRMATION
    assert result.dry_run is True
    assert result.executed is False
    assert result.audit_metadata["execution_attempted"] is False


def test_routine_engine_run_unknown():
    engine = RoutineEngine()
    result = engine.run_routine("bilinmeyen bir mod")
    assert result.status == RoutineStatus.BLOCKED


def test_routine_engine_create_custom_routine():
    engine = RoutineEngine()
    definition = RoutineDefinition(
        routine_id="custom-focus-mode",
        name="odak modu",
        display_name="Odak Modu",
        description="Kisa odak rutini",
        category=RoutineCategory.CUSTOM,
        source=RoutineSource.USER_CREATED,
        steps=[
            RoutineStep(
                step_id="step-1",
                order=1,
                label="Browser ac",
                action_type="pc.open_app",
                target="Chrome",
                risk_level="low",
            )
        ],
    )
    engine.create_custom_routine(definition)
    assert engine.get_template("odak modu") is not None
