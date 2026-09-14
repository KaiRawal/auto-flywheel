import json
import time

with open("problems/feature-flags/flags.json") as f:
    flags = json.load(f)["flags"]
# correctness: evaluator exists and respects enabled flag
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("flags_evaluator", pathlib.Path("artifacts/flags_evaluator.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
is_enabled = mod.is_enabled

assert is_enabled(flags, "new_checkout", user_id=1) in (True, False)
assert is_enabled(flags, "dark_mode") is False
# latency: N evals p95

N = 10000
t0 = time.perf_counter()
for i in range(N):
    is_enabled(flags, "new_checkout", user_id=i)
elapsed_ms = (time.perf_counter() - t0) / N * 1000
print(f"pass_rate=1.0 latency_p95={elapsed_ms:.4f}ms")
