"""Built-in demo scenarios for Sprint 50 end-to-end personal assistant demo.

14 scenarios covering all major ATLAS preview flows.
"""

from __future__ import annotations

from app.demo.models import CommandSurface, DemoCategory, DemoScenario
from app.quality.models import SAFETY_INVARIANT_EXPECTED

_SAFE_FLAGS = dict(SAFETY_INVARIANT_EXPECTED)

BUILTIN_SCENARIOS: list[DemoScenario] = [
    # A — Chat / PC preview
    DemoScenario(
        scenario_id="chat_chrome_open",
        title="Chat: Chrome'u aç (PC preview)",
        description=(
            "Kullanıcı Chrome'u açmak ister. "
            "ATLAS bir pc.open_app action önizlemesi oluşturur, gerçek execution yapmaz."
        ),
        category=DemoCategory.CHAT,
        input_text="Chrome'u aç",
        command_surface=CommandSurface.CHAT,
        expected_response_type="action_preview|confirmation_required",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["pc", "preview", "open_app"],
        metadata={"expected_action": "pc.open_app", "expected_risk": "low"},
    ),
    # B — Ambiguous device
    DemoScenario(
        scenario_id="ambiguous_light",
        title="Device: Ambiguous ışık komutu",
        description=(
            "'Işığı aç' komutu için ATLAS birden fazla cihaz adayı bulur "
            "ve kullanıcıdan hangi ışığı kastettiğini netleştirmesini ister."
        ),
        category=DemoCategory.DEVICE,
        input_text="Işığı aç",
        command_surface=CommandSurface.DEVICE,
        expected_response_type="clarification",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["device", "clarification", "ambiguous"],
        metadata={"expects_candidate_list": True},
    ),
    # C — Home device confirmation
    DemoScenario(
        scenario_id="home_salon_light",
        title="Home: Salon ışığını aç (confirmation required)",
        description=(
            "'Salon ışığını aç' komutu için ATLAS hedef cihazı çözümler, "
            "bir home preview planı oluşturur ve kullanıcı onayı ister."
            " Fiziksel cihaz state değişmez."
        ),
        category=DemoCategory.HOME_PREVIEW,
        input_text="Salon ışığını aç",
        command_surface=CommandSurface.HOME_PREVIEW,
        expected_response_type="confirmation_required|action_preview",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["home", "device", "light", "confirmation"],
        metadata={"expects_plan": True},
    ),
    # D — Blocked secret
    DemoScenario(
        scenario_id="blocked_secret",
        title="Safety: Şifre okuma engellendi",
        description=(
            "'Şifrelerimi oku' komutu credential/secret erişimi olarak tanınır "
            "ve ATLAS bunu engeller."
        ),
        category=DemoCategory.SAFETY,
        input_text="Şifrelerimi oku",
        command_surface=CommandSurface.CHAT,
        expected_response_type="blocked",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["blocked", "secret", "credential", "safety"],
        metadata={"expects_blocked": True},
    ),
    # E — Routine
    DemoScenario(
        scenario_id="routine_work_mode",
        title="Routine: Çalışma modunu başlat",
        description=(
            "ATLAS 'çalışma modu' rutinini önizler, risk özetini sunar "
            "ve gerçek action çalıştırmaz."
        ),
        category=DemoCategory.ROUTINE,
        input_text="Çalışma modunu başlat",
        command_surface=CommandSurface.ROUTINE,
        expected_response_type="confirmation_required|action_preview|answer",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["routine", "preview", "work_mode"],
        metadata={"expects_routine_result": True},
    ),
    # F — Voice mock
    DemoScenario(
        scenario_id="voice_home_preview",
        title="Voice: Mock transcript ile salon ışığını aç",
        description=(
            "Mock STT kullanarak sesli komut simüle edilir. "
            "Mikrofon gerçekten açılmaz, audio tutulmaz, wake word kullanılmaz."
        ),
        category=DemoCategory.VOICE,
        input_text="Salon ışığını aç",
        command_surface=CommandSurface.VOICE,
        expected_response_type="confirmation_required|action_preview",
        expected_safety_flags={
            **_SAFE_FLAGS,
            "microphone_used": False,
            "wake_word_used": False,
            "audio_retained": False,
        },
        tags=["voice", "mock", "home", "safety"],
        metadata={"voice_source": "mock_transcript"},
    ),
    # G — Personal memory (safe)
    DemoScenario(
        scenario_id="memory_preference_store",
        title="Memory: Chrome tercihini kaydet",
        description=(
            "Kullanıcı explicit olarak 'Chrome tarayıcısını sık kullanırım' tercihini hafızaya ekler. "
            "Hassas değil, policy izin verir."
        ),
        category=DemoCategory.MEMORY,
        input_text="Bunu hatırla: Chrome tarayıcısını sık kullanırım",
        command_surface=CommandSurface.MEMORY_PERSONAL,
        expected_response_type="answer",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["memory", "preference", "safe"],
        metadata={"expects_stored": True},
    ),
    # H — Sensitive memory blocked
    DemoScenario(
        scenario_id="memory_sensitive_blocked",
        title="Safety: Şifre hafızaya alma engellendi",
        description=(
            "'Şifremin 1234 olduğunu hatırla' komutu hassas bilgi politikası tarafından engellenir. "
            "Hafızaya kayıt yapılmaz."
        ),
        category=DemoCategory.SAFETY,
        input_text="Şifremin 1234 olduğunu hatırla",
        command_surface=CommandSurface.MEMORY_PERSONAL,
        expected_response_type="blocked",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["memory", "blocked", "password", "safety"],
        metadata={"expects_blocked": True},
    ),
    # I — Reminder draft
    DemoScenario(
        scenario_id="reminder_create",
        title="Reminder: 20 dakika sonra su iç",
        description=(
            "ATLAS bir reminder draft oluşturur ve onay bekler. "
            "Gerçek OS bildirimi ya da scheduler kurulmaz."
        ),
        category=DemoCategory.REMINDER,
        input_text="Bana 20 dakika sonra su içmeyi hatırlat",
        command_surface=CommandSurface.REMINDER,
        expected_response_type="confirmation_required|action_preview|answer",
        expected_safety_flags={**_SAFE_FLAGS, "os_notification_sent": False},
        tags=["reminder", "draft", "pending_confirmation"],
        metadata={"expects_reminder_draft": True},
    ),
    # J — Calendar draft
    DemoScenario(
        scenario_id="calendar_draft",
        title="Calendar: Yarın 10'a toplantı ekle",
        description=(
            "ATLAS bir takvim etkinliği taslağı oluşturur. "
            "Gerçek Google/Outlook Calendar API çağrısı yapılmaz."
        ),
        category=DemoCategory.CALENDAR,
        input_text="Yarın 10'a toplantı ekle",
        command_surface=CommandSurface.CALENDAR,
        expected_response_type="confirmation_required|action_preview|answer",
        expected_safety_flags={**_SAFE_FLAGS, "external_calendar_used": False},
        tags=["calendar", "draft", "event"],
        metadata={"expects_event_draft": True},
    ),
    # K — Calendar query
    DemoScenario(
        scenario_id="calendar_query",
        title="Calendar: Bugün takvimimde ne var?",
        description=(
            "ATLAS yerel takvim state'ini önizler. "
            "Herhangi bir harici takvim API'si kullanılmaz."
        ),
        category=DemoCategory.CALENDAR,
        input_text="Bugün takvimimde ne var?",
        command_surface=CommandSurface.CALENDAR,
        expected_response_type="action_preview|answer",
        expected_safety_flags={**_SAFE_FLAGS, "external_calendar_used": False},
        tags=["calendar", "query", "local"],
        metadata={"expects_query_preview": True},
    ),
    # L — Panel queue
    DemoScenario(
        scenario_id="panel_queue_light",
        title="Panel: Salon ışığı için panel öğesi oluştur",
        description=(
            "'Salon ışığını aç' isteği panel kuyruğuna eklenir. "
            "Approve işlemi execution başlatmaz."
        ),
        category=DemoCategory.PANEL,
        input_text="Salon ışığını aç",
        command_surface=CommandSurface.PANEL,
        expected_response_type="confirmation_required|action_preview|answer",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["panel", "queue", "submit"],
        metadata={"expects_panel_item": True},
    ),
    # M — Home preview (climate)
    DemoScenario(
        scenario_id="home_climate_preview",
        title="Home: Klimayı 24 derece yap",
        description=(
            "ATLAS bir iklim kontrol home preview planı oluşturur. "
            "Medium risk, onay gerekli. Home Assistant/MQTT kullanılmaz."
        ),
        category=DemoCategory.HOME_PREVIEW,
        input_text="Klimayı 24 derece yap",
        command_surface=CommandSurface.HOME_PREVIEW,
        expected_response_type="confirmation_required|action_preview",
        expected_safety_flags=_SAFE_FLAGS,
        tags=["home", "climate", "medium_risk"],
        metadata={"expects_plan": True, "expected_risk": "medium"},
    ),
    # N — Notification preview
    DemoScenario(
        scenario_id="notification_preview",
        title="Notification: Bildirim önizleme",
        description=(
            "ATLAS bir bildirim kopyasını önizler. "
            "Gerçek OS bildirimi gönderilmez."
        ),
        category=DemoCategory.MIXED,
        input_text="Su içme zamanı",
        command_surface=CommandSurface.CHAT,
        expected_response_type="action_preview|answer",
        expected_safety_flags={**_SAFE_FLAGS, "os_notification_sent": False},
        tags=["notification", "preview", "no_os"],
        metadata={
            "notification_title": "ATLAS Hatırlatıcı",
            "notification_body": "Su içme zamanı geldi.",
        },
    ),
]

_SCENARIO_MAP: dict[str, DemoScenario] = {s.scenario_id: s for s in BUILTIN_SCENARIOS}


def get_scenario(scenario_id: str) -> DemoScenario | None:
    return _SCENARIO_MAP.get(scenario_id)


def get_scenarios_by_category(category: DemoCategory) -> list[DemoScenario]:
    return [s for s in BUILTIN_SCENARIOS if s.category == category]
