import importlib.util
import json
import pathlib


def test_flags_correctness_and_latency():
    spec = importlib.util.spec_from_file_location(
        "flags_evaluator", pathlib.Path("artifacts/flags_evaluator.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open("problems/feature-flags/flags.json") as f:
        flags = json.load(f)["flags"]
    assert mod.is_enabled(flags, "dark_mode") is False
    assert mod.is_enabled(flags, "new_checkout", user_id=1) in (True, False)
    import time

    t0 = time.perf_counter()
    for i in range(10000):
        mod.is_enabled(flags, "new_checkout", user_id=i)
    assert (time.perf_counter() - t0) / 10000 * 1000 <= 50
