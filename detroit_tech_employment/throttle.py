import datetime
from time import sleep


def throttle(min_return_seconds): # in seconds
    """
    This decorator forces the function that it wraps to wait until a minimum
    running time is reached before returning.
    """
    def inner_throttle(function):
        def wrapped(*args, **kwargs):
            # What time is it now?
            then = datetime.datetime.now()
            # Run the function right away
            result = function(*args, **kwargs)
            # How long did that take?
            running_time = datetime.datetime.now() - then

            # If the minimum time hasnt' been reached, sleep for the remainder.
            sleep(max(0, min_return_seconds - running_time.total_seconds()))

            return result
        return wrapped
    return inner_throttle

