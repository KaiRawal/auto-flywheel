
def is_enabled(flags, name, user_id=0):
    f = flags.get(name)
    if not f or not f.get("enabled"):
        return False
    return (hash(f"{name}:{user_id}") % 100) < int(f.get("rollout", 1.0) * 100)
