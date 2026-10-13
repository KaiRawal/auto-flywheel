# toy-tabular (sample)

Trivial <1 min proof that the autonomous loop works. Fits a
`LogisticRegression` on sklearn breast-cancer; no downloads.

Run:

```
/flywheel-run problems/toy-tabular
```

Manual equivalent (`problem.yaml: blackbox`):

```bash
.venv/bin/python problems/toy-tabular/train.py --out artifacts/model.joblib
.venv/bin/python problems/toy-tabular/predict.py --model artifacts/model.joblib
```

Expected output:

```
train f1=0.9560 test f1=0.9561
loaded artifacts/model.joblib: test accuracy 0.9561
```

Gates: `f1 >= 0.85` (`budgets: {samples: 100}`).
Deliverables: `artifacts/model.joblib`, `tests/test_toy.py`, `examples/demo.ipynb`.
