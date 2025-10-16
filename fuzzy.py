try:
    from Levenshtein import distance as levenshtein_distance
except Exception:
    levenshtein_distance = None

from difflib import SequenceMatcher

class FuzzyChecker:
    def __init__(self, leaked_list=None):
        self.leaked = leaked_list or []

    def _distance(self, a, b):
        if levenshtein_distance:
            return levenshtein_distance(a, b)
        ratio = SequenceMatcher(None, a, b).ratio()
        return int(max(len(a), len(b)) * (1 - ratio))

    def find_similar(self, password, threshold=2, max_checks=1000):
        result = []
        checks = 0
        for leaked in self.leaked:
            if checks >= max_checks: break
            dist = self._distance(password, leaked)
            if dist <= threshold: result.append({"leaked": leaked, "distance": dist})
            checks += 1
        return {"similar_count": len(result), "matches": result}