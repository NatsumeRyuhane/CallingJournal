
import sys
import os
sys.path.append(os.getcwd())

try:
    from src.main import app
    print("Successfully imported src.main")
except Exception as e:
    print(f"Failed to import src.main: {e}")
    import traceback
    traceback.print_exc()

try:
    import pytest
    print("Successfully imported pytest")
except ImportError:
    print("Failed to import pytest")
