import os
from datetime import datetime
from ..core.language_handler import LanguageHandler
from ..core.variable_handler import VariableHandler
from ..core.config_manager import ConfigManager
from .driver import get_driver

class FrameworkHooks:
    @staticmethod
    def bootstrap(context, lang_dir=None, default_lang="en", dataset_config=None):
        """
        Initializes core framework components (I18n, Variables, Config).
        Driver initialization is now deferred to before_scenario/before_feature
        depending on configuration.
        """
        # 1. Configuration
        config = ConfigManager.instance()
        context.config_obj = config # Store for later use
        
        # 2. Driver Config
        driver_config = {}
        # ConfigManager returns a dict for the section, or None/Empty dict
        driver_section = config.get('Driver')
        if driver_section:
            driver_config = {
                'reuse_driver': str(driver_section.get('reuse_driver', 'false')).lower() == 'true',
                'reuse_driver_session': str(driver_section.get('reuse_driver_session', 'false')).lower() == 'true',
                'restart_driver_after_failure': str(driver_section.get('restart_driver_after_failure', 'true')).lower() == 'true',
            }
        context.driver_config = driver_config

        # 3. I18n
        if lang_dir and os.path.exists(lang_dir):
            context.i18n = LanguageHandler(lang_dir, default_lang=default_lang)
        
        # 4. Variables
        if not dataset_config:
            dataset_config = {
                "dataset": {
                    "language": default_lang.split('_')[0],
                    "country": "US"
                }
            }
        context.variables = VariableHandler(config=dataset_config)
        
        # 5. Visual Testing Config
        visual_config = {}
        visual_section = config.get('VisualTests')
        if visual_section:
            for option, raw_value in visual_section.items():
                resolved_value = str(raw_value) 
                if resolved_value.lower() in ['true', 'false']:
                    visual_config[option] = resolved_value.lower() == 'true'
                else:
                    visual_config[option] = resolved_value
        
        # Override from Environment Variables
        if os.environ.get('VISUALTESTS_SAVE', '').lower() == 'true':
            visual_config['save'] = True
        if os.environ.get('VISUALTESTS_ENABLED', '').lower() == 'false':
            visual_config['enabled'] = False
            
        context.visual_config = visual_config
        
        # 6. Metadata
        context.screenshots = []
        context.run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    @staticmethod
    def before_scenario(context, scenario):
        """
        Handles driver initialization per scenario basis, respecting reuse settings.
        """
        driver_config = getattr(context, 'driver_config', {})
        
        # Determine if this is an API test (should skip driver init)
        tags = list(scenario.tags) + list(scenario.feature.tags)
        is_api = any(tag.lower() == 'api' for tag in tags)
        
        # Initialize context.dataset for all tests to prevent attribute errors
        if not hasattr(context, 'dataset'):
            context.dataset = {}

        if is_api:
            # We skip driver initialization for API tests
            return

        reuse_session = driver_config.get('reuse_driver_session', False)
        reuse_feature = driver_config.get('reuse_driver', False) or 'reuse_driver' in scenario.feature.tags
        
        force_reset = 'reset_driver' in scenario.tags
        
        should_init = False
        
        if not hasattr(context, 'driver') or context.driver is None:
            should_init = True
        elif force_reset:
            print(f"[FRAMEWORK] @reset_driver tag detected. Restarting browser for scenario: {scenario.name}")
            FrameworkHooks.teardown_driver(context)
            should_init = True
            
        if should_init:
            headless = os.getenv("HEADLESS", "true").lower() == "true"
            context.driver = get_driver(headless=headless)

        # Configure headless downloads for Chrome if using Selenium/Chrome
        # This ensures downloads work even in CI/Headless environments
        if hasattr(context, 'driver') and context.driver and context.driver.name == 'chrome':
             downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
             if not os.path.exists(downloads_dir):
                 os.makedirs(downloads_dir)
                 
             try:
                 context.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                     'behavior': 'allow',
                     'downloadPath': downloads_dir
                 })
             except Exception:
                 # Driver might not support CDP or is already configured
                 pass  # nosec B110

    @staticmethod
    def after_scenario(context, scenario, step_failure_dir=None):
        """
        Handles driver teardown or failure recovery.
        """
        driver_config = getattr(context, 'driver_config', {})
        reuse_session = driver_config.get('reuse_driver_session', False)
        reuse_feature = driver_config.get('reuse_driver', False) or 'reuse_driver' in scenario.feature.tags
        restart_on_failure = driver_config.get('restart_driver_after_failure', True)
        
        failed = scenario.status == "failed"
        
        # Capture screenshots on failure if dir provided
        if failed and step_failure_dir:
            # Note: Step failures are usually handled in after_step, 
            # but we can do a final sanity check here.
            pass

        # Decide if we should close the driver now
        # If we failed and restart_on_failure is true, we always close it to ensure fresh start
        if failed and restart_on_failure:
            print(f"[FRAMEWORK] Scenario failed. Restarting driver for next test.")
            FrameworkHooks.teardown_driver(context)
        elif not reuse_session and not reuse_feature:
            # Case: Standard isolation (per scenario)
            FrameworkHooks.teardown_driver(context)

    @staticmethod
    def after_feature(context, feature):
        """Standard teardown after feature completion."""
        driver_config = getattr(context, 'driver_config', {})
        reuse_session = driver_config.get('reuse_driver_session', False)
        reuse_feature = driver_config.get('reuse_driver', False) or 'reuse_driver' in feature.tags

        if reuse_feature and not reuse_session:
            FrameworkHooks.teardown_driver(context)

    @staticmethod
    def teardown_driver(context):
        """Safely shuts down the driver instance."""
        if hasattr(context, "driver") and context.driver:
            try:
                context.driver.quit()
            except Exception as e:
                print(f"[FRAMEWORK] Error during driver quit: {e}")
            finally:
                context.driver = None

    @staticmethod
    def handle_step_failure(context, step, screenshots_base_dir):
        """
        Common logic to capture failure screenshots.
        """
        if step.status == "failed" and hasattr(context, 'driver') and context.driver:
            failure_dir = os.path.join(screenshots_base_dir, context.run_timestamp)
            if not os.path.exists(failure_dir):
                os.makedirs(failure_dir)
            
            scenario_name = context.scenario.name.replace(" ", "_").replace("/", "_")
            step_name = step.name.replace(" ", "_").replace("/", "_")[:30]
            
            filename = f"FAILED_{scenario_name}_{step_name}.png"
            filepath = os.path.join(failure_dir, filename)
            
            try:
                context.driver.save_screenshot(filepath)
                if hasattr(context, 'embed'):
                    import base64
                    with open(filepath, 'rb') as img:
                        data = base64.b64encode(img.read()).decode('utf-8')
                    context.embed('image/png', data, caption=f"Failure: {step.name}")
                
                abspath = os.path.abspath(filepath).replace('\\', '/')
                print(f"[FAILURE] Screenshot: file:///{abspath}")
                context.screenshots.append(filepath)
            except Exception as e:
                print(f"Error capturing failure screenshot: {e}")

    @staticmethod
    def teardown(context):
        """Final project-level teardown."""
        FrameworkHooks.teardown_driver(context)
        if hasattr(context, 'screenshots') and context.screenshots:
             print(f"\n[FRAMEWORK] Screenshots captured: {len(context.screenshots)}")
