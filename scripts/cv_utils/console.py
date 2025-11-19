"""Console output utilities for CV scripts."""

import sys

# Configure stdout to use UTF-8 encoding on Windows to support Unicode symbols
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 fallback
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'


def print_status(message: str, status: str = 'info') -> None:
    """
    Print colored status messages.

    Args:
        message: Message to print
        status: Status type ('success', 'error', 'warning', 'info')
    """
    if status == 'success':
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    elif status == 'error':
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    elif status == 'info':
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")
    else:
        print(message)
