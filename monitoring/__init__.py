"""Top-level monitoring package shim for tests.

This package exists to make imports like `monitoring.baseline_metrics_system`
work in test environments that don't add the project root to PYTHONPATH.

It intentionally does not import submodules to avoid circular imports.
"""

# No-op: submodules handle redirecting to core implementations.
