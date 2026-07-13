"""Conversation state constants shared across handlers."""
from __future__ import annotations

# Status / search flow
SEARCH_NAME = 0
# Results are shown and we now expect a button tap (not typed input).
SHOW_RESULTS = 7

# Registration form flow
REG_FIRST_NAME = 1
REG_FATHER_NAME = 2
REG_PHONE = 3
REG_AGE = 4
REG_EDUCATION = 5
REG_WAITING_FAMILY = 6

# Keys used within context.user_data
# Set when the conversation has ended; any further input shows the main menu.
UD_IDLE = "idle"
UD_RECORDS = "records"
UD_QUERY = "search_query"
UD_FIRST_NAME = "first_name"
UD_FATHER_NAME = "father_name"
UD_PHONE = "phone"
UD_AGE = "age"
UD_EDUCATION = "education"
