"""Advanced Alerting Subsystem - ICT Engine v6.0
Provides higher-level orchestration over basic AlertDispatcher.

Public API kept minimal & stable. Relative imports avoid
environment issues when the package path isn't installed site-wide.
"""
from .models import AdvancedAlert, AdvancedChannelType, AlertDedupPolicy
from .channels import BaseChannel
from .manager import AdvancedAlertManager, get_advanced_alert_manager

__all__ = [
    "AdvancedAlert",
    "AdvancedChannelType",
    "AlertDedupPolicy",
    "BaseChannel",
    "AdvancedAlertManager",
    "get_advanced_alert_manager",
]

__version__ = "0.1.0"
