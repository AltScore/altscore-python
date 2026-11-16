import importlib
import pkgutil

import pytest

import altscore

MODULES = sorted(
    m.name for m in pkgutil.walk_packages(altscore.__path__, prefix="altscore.")
)


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports(module_name):
    importlib.import_module(module_name)
