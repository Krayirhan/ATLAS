from __future__ import annotations

import re
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.personal_assistant.models import CalendarOperation, ReminderOperation


WEEKDAY_ORDER = {
    "pazartesi": 0,
    "sali": 1,
    "carsamba": 2,
    "persembe": 3,
    "cuma": 4,
    "cumartesi": 5,
    "pazar": 6,
}

DAY_TOKEN_PATTERN = r"(?:bugun|yarin|aksam|sabah|ogle|gece|pazartesi|sali|carsamba|persembe|cuma|cumartesi|pazar)"
TIME_PATTERN = r"\d{1,2}(?::\d{2})?"
TIME_SUFFIX_PATTERN = r"(?:\s*(?:da|de|a|e))?"
RELATIVE_TIME_PATTERN = r"\d+\s+(?:dakika|saat)\s+sonra"
ABSOLUTE_TIME_PATTERN = rf"{DAY_TOKEN_PATTERN}(?:\s+{TIME_PATTERN}{TIME_SUFFIX_PATTERN})?"


def normalize_text(text: str) -> str:
    normalized = text.strip().lower()
    normalized = normalized.replace("â€™", "'").replace("`", "'")
    normalized = normalized.translate(
        str.maketrans(
            {
                "ç": "c",
                "ğ": "g",
                "ı": "i",
                "ö": "o",
                "ş": "s",
                "ü": "u",
            }
        )
    )
    normalized = re.sub(r"['\"]", "", normalized)
    normalized = re.sub(r"[!?.,;()]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_reminder_request(text: str) -> tuple[ReminderOperation, dict[str, object]]:
    normalized = normalize_text(text)

    if any(token in normalized for token in ("hatirlaticilarimi goster", "neleri hatirlatacaksin", "reminder listesi")):
        return ReminderOperation.LIST, {}

    if "son hatirlaticiyi iptal et" in normalized or "son hatirlaticiyi sil" in normalized:
        return ReminderOperation.CANCEL, {"identifier": "last"}

    cancel_match = re.search(r"(?P<identifier>.+?)\s+hatirlaticisini\s+iptal\s+et", normalized)
    if cancel_match:
        return ReminderOperation.CANCEL, {"identifier": cancel_match.group("identifier").strip()}

    if "hatirlaticiyi sil" in normalized or "hatirlaticiyi iptal et" in normalized:
        return ReminderOperation.CANCEL, {"identifier": "last"}

    create_match = re.search(r"bana\s+(?P<body>.+?)\s+hatirlat", normalized)
    if create_match:
        due_at_text, reminder_text = _split_time_and_message(create_match.group("body").strip())
        return ReminderOperation.CREATE, {
            "due_at_text": due_at_text,
            "reminder_text": reminder_text or create_match.group("body").strip(),
        }

    absolute_match = re.search(
        rf"(?P<when>{RELATIVE_TIME_PATTERN}|{ABSOLUTE_TIME_PATTERN})\s+(?P<what>.+?)\s+hatirlat",
        normalized,
    )
    if absolute_match:
        return ReminderOperation.CREATE, {
            "due_at_text": absolute_match.group("when").strip(),
            "reminder_text": absolute_match.group("what").strip(),
        }

    return ReminderOperation.UNKNOWN, {}


def parse_calendar_request(text: str) -> tuple[CalendarOperation, dict[str, object]]:
    normalized = normalize_text(text)

    if any(token in normalized for token in ("taslak takvimi goster", "takvim taslaklarini goster", "takvim draftlarini goster")):
        return CalendarOperation.LIST_LOCAL, {}

    if "son takvim taslagini iptal et" in normalized:
        return CalendarOperation.CANCEL_DRAFT, {"identifier": "last"}

    cancel_match = re.search(r"(?P<identifier>.+?)\s+takvim\s+taslagini\s+iptal\s+et", normalized)
    if cancel_match:
        return CalendarOperation.CANCEL_DRAFT, {"identifier": cancel_match.group("identifier").strip()}

    if any(token in normalized for token in ("takvimimde ne var", "toplantim var mi", "takvimim nasil")):
        date_text = _extract_query_date_text(normalized)
        return CalendarOperation.QUERY, {"date_text": date_text}

    draft_match = re.search(
        rf"(?P<when>{ABSOLUTE_TIME_PATTERN})\s+(?P<title>.+?)\s+(?:ekle|koy)",
        normalized,
    )
    if draft_match:
        return CalendarOperation.DRAFT_EVENT, {
            "start_text": draft_match.group("when").strip(),
            "title": draft_match.group("title").strip(),
        }

    return CalendarOperation.UNKNOWN, {}


def parse_datetime_text(date_text: str, timezone_name: str = "Europe/Istanbul", now: datetime | None = None) -> datetime | None:
    if not date_text:
        return None

    tzinfo = _tzinfo(timezone_name)
    current = now.astimezone(tzinfo) if now is not None else datetime.now(tzinfo)
    normalized = normalize_text(date_text)

    relative_match = re.fullmatch(r"(?P<amount>\d+)\s+(?P<unit>dakika|saat)\s+sonra", normalized)
    if relative_match:
        amount = int(relative_match.group("amount"))
        delta = timedelta(minutes=amount) if relative_match.group("unit") == "dakika" else timedelta(hours=amount)
        return current + delta

    explicit_time = _extract_time(normalized)
    if normalized.startswith("bugun"):
        return _combine_date_and_time(current.date(), explicit_time or time(9, 0), current, tzinfo)
    if normalized.startswith("yarin"):
        return _combine_date_and_time(current.date() + timedelta(days=1), explicit_time or time(9, 0), current, tzinfo)
    if normalized.startswith("aksam"):
        return _combine_with_rollover(current.date(), explicit_time or time(20, 0), current, tzinfo)
    if normalized.startswith("sabah"):
        return _combine_with_rollover(current.date(), explicit_time or time(9, 0), current, tzinfo)
    if normalized.startswith("ogle"):
        return _combine_with_rollover(current.date(), explicit_time or time(13, 0), current, tzinfo)
    if normalized.startswith("gece"):
        return _combine_with_rollover(current.date(), explicit_time or time(22, 0), current, tzinfo)

    for token, weekday in WEEKDAY_ORDER.items():
        if normalized.startswith(token):
            base_date = current.date() + timedelta(days=(weekday - current.weekday()) % 7)
            candidate = _combine_date_and_time(base_date, explicit_time or time(9, 0), current, tzinfo)
            if candidate <= current:
                candidate = candidate + timedelta(days=7)
            return candidate

    return None


def parse_calendar_range(date_text: str, timezone_name: str = "Europe/Istanbul", now: datetime | None = None) -> tuple[datetime | None, datetime | None]:
    tzinfo = _tzinfo(timezone_name)
    current = now.astimezone(tzinfo) if now is not None else datetime.now(tzinfo)
    normalized = normalize_text(date_text)

    if normalized == "bugun":
        start = datetime.combine(current.date(), time.min, tzinfo=tzinfo)
        end = datetime.combine(current.date(), time.max, tzinfo=tzinfo)
        return start, end
    if normalized == "yarin":
        day = current.date() + timedelta(days=1)
        start = datetime.combine(day, time.min, tzinfo=tzinfo)
        end = datetime.combine(day, time.max, tzinfo=tzinfo)
        return start, end
    if normalized == "bu hafta":
        week_start = current.date() - timedelta(days=current.weekday())
        week_end = week_start + timedelta(days=6)
        start = datetime.combine(week_start, time.min, tzinfo=tzinfo)
        end = datetime.combine(week_end, time.max, tzinfo=tzinfo)
        return start, end
    parsed = parse_datetime_text(date_text, timezone_name=timezone_name, now=current)
    if parsed is None:
        return None, None
    return parsed, parsed


def _split_time_and_message(text: str) -> tuple[str, str]:
    relative_match = re.match(rf"(?P<when>{RELATIVE_TIME_PATTERN})\s+(?P<what>.+)", text)
    if relative_match:
        return relative_match.group("when").strip(), relative_match.group("what").strip()

    absolute_match = re.match(rf"(?P<when>{ABSOLUTE_TIME_PATTERN})\s+(?P<what>.+)", text)
    if absolute_match:
        return absolute_match.group("when").strip(), absolute_match.group("what").strip()

    return "", text.strip()


def _extract_query_date_text(normalized: str) -> str:
    if "bu hafta" in normalized:
        return "bu hafta"
    if "yarin" in normalized:
        return "yarin"
    if "bugun" in normalized:
        return "bugun"
    return "bugun"


def _extract_time(text: str) -> time | None:
    match = re.search(r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?", text)
    if match is None:
        return None
    hour = max(0, min(23, int(match.group("hour"))))
    minute = max(0, min(59, int(match.group("minute") or "0")))
    return time(hour=hour, minute=minute)


def _combine_date_and_time(day, value: time, current: datetime, tzinfo) -> datetime:
    candidate = datetime.combine(day, value, tzinfo=tzinfo)
    if day == current.date() and candidate <= current:
        return candidate + timedelta(days=1)
    return candidate


def _combine_with_rollover(day, value: time, current: datetime, tzinfo) -> datetime:
    candidate = datetime.combine(day, value, tzinfo=tzinfo)
    if candidate <= current:
        return candidate + timedelta(days=1)
    return candidate


def _tzinfo(timezone_name: str):
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return timezone.utc
