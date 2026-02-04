import os
from datetime import datetime
from ..core.language_handler import LanguageHandler
from ..core.variable_handler import VariableHandler
from .driver import get_driver

class FrameworkHooks:
    @staticmethod
    def bootstrap(context, lang_dir=None, default_lang="en", dataset_config=None):
        """
        Initializes the core framework components (Driver, I18n, Variables).
        """
        # 1. Driver
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        context.driver = get_driver(headless=headless)
        
        # 2. I18n
        if lang_dir and os.path.exists(lang_dir):
            context.i18n = LanguageHandler(lang_dir, default_lang=default_lang)
        
        # 3. Variables
        if not dataset_config:
            dataset_config = {
                "dataset": {
                    "language": default_lang.split('_')[0],
                    "country": "US"
                }
            }
        context.variables = VariableHandler(config=dataset_config)
        
        # 4. Screenshot metadata
        context.screenshots = []
        context.run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
    @staticmethod
    def handle_step_failure(context, step, screenshots_base_dir):
        """
        Common logic to capture failure screenshots.
        """
        if step.status == "failed" and hasattr(context, 'driver'):
            # Create timestamped failure dir if it doesn't exist
            failure_dir = os.path.join(screenshots_base_dir, context.run_timestamp)
            if not os.path.exists(failure_dir):
                os.makedirs(failure_dir)
            
            # Clean names for filesystem
            scenario_name = context.scenario.name.replace(" ", "_").replace("/", "_")
            step_name = step.name.replace(" ", "_").replace("/", "_")[:30]
            
            filename = f"FAILED_{scenario_name}_{step_name}.png"
            filepath = os.path.join(failure_dir, filename)
            
            try:
                context.driver.save_screenshot(filepath)
                
                # Support Behave's embedding if available
                if hasattr(context, 'embed'):
                    import base64
                    with open(filepath, 'rb') as img:
                        data = base64.b64encode(img.read()).decode('utf-8')
                    context.embed('image/png', data, caption=f"Failure: {step.name}")
                
                # Log to stdout for HTML formatters or consoles
                abspath = os.path.abspath(filepath)
                print(f"\n[FAILURE] Screenshot: file:///{abspath.replace('\\', '/')}")
                
                context.screenshots.append(filepath)
            except Exception as e:
                print(f"Error capturing failure screenshot: {e}")

    @staticmethod
    def teardown(context):
        """Standard teardown logic"""
        if hasattr(context, "driver") and context.driver:
            context.driver.quit()
        
        if hasattr(context, 'screenshots') and context.screenshots:
             print(f"\n[FRAMEWORK] Screenshots captured: {len(context.screenshots)}")
