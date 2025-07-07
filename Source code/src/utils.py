import numpy as np

# five-zone migration
def migrate(F: np.ndarray, P: np.ndarray) -> np.ndarray:
    if not np.allclose(P.sum(axis=1), 1.0):
        raise ValueError("Rows of P must sum to 1.")
    return F @ P

# seasonal swap
def seasonal_matrix(day: int,
                    P_summer: np.ndarray,
                    P_winter: np.ndarray,
                    summer_start: int = 90,
                    summer_end:   int = 270) -> np.ndarray:
    in_summer = summer_start <= (day % 365) <= summer_end
    return P_summer if in_summer else P_winter

# fishing-pressure scaling
def pressure_matrix(P: np.ndarray,
                    h: np.ndarray,
                    alpha: float) -> np.ndarray:
    scale      = np.exp(-alpha * h)        # shrink columns w/ high pressure
    P_scaled   = P * scale                 # broadcast along rows
    P_norm     = P_scaled / P_scaled.sum(axis=1, keepdims=True)
    return P_norm

# ─────────────────────────────────────────────────────────
def catch_mix_str(strategies: list[str]) -> str:
    """
    Map a list of actions (e.g. ['C','D']) to one of
    {'C','D','CC','CD','DD'} for Zone.harvest().
    """
    counts = {"C": strategies.count("C"), "D": strategies.count("D")}
    if counts["C"] == 0: return "D"
    if counts["D"] == 0: return "C"
    # mix cases: preserve alphabetical order for consistency
    return "CD" if counts["C"] == counts["D"] == 1 else (
           "CC" if counts["C"] > counts["D"] else "DD")

# ─────────────────────────────────────────────────────────
def density_multiplier(biomass: float,
                       cap: float,
                       thresholds: dict[str, float]) -> float:
    """
    Returns a ≤1 multiplier that down-scales catch when stocks run low.
      • ratio ≥ warning → 1.0   (normal harvesting)
      • critical ≤ ratio < warning → 0.4
      • ratio < critical → 0.1   (emergency)
    """
    ratio = biomass / cap
    if ratio < thresholds["critical"]:
        return 0.1          # near-collapse, almost ban fishing
    elif ratio < thresholds["warning"]:
        return 0.4          # low-density regime
    else:
        return 1.0          # healthy
