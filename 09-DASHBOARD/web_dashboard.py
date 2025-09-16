"""web_dashboard deprecated and removed (placeholder).

All web UI code was removed. This module only exists so that any
legacy import does not crash the runtime. Do not use.
"""

def create_web_dashboard(*_, **__):  # type: ignore
    raise RuntimeError("web_dashboard removed. Use terminal dashboard utilities.")

class ICTWebDashboard:  # sentinel placeholder
    def __init__(self, *_, **__):  # type: ignore
        raise RuntimeError("ICTWebDashboard removed. Use terminal dashboard utilities.")

if __name__ == "__main__":  # pragma: no cover
    raise RuntimeError("web_dashboard module is deprecated.")