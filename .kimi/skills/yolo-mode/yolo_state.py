"""
Yolo Mode State Manager for Kimi CLI

Manages the yolo mode state for autonomous execution.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class YoloState:
    """Represents the current yolo mode state."""
    active: bool = False
    session_start: Optional[str] = None
    actions_taken: int = 0
    
    @classmethod
    def from_env(cls) -> "YoloState":
        """Load state from environment variable."""
        active = os.environ.get("KIMI_YOLO_MODE", "").lower() in ("true", "1", "yes", "on")
        return cls(active=active)
    
    def enable(self) -> None:
        """Enable yolo mode for current session."""
        self.active = True
        os.environ["KIMI_YOLO_MODE"] = "true"
    
    def disable(self) -> None:
        """Disable yolo mode for current session."""
        self.active = False
        os.environ["KIMI_YOLO_MODE"] = "false"
    
    def toggle(self) -> bool:
        """Toggle yolo mode state. Returns new state."""
        if self.active:
            self.disable()
        else:
            self.enable()
        return self.active
    
    def should_confirm(self, action_type: str) -> bool:
        """
        Determine if confirmation is needed for a specific action.
        
        Even in yolo mode, certain actions always require confirmation.
        """
        always_confirm = [
            "delete_directory",
            "access_outside_working_dir",
            "elevated_privileges",
            "production_deployment",
            "expose_credentials",
        ]
        
        if action_type in always_confirm:
            return True
        
        return not self.active
    
    def record_action(self) -> None:
        """Record that an action was taken in yolo mode."""
        if self.active:
            self.actions_taken += 1
    
    def __str__(self) -> str:
        status = "🚀 ACTIVE" if self.active else "🛑 INACTIVE"
        return f"Yolo Mode: {status} ({self.actions_taken} actions)"


# Global state instance
_yolo_state: Optional[YoloState] = None


def get_yolo_state() -> YoloState:
    """Get or create the global yolo state instance."""
    global _yolo_state
    if _yolo_state is None:
        _yolo_state = YoloState.from_env()
    return _yolo_state


def handle_yolo_command(command: str = "") -> str:
    """
    Handle yolo mode commands.
    
    Args:
        command: The subcommand ("on", "off", "status", or "")
        
    Returns:
        Response message for the user
    """
    state = get_yolo_state()
    cmd = command.strip().lower()
    
    if cmd in ("", "on", "enable"):
        state.enable()
        return "🚀 Yolo mode activated. I'll proceed with actions without confirmation."
    
    elif cmd in ("off", "disable"):
        state.disable()
        return "🛑 Yolo mode deactivated. I'll ask for confirmation before actions."
    
    elif cmd == "status":
        status = "ACTIVE" if state.active else "INACTIVE"
        icon = "🚀" if state.active else "🛑"
        return f"{icon} Yolo mode is currently: {status}"
    
    elif cmd == "toggle":
        new_state = state.toggle()
        if new_state:
            return "🚀 Yolo mode activated. I'll proceed with actions without confirmation."
        else:
            return "🛑 Yolo mode deactivated. I'll ask for confirmation before actions."
    
    else:
        return f"Unknown yolo command: {command}. Use: /yolo [on|off|status|toggle]"


def is_yolo_active() -> bool:
    """Quick check if yolo mode is currently active."""
    return get_yolo_state().active
