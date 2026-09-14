import joblib


def test_toy_fidelity():
    bundle = joblib.load("artifacts/model.joblib")
    clf, Xte, yte = bundle["model"], bundle["Xte"], bundle["yte"]
    assert clf.score(Xte, yte) >= 0.85
