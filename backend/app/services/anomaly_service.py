from dataclasses import dataclass

@dataclass(frozen=True)
class AnomalyResult:
    anomalous: bool
    score: float
    reason: str

def detect_volume_anomaly(*, current_count: int, baseline_average: float, multiplier: float = 4.0) -> AnomalyResult:
    if current_count < 0 or baseline_average < 0: raise ValueError("counts must be non-negative")
    threshold = max(5.0, baseline_average * multiplier)
    score = 0.0 if threshold == 0 else current_count / threshold
    return AnomalyResult(current_count > threshold, round(score, 3), "Request volume exceeds behavioral baseline" if current_count > threshold else "Within behavioral baseline")
