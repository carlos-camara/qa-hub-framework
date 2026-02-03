from behave import step
import time

@step('I wait for {seconds:d} seconds')
def step_wait_seconds(context, seconds):
    """
    Explicit wait. Use sparingly; prefer specialized waits in Page Objects.
    """
    time.sleep(seconds)
