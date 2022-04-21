import arrow

def date_time_format(date_string):
    """Format datetime from boto to be human-readable."""
    dt = arrow.get(date_string)
    return dt.humanize()