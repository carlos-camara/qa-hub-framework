"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Common Step Definitions                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Utility steps that apply across multiple testing domains (GUI, API, etc.).   ║
║                                                                              ║
║  Features:                                                                    ║
║  • Explicit timing control                                                   ║
║  • Dynamic variable storage from UI text                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from behave import step
import time
from qa_framework.utils.logger import ContextualLogger

@step('I wait for {seconds:f} seconds')
@step('I wait for {seconds:d} second')
@step('I wait for {seconds:d} seconds')
def step_wait_seconds(context, seconds):
    """
    Explicit wait. Use sparingly; prefer specialized waits in Page Objects.
    """
    ContextualLogger.warning(f"Explicit wait for {seconds} seconds. Prefer using wait_until_* on elements.", context)
    time.sleep(float(seconds))


@step('I wait for "{name}" to be stable')
@step('I wait for "{name}" to update')
@step('I wait for "{name}" to be ready')
def step_wait_for_stability(context, name):
    """
    Generic placeholder for stability waits (animations, loading states).
    Standardizes 'I wait for "dashboard" to be stable' across projects.
    """
    ContextualLogger.debug(f"Waiting for '{name}' stability (1s wait)...", context)
    time.sleep(1)


@step('I store the text of the "{element_name}" as "{var_name}"')
def step_store_element_text(context, element_name, var_name):
    """
    Extract text content from a UI element and store it in context.vars.
    
    Example:
        When I store the text of the "order_number" as "StoredOrderID"
        And I navigate to "/search?id=${StoredOrderID}"
    """
    from .gui_steps import get_element_from_page_object
    page_name = getattr(context, 'current_page', None)
    element = get_element_from_page_object(context, element_name, page_name)
    text = element.get_text()
    
    if not hasattr(context, 'vars') or context.vars is None:
        context.vars = {}
    context.vars[var_name] = text
    ContextualLogger.debug(f"Stored UI text from '{element_name}' as '${{{var_name}}}': {text}", context)
