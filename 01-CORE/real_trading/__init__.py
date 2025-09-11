"""
Real Trading Module - ICT Engine v6.0 Enterprise
==============================================

Componentes críticos para trading en cuenta real:
- Auto Position Sizing
- Emergency Stop System  
- Signal Validation
- Execution Engine

Integra con sistema ICT Engine existente.
"""

from .auto_position_sizer import AutoPositionSizer
from .emergency_stop_system import EmergencyStopSystem
from .signal_validator import SignalValidator
from .execution_engine import ExecutionEngine

__all__ = [
    'AutoPositionSizer',
    'EmergencyStopSystem', 
    'SignalValidator',
    'ExecutionEngine'
]

__version__ = "1.0.0"
