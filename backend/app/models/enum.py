import enum

class ChangeType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"


class EventCategory(str, enum.Enum):
    MUSIC = "music"
    SPORTS = "sports"
    CONFERENCE = "conference"
    THEATER = "theater"
    OTHER = "other"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
class NotificationType(str, enum.Enum):
    EVENT_REMINDER = "event_reminder"
    EVENT_UPDATE = "event_update"
    EVENT_CANCELLED = "event_cancelled"
    TICKET_CONFIRMATION = "ticket_confirmation"
    REVIEW_REPLY = "review_reply"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"

