import uuid
from app.routines.models import RoutineDefinition, RoutineStep, RoutineCategory, RoutineSource

def _create_step(order: int, label: str, action_type: str, target: str = None, parameters: dict = None, risk_level: str = "low", optional: bool = False) -> RoutineStep:
    return RoutineStep(
        step_id=str(uuid.uuid4()),
        order=order,
        label=label,
        action_type=action_type,
        target=target,
        parameters=parameters or {},
        risk_level=risk_level,
        optional=optional
    )

def get_builtin_templates() -> list[RoutineDefinition]:
    return [
        RoutineDefinition(
            routine_id="builtin-work-mode",
            name="çalışma modu",
            display_name="Çalışma Modu",
            description="Çalışma ortamına geçiş",
            category=RoutineCategory.WORK,
            source=RoutineSource.BUILT_IN,
            risk_level="medium",
            steps=[
                _create_step(1, "Ana uygulamayı aç", "pc.open_app", target="VS Code", risk_level="low"),
                _create_step(2, "Sesi kıs", "pc.volume.set", parameters={"value": 30}, risk_level="low"),
                _create_step(3, "Bildirim önerisi", "routine.note", target="bildirimleri azaltmayı öner", risk_level="low")
            ]
        ),
        RoutineDefinition(
            routine_id="builtin-gaming-mode",
            name="oyun modu",
            display_name="Oyun Modu",
            description="Oyun ortamına geçiş",
            category=RoutineCategory.GAMING,
            source=RoutineSource.BUILT_IN,
            risk_level="medium",
            steps=[
                _create_step(1, "Oyun uygulamasını aç", "pc.open_app", target="Steam", risk_level="low"),
                _create_step(2, "Sesi artır", "pc.volume.set", parameters={"value": 50}, risk_level="low"),
                _create_step(3, "Performans önerisi", "routine.note", target="performans modu önerisi", risk_level="low")
            ]
        ),
        RoutineDefinition(
            routine_id="builtin-sleep-mode",
            name="uyku modu",
            display_name="Uyku Modu",
            description="Uyku hazırlığı",
            category=RoutineCategory.SLEEP,
            source=RoutineSource.BUILT_IN,
            risk_level="medium",
            requires_confirmation=True,
            steps=[
                _create_step(1, "Sesi kıs", "pc.volume.set", parameters={"value": 10}, risk_level="low"),
                _create_step(2, "Yatak odası ışığını kapat", "device.turn_off", target="bedroom light", risk_level="medium"),
                _create_step(3, "Sabah hatırlatıcısı", "reminder.preview", target="sabah hatırlatıcı", risk_level="low", optional=True)
            ]
        ),
        RoutineDefinition(
            routine_id="builtin-meeting-mode",
            name="toplantı modu",
            display_name="Toplantı Modu",
            description="Toplantı ortamına hazırlık",
            category=RoutineCategory.MEETING,
            source=RoutineSource.BUILT_IN,
            risk_level="medium",
            steps=[
                _create_step(1, "Sesi kapat (Mute)", "pc.volume.mute_toggle", risk_level="low"),
                _create_step(2, "Toplantı uygulamasını aç", "pc.open_app", target="Zoom", risk_level="low"),
                _create_step(3, "Dikkat dağıtıcıları kapat", "routine.note", target="dikkat dağıtıcıları kapatmayı öner", risk_level="low")
            ]
        ),
        RoutineDefinition(
            routine_id="builtin-arriving-home",
            name="eve geldim",
            display_name="Eve Geldim",
            description="Eve varış rutini",
            category=RoutineCategory.ARRIVING_HOME,
            source=RoutineSource.BUILT_IN,
            risk_level="medium",
            steps=[
                _create_step(1, "Antre ışığını aç", "device.turn_on", target="hall light", risk_level="medium"),
                _create_step(2, "Müzik uygulamasını aç", "pc.open_app", target="Spotify", risk_level="low", optional=True)
            ]
        ),
        RoutineDefinition(
            routine_id="builtin-leaving-home",
            name="evden çıkıyorum",
            display_name="Evden Çıkıyorum",
            description="Evden ayrılış rutini",
            category=RoutineCategory.LEAVING_HOME,
            source=RoutineSource.BUILT_IN,
            risk_level="high",
            requires_confirmation=True,
            steps=[
                _create_step(1, "Tüm ışıkları kapat", "device.turn_off", target="lights", risk_level="medium"),
                _create_step(2, "Bilgisayarı kilitle", "pc.lock", target="computer", risk_level="high")
            ]
        )
    ]
