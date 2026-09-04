import subprocess
import sys


def test_core_does_not_import_a_rendering_library():
    # the whole point of the core package: it has to be usable from tests,
    # a cli, or a future c++ port without a display
    code = ("import sys, core, core.model, core.solver, core.geometry;"
            "assert 'pygame' not in sys.modules, sorted(sys.modules)")
    subprocess.check_call([sys.executable, "-c", code])
