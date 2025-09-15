"""Centralized lightweight Dash stubs.

Provides minimal drop-in stand‑ins for dash.html / dash.dcc components and
the Input/Output/State decorators so modules can be imported in
non-dashboard environments (e.g. headless validation, smoke import
checks, Pylance static analysis) without sprinkling `type: ignore`.

Usage:
    from core.stubs.dash_stubs import dash_safe_imports
    html, dcc, Input, Output, State, DASHBOARD_AVAILABLE = dash_safe_imports()

If dash is installed and importable, real objects are returned. Otherwise
simple callable stubs are provided. The stubs are intentionally *very*
small to avoid adding runtime cost.
"""
from __future__ import annotations
from typing import Any, Callable, Tuple

__all__ = [
    "dash_safe_imports",
    "DASHBOARD_AVAILABLE",
]

DASHBOARD_AVAILABLE: bool = False


def _build_stubs() -> Tuple[Any, Any, Callable[..., Any], Callable[..., Any], Callable[..., Any], bool]:
    class _DashComponentStub:
        def __init__(self, *_: Any, **__: Any) -> None:
            pass
        def __call__(self, *_: Any, **__: Any) -> Any:  # mimic callable behavior
            return {"stub": True}

    class _HtmlStub:
        Div = H2 = H3 = H4 = P = Pre = Button = Label = Span = Strong = Table = Tr = Th = Td = _DashComponentStub

    class _DccStub:
        Dropdown = Interval = Store = Graph = _DashComponentStub

    def _identity_decorator(*_d_args: Any, **_d_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def _wrap(func: Callable[..., Any]) -> Callable[..., Any]:
            return func
        return _wrap

    return _HtmlStub(), _DccStub(), _identity_decorator, _identity_decorator, _identity_decorator, False


def dash_safe_imports() -> Tuple[Any, Any, Any, Any, Any, bool]:
    """Return (html, dcc, Input, Output, State, available_flag).

    Attempts real dash imports first; falls back to stubs on failure.
    No exceptions propagate outward.
    """
    global DASHBOARD_AVAILABLE  # noqa: PLW0603 (intentional one-time mutable state)
    try:  # Real imports
        import dash  # type: ignore  # noqa: F401
        from dash import html as _real_html, dcc as _real_dcc  # type: ignore
        from dash import Input as _RealInput, Output as _RealOutput, State as _RealState  # type: ignore
        DASHBOARD_AVAILABLE = True
        # Return as Any to keep downstream typing lenient when running without dash type hints
        return _real_html, _real_dcc, _RealInput, _RealOutput, _RealState, True
    except Exception:  # pragma: no cover
        return _build_stubs()
