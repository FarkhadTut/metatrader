
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

def minutes_between_datetimes(start_datetime, end_datetime):
    # Calculate the difference between the datetimes
    time_difference = end_datetime - start_datetime
    
    # Convert the difference to minutes
    minutes = time_difference.total_seconds() / 60
    
    return int(minutes)


def generate_time_list(start_datetime, end_datetime):
    """
    Generates a list of datetime objects with 4-hour intervals, excluding weekends.

    Args:
        start_datetime: The starting datetime object.
        end_datetime: The ending datetime object.

    Returns:
        A list of datetime objects within the specified range, excluding weekends.
    """
    start_datetime = pd.to_datetime(start_datetime)
    end_datetime = pd.to_datetime(end_datetime)
    time_list = []
    current_time = start_datetime
    while current_time <= end_datetime:
        if current_time.dayofweek not in (5, 6):  # Skip Saturdays and Sundays (weekend days)
            time_list.append(current_time)
        current_time += relativedelta(hours=4)
    return time_list