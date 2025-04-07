"""Get today's date."""

from datetime import datetime

import pytz
from langchain.tools import tool


@tool
def get_todays_date(timezone: str = "UTC") -> str:
    """Return today's date in YYYY-MM-DD format based on the specified timezone.

    Use this tool when you need today's date.

    Args:
        timezone (str): Timezone name (default is "UTC").

    Returns:
        str: Today's date as a string.

    """
    tz = pytz.timezone(timezone)
    today = datetime.now(tz).date()
    return today.isoformat()
