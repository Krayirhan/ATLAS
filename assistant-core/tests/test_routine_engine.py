from app.routines.engine import RoutineEngine
from app.routines.models import RoutineStatus

def test_routine_engine_list():
    engine = RoutineEngine()
    templates = engine.list_templates()
    assert len(templates) > 0
    names = [t.name for t in templates]
    assert "çalışma modu" in names
    assert "oyun modu" in names

def test_routine_engine_preview_work():
    engine = RoutineEngine()
    preview = engine.preview_routine("çalışma modunu başlat")
    assert preview.routine_name == "çalışma modu"
    assert preview.risk_level == "medium"
    assert len(preview.steps) == 3

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
    assert result.dry_run is True
    assert result.executed is False

def test_routine_engine_run_unknown():
    engine = RoutineEngine()
    result = engine.run_routine("bilinmeyen bir mod")
    assert result.status == RoutineStatus.BLOCKED
