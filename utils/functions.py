
from datetime import datetime

def minutes_between_datetimes(start_datetime, end_datetime):
    # Calculate the difference between the datetimes
    time_difference = end_datetime - start_datetime
    
    # Convert the difference to minutes
    minutes = time_difference.total_seconds() / 60
    
    return int(minutes)