try:
    import zxcvbn
except Exception:
    zxcvbn = None

class Predictive:
    def __init__(self):
        pass

    def estimate(self, password):
        if zxcvbn is None:
            return {"error": "zxcvbn_not_installed"}
        analysis = zxcvbn.zxcvbn(password)
        crack_time = analysis.get("crack_times_seconds", {}).get("offline_fast_hashing_1e10_per_second")
        score = analysis.get("score")
        feedback = analysis.get("feedback", {})
        return {"score": score, "crack_time_seconds": crack_time, "feedback": feedback}