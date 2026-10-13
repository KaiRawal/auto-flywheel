# feature-flags (sample)

Toy feature-flag evaluator proving correctness + latency gates.
Builds `artifacts/flags_evaluator.py` from `problems/feature-flags/flags.json`.

Run:

```
/flywheel-run problems/feature-flags
```

Manual equivalent (`problem.yaml: blackbox`):

```bash
.venv/bin/python problems/feature-flags/build.py
.venv/bin/python problems/feature-flags/eval.py
```

Expected output (latency value is machine-dependent, must stay << 50ms):

```
built artifacts/flags_evaluator.py
pass_rate=1.0 latency_p95=0.0003ms
```

Gates: `pass_rate == 1.0`, `latency_p95 <= 50` (`budgets: {samples: 100}`).
Deliverables: `artifacts/flags_evaluator.py`, `tests/test_flags.py`.
