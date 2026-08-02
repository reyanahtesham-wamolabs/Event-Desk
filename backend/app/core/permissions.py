from enum import Enum
from app.models.user import UserRole

class Permission(str, Enum):
    """Permissions available in the system."""

    UPDATE_OWN_PROFILE = "update_own_profile"
    VIEW_ALL_USERS = "view_all_users"
    CHANGE_USER_ROLE = "change_user_role"
    TOGGLE_USER_ACTIVATION = "toggle_user_activation"

    CREATE_EVENT = "create_event"
    EDIT_EVENT = "edit_event"
    CANCEL_EVENT = "cancel_event"
    VIEW_PUBLISHED_EVENTS = "view_published_events"
    DELETE_EVENT="delete_event"

    CREATE_TAG="create_tag"
    EDIT_TAG="edit_tag"
    DELETE_TAG="delete_tag"

    BOOK_TICKET = "book_ticket"
    CANCEL_BOOKING = "cancel_booking"

    LEAVE_REVIEW = "leave_review"
    REPLY_TO_REVIEW = "reply_to_review"
    EDIT_OWN_REVIEW = "edit_own_review"
    EDIT_ANY_REVIEW = "edit_any_review"

    VIEW_OWN_NOTIFICATIONS = "view_own_notifications"
    VIEW_AUDIT_LOGS = "view_audit_logs"



ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: set(Permission),
    UserRole.ORGANIZER: {
        Permission.UPDATE_OWN_PROFILE,
        Permission.CREATE_EVENT,#only own
        Permission.EDIT_EVENT,#only own
        Permission.CANCEL_EVENT,#only own
        Permission.VIEW_PUBLISHED_EVENTS,
        Permission.BOOK_TICKET,
        Permission.CANCEL_BOOKING,#only own
        Permission.REPLY_TO_REVIEW,#only own
        Permission.EDIT_OWN_REVIEW,
        Permission.VIEW_OWN_NOTIFICATIONS,
        Permission.EDIT_TAG,#only own
        Permission.CREATE_TAG,                        
    },
    UserRole.ATTENDEE: {
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_PUBLISHED_EVENTS,
        Permission.BOOK_TICKET,
        Permission.CANCEL_BOOKING,#only own
        Permission.LEAVE_REVIEW,
        Permission.EDIT_OWN_REVIEW,
        Permission.VIEW_OWN_NOTIFICATIONS,
    },
}
