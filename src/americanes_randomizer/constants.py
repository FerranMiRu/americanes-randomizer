import enum


class Levels(enum.Enum):
    """Enum for the levels of the players"""

    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D = "D"


class SearchLevelOptions(enum.Enum):
    """Extended Enum for the levels of the players plus All"""

    ALL = "All"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D = "D"


class PaginationOptions(enum.Enum):
    """Enum for the possible options in pagination"""

    FIRST = "first"
    PREVIOUS = "previous"
    NEXT = "next"
    LAST = "last"
    SAME = "same"


class ListPurposes(enum.Enum):
    """Enum for the purposes of the list"""

    DATABASE = "database"
    SELECTED = "selected"


class ButtonEmojis(enum.Enum):
    """Enum for the emojis used in the buttons"""

    FIRST = "⏮️"
    PREVIOUS = "⬅️"
    NEXT = "➡️"
    LAST = "⏭️"
    REFRESH = "🔄"
    DELETE = "🗑️"
    ADD = "➕"
    EDIT = "✏️"
    SEARCH = "🔍"
    QUESTION = "❓"
    INFO = "ℹ️"
    WARNING = "⚠️"
    CONFIRM = "✅"
    CANCEL = "❌"
    YES = "✅"
    NO = "❌"
    CLOSE = "🔒"
    OPEN = "🔓"
    SUCCESS = "✅"
    ERROR = "❌"
