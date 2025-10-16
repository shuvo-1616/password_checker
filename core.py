import re
import hashlib
import requests

class CoreChecker:
    def __init__(self, user_agent="PasswordChecker/2.0"):
        self.user_agent = user_agent
        self.pw_regex = re.compile(r"[!@#$%^&*()\-\_=+\[\]{};:'\",.<>/?\\|`~]")

    def check_strength(self, password):
        length = len(password)
        score = 0
        if length >= 8: score += 1
        if length >= 12: score += 1
        if re.search(r"[A-Z]", password): score += 1
        if re.search(r"[a-z]", password): score += 1
        if re.search(r"[0-9]", password): score += 1
        if self.pw_regex.search(password): score += 1
        if score >= 5: label = "Very Strong"
        elif score == 4: label = "Strong"
        elif score == 3: label = "Moderate"
        else: label = "Weak"
        return {"score": score, "label": label, "length": length}

    def hibp_pwned_check(self, password):
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return {"error": "hibp_non_200", "status_code": resp.status_code}
            for line in resp.text.splitlines():
                h, count = line.split(":")
                if h == suffix:
                    return {"pwned": True, "count": int(count)}
        except Exception as e:
            return {"error": "hibp_request_failed", "detail": str(e)}
        return {"pwned": False, "count": 0}