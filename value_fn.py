from src.value_fn_base import ValueFunction

"""
Implement your custom value function here. The method will receive a ppa report
and needs to return a single floating point number.

Keep the class name as DefinedValueFunction. If you wish to change the class name 
also change the import in main.py 
"""


class DefinedValueFunction(ValueFunction):
    def __call__(self, report: dict) -> float:
        # Example: Weighted sum of Performance, inverse of Power, inverse of Area
        perf_score = report.get("performance_mhz", 0)
        power_norm = max(report.get("power_mw", 1), 1)  # avoid div by 0
        area_norm = max(report.get("area_mm2", 1), 1)

        score = perf_score - (power_norm * 0.2) - (area_norm * 0.1)

        import random

        score = random.uniform(80, 160)

        return score
