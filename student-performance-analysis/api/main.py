"""Vercel serverless function entrypoint for SAPAS API."""
import importlib.util
import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_dir)

_api_file = os.path.join(_project_root, "api.py")
if not os.path.exists(_api_file):
    _sub_api = os.path.join(_project_root, "student-performance-analysis", "api.py")
    if os.path.exists(_sub_api):
        _api_file = _sub_api
        _project_root = os.path.join(_project_root, "student-performance-analysis")

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_spec = importlib.util.spec_from_file_location("sapas_api_root", _api_file)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class handler(_mod.handler):
    """Vercel requires a statically defined top-level `handler` class."""


__all__ = ["handler"]
