import pathlib

pathlib.Path("artifacts").mkdir(exist_ok=True)
with open("artifacts/flags_evaluator.py", "w") as f:
    f.write("""
import json
def is_enabled(flags, name, user_id=0):
    f = flags.get(name)
    if not f or not f.get("enabled"):
        return False
    return (hash(f"{name}:{user_id}") % 100) < int(f.get("rollout", 1.0) * 100)
""")
print("built artifacts/flags_evaluator.py")
