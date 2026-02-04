"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Contextual Logger Utility                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  A professional logging utility that provides:                                ║
║  • Automatic context extraction (Feature/Scenario names)                      ║
║  • Standardized console colors for different log levels                       ║
║  • High-fidelity timestamps for audit trails                                  ║
║  • Clean formatting for CI/CD environments                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import datetime
import sys
from typing import Any, Optional

# ANSI Color Codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'

class ContextualLogger:
    """
    Utility class for contextual logging in the QA Hub Framework.
    
    This logger automatically extracts the current Feature and Scenario names
    from the Behave context object to provide rich audit logs.
    """
    
    @staticmethod
    def _get_timestamp() -> str:
        """Returns the current timestamp in HH:MM:SS format."""
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def _get_context_info(context: Optional[Any]) -> str:
        """
        Extracts Feature and Scenario names from the Behave context.
        
        Returns:
            Formatted string "[Feature | Scenario]" or empty string if context is missing.
        """
        if not context:
            return ""
            
        feature = "Global"
        scenario = "Setup"
        
        if hasattr(context, 'feature') and context.feature:
            feature = context.feature.name
        if hasattr(context, 'scenario') and context.scenario:
            scenario = context.scenario.name
            
        return f"{Colors.GRAY}[{feature} | {scenario}]{Colors.END} "

    @staticmethod
    def info(message: str, context: Optional[Any] = None):
        """Log an informational message in Blue."""
        timestamp = f"{Colors.GRAY}{ContextualLogger._get_timestamp()}{Colors.END}"
        ctx = ContextualLogger._get_context_info(context)
        print(f"{timestamp} {ctx}{Colors.BLUE}INFO:{Colors.END} {message}")

    @staticmethod
    def success(message: str, context: Optional[Any] = None):
        """Log a success message in Green."""
        timestamp = f"{Colors.GRAY}{ContextualLogger._get_timestamp()}{Colors.END}"
        ctx = ContextualLogger._get_context_info(context)
        print(f"{timestamp} {ctx}{Colors.GREEN}SUCCESS:{Colors.END} {message}")

    @staticmethod
    def warning(message: str, context: Optional[Any] = None):
        """Log a warning message in Yellow."""
        timestamp = f"{Colors.GRAY}{ContextualLogger._get_timestamp()}{Colors.END}"
        ctx = ContextualLogger._get_context_info(context)
        print(f"{timestamp} {ctx}{Colors.YELLOW}WARNING:{Colors.END} {message}")

    @staticmethod
    def error(message: str, context: Optional[Any] = None):
        """Log an error message in Red."""
        timestamp = f"{Colors.GRAY}{ContextualLogger._get_timestamp()}{Colors.END}"
        ctx = ContextualLogger._get_context_info(context)
        print(f"{timestamp} {ctx}{Colors.RED}{Colors.BOLD}ERROR:{Colors.END} {message}", file=sys.stderr)

    @staticmethod
    def debug(message: str, context: Optional[Any] = None):
        """Log a debug message in Gray."""
        timestamp = f"{Colors.GRAY}{ContextualLogger._get_timestamp()}{Colors.END}"
        ctx = ContextualLogger._get_context_info(context)
        print(f"{timestamp} {ctx}{Colors.GRAY}DEBUG: {message}{Colors.END}")

    @staticmethod
    def section(title: str):
        """Log a section header to visually separate log blocks."""
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}{title.upper()}{Colors.END}")
