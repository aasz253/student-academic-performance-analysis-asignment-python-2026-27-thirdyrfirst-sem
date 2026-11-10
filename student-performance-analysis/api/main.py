"""Vercel serverless function entrypoint for SAPAS API.

Re-exports the handler from the root api.py so Vercel's Python runtime
finds a top-level `handler` variable under the api/ directory, as expected
by the /api/(.*) route in vercel.json.
"""

import importlib.util
import os

# Load the root api.py module by file path (api/ is now a package, so
# a normal import would resolve to this package instead of root api.py)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
api_py_path = os.path.join(project_root, "api.py")

spec = importlib.util.spec_from_file_location("sapas_root_api", api_py_path)
root_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_api)

handler = root_api.handler  # re-exported for Vercel