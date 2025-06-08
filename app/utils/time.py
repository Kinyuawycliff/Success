# app/utils/time.py

#? NOTE: The below function is a simplified version that only handles single units (e.g., '1h', '30m', '120s').

# def convert_session_time_to_seconds(session_time_str: str) -> int:
#     """Converts session time string (e.g., '1h', '30m', '120s') to seconds."""
#     try:
#         time_value = int(session_time_str[:-1])
#         time_unit = session_time_str[-1].lower()

#         if time_unit == 'h':
#             return time_value * 3600
#         elif time_unit == 'm':
#             return time_value * 60
#         elif time_unit == 's':
#             return time_value
#         else:
#             raise ValueError("Invalid time unit. Use 'h', 'm', or 's'.")
#     except (ValueError, IndexError) as e:
#         raise ValueError(f"Invalid session time format: {session_time_str}. Error: {e}")



#? NOTE: This function supports **combined time formats** such as '1h30m', '2d4h', '1y2mo3d10m45s', etc.
# It parses multiple time units in a single string and converts the total duration to seconds.
# Supported units:
#   - 's'  : seconds
#   - 'm'  : minutes
#   - 'h'  : hours
#   - 'd'  : days
#   - 'mo' : months (assumed as 30 days)
#   - 'y'  : years  (assumed as 365 days)
# Example:
#   '1h30m'     => 5400 seconds
#   '2d4h20m'   => 190800 seconds
#   '1y2mo3d'   => 38880000 seconds


import re

def convert_session_time_to_seconds(session_time_str: str) -> int:
    """
    Converts a combined session time string to total seconds.
    Supports: s (seconds), m (minutes), h (hours), d (days), mo (months), y (years)
    Example inputs: '1h30m', '2d4h20m', '1y2mo3d', '10m45s'
    """
    session_time_str = session_time_str.strip().lower()

    # Time multipliers in seconds
    time_multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'mo': 2592000,     # 30 days
        'y': 31536000      # 365 days
    }

    # Regex to find all number + unit groups (like 2h, 30m, 1mo)
    pattern = r'(\d+)(y|mo|d|h|m|s)'
    matches = re.findall(pattern, session_time_str)

    if not matches:
        raise ValueError(f"Invalid session time format: {session_time_str}")

    total_seconds = 0
    for value, unit in matches:
        if unit not in time_multipliers:
            raise ValueError(f"Unsupported time unit: {unit}")
        total_seconds += int(value) * time_multipliers[unit]

    return total_seconds
