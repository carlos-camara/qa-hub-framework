"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                          CLI Unit Tests                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for the qa-hub CLI including:                                         ║
║  • Argument parsing and validation                                           ║
║  • Behave command string generation                                          ║
║  • Error handling and exit codes                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from qa_framework.cli import main

@pytest.fixture
def mock_popen():
    with patch("subprocess.Popen") as mock:
        process = MagicMock()
        process.returncode = 0
        mock.return_value = process
        yield mock

def test_cli_help(capsys):
    """✓ --help should display usage information."""
    with patch.object(sys, 'argv', ['qa-hub', '--help']):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
        captured = capsys.readouterr()
        assert "QA Hub Framework CLI" in captured.out
        assert "run" in captured.out

def test_run_basic_command(mock_popen):
    """✓ Basic 'run' command generates correct behave call."""
    with patch.object(sys, 'argv', ['qa-hub', 'run']):
        main()
        
        args, _ = mock_popen.call_args
        cmd = args[0]
        assert "behave" in cmd
        assert "features" in cmd
        assert "-D env=local" in " ".join(cmd)

def test_run_with_env_and_tags(mock_popen):
    """✓ 'run' with --env and --tags generates correct behave call."""
    with patch.object(sys, 'argv', ['qa-hub', 'run', '--env', 'staging', '--tags', 'smoke']):
        main()
        
        args, _ = mock_popen.call_args
        cmd = " ".join(args[0])
        assert "--tags smoke" in cmd
        assert "-D env=staging" in cmd

def test_run_with_browser(mock_popen):
    """✓ 'run' with --browser passes browser variable to behave."""
    with patch.object(sys, 'argv', ['qa-hub', 'run', '--browser', 'firefox']):
        main()
        
        args, _ = mock_popen.call_args
        cmd = " ".join(args[0])
        assert "-D browser=firefox" in cmd

def test_run_with_flags(mock_popen):
    """✓ 'run' with --fail and --no-capture translates to behave flags."""
    with patch.object(sys, 'argv', ['qa-hub', 'run', '--fail', '--no-capture']):
        main()
        
        args, _ = mock_popen.call_args
        cmd = " ".join(args[0])
        assert "--stop" in cmd
        assert "--no-capture" in cmd

@patch("sys.exit")
def test_run_failure_exit_code(mock_exit, mock_popen):
    """✓ CLI should exit with non-zero code if behave fails."""
    mock_popen.return_value.returncode = 1
    
    with patch.object(sys, 'argv', ['qa-hub', 'run']):
        main()
        mock_exit.assert_called_with(1)

def test_invalid_command(capsys):
    """✓ Invalid command should exit with code 2."""
    with patch.object(sys, 'argv', ['qa-hub', 'invalid']):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
