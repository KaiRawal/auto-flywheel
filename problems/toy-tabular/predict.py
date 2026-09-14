import argparse

import joblib

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="artifacts/model.joblib")
args = ap.parse_args()
bundle = joblib.load(args.model)
print(f"loaded {args.model}: test accuracy {bundle['model'].score(bundle['Xte'], bundle['yte']):.4f}")
