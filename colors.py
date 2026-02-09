"""ANSI color codes for terminal text formatting.

Provides color and style utilities for enhanced terminal output.
"""

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    # Text colors
    GREEN = '\033[92m'      # Success, gains, positive
    RED = '\033[91m'        # Danger, damage, negative
    YELLOW = '\033[93m'     # Warning, important info
    CYAN = '\033[96m'       # Info, system messages
    BLUE = '\033[94m'       # Secondary info, player actions
    MAGENTA = '\033[95m'    # Enemy actions, special effects
    WHITE = '\033[97m'      # Default text
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    # Backgrounds (subtle)
    BG_DARK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'


def success(text: str) -> str:
    """Format text as success (green)."""
    return f"{Colors.GREEN}✓ {text}{Colors.RESET}"


def error(text: str) -> str:
    """Format text as error/danger (red)."""
    return f"{Colors.RED}✗ {text}{Colors.RESET}"


def warning(text: str) -> str:
    """Format text as warning (yellow)."""
    return f"{Colors.YELLOW}⚠ {text}{Colors.RESET}"


def info(text: str) -> str:
    """Format text as info (cyan)."""
    return f"{Colors.CYAN}ℹ {text}{Colors.RESET}"


def player_action(text: str) -> str:
    """Format text as player action (blue bold)."""
    return f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}"


def enemy_action(text: str) -> str:
    """Format text as enemy action (magenta)."""
    return f"{Colors.MAGENTA}{text}{Colors.RESET}"


def bold(text: str) -> str:
    """Make text bold."""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def dim(text: str) -> str:
    """Make text dim."""
    return f"{Colors.DIM}{text}{Colors.RESET}"


def header(text: str, width: int = 50) -> str:
    """Format text as a section header."""
    return f"\n{Colors.BOLD}{Colors.CYAN}{'═' * width}{Colors.RESET}\n{Colors.BOLD}{Colors.CYAN}{text.center(width)}{Colors.RESET}\n{Colors.BOLD}{Colors.CYAN}{'═' * width}{Colors.RESET}"


def divider(char: str = "─", width: int = 50) -> str:
    """Create a divider line."""
    return f"{Colors.DIM}{char * width}{Colors.RESET}"
