"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Command Line Interface                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  The central entry point for executing tests.                               ║
║                                                                              ║
║  Features:                                                                    ║
║  • Simplified test execution command: qa-hub run                             ║
║  • Environment selection: --env                                              ║
║  • Tag filtering: --tags                                                     ║
║  • Browser selection: --browser                                              ║
║  • Automated report generation logic                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import argparse
import subprocess
import sys
import os
from .utils.logger import ContextualLogger, Colors

def main():
    """Main entry point for the qa-hub CLI."""
    parser = argparse.ArgumentParser(
        description=f"{Colors.BLUE}QA Hub Framework CLI{Colors.END}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Execute the test suite")
    run_parser.add_argument("--env", help="Target environment (e.g., staging, prod)", default="local")
    run_parser.add_argument("--tags", help="Filter scenarios by tags (e.g., smoke, slow)", default=None)
    run_parser.add_argument("--browser", help="Browser to use (chrome, firefox, playwright)", default=None)
    run_parser.add_argument("--fail", action="store_true", help="Stop execution on first failure")
    run_parser.add_argument("--no-capture", action="store_true", help="Don't capture stdout (show prints in real-time)")
    run_parser.add_argument("--path", help="Path to feature files", default="features")
    
    args = parser.parse_args()
    
    if args.command == "run":
        execute_run(args)
    else:
        parser.print_help()

def execute_run(args):
    """Translates CLI arguments into a Behave command and executes it."""
    ContextualLogger.section("QA Hub: Initializing Test Execution")
    
    # Start building the command
    cmd = [sys.executable, "-m", "behave"]
    
    # 1. Path
    cmd.append(args.path)
    
    # 2. Tags
    if args.tags:
        cmd.extend(["--tags", args.tags])
    
    # 3. Fast failure
    if args.fail:
        cmd.append("--stop")
        
    # 4. Output capture
    if args.no_capture:
        cmd.append("--no-capture")
    
    # 5. Define variables (Environment, Browser)
    # We pass these as user-defined variables using -D
    cmd.extend(["-D", f"env={args.env}"])
    
    if args.browser:
        cmd.extend(["-D", f"browser={args.browser}"])
        
    # Log the command being executed
    ContextualLogger.info(f"Environment: {Colors.BOLD}{args.env}{Colors.END}")
    if args.tags:
        ContextualLogger.info(f"Filtering by tags: {Colors.BOLD}{args.tags}{Colors.END}")
    if args.browser:
        ContextualLogger.info(f"Target browser: {Colors.BOLD}{args.browser}{Colors.END}")
        
    ContextualLogger.debug(f"Executing: {' '.join(cmd)}")
    
    # Run the process
    try:
        # We use a subprocess and pipe the output so it shows up in real-time
        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            universal_newlines=True
        )
        process.wait()
        
        if process.returncode == 0:
            ContextualLogger.success("Test execution completed successfully!")
        else:
            ContextualLogger.error(f"Test execution failed with exit code: {process.returncode}")
            sys.exit(process.returncode)
            
    except KeyboardInterrupt:
        ContextualLogger.warning("Execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        ContextualLogger.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
