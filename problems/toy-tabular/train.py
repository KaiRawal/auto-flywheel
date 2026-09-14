import argparse

import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="artifacts/model.joblib")
args = ap.parse_args()

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0)
clf = LogisticRegression(max_iter=500).fit(Xtr, ytr)
joblib.dump({"model": clf, "Xte": Xte, "yte": yte}, args.out)
print(f"train f1={clf.score(Xtr, ytr):.4f} test f1={clf.score(Xte, yte):.4f}")
