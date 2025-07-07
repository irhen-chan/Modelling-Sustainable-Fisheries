from dataclasses import dataclass, field
import numpy as np
from .config import PARAMS
from typing import List

rng = np.random.default_rng(seed=42)

@dataclass
class Fleet:
    """
    Base fishing fleet (strategy = 'C'/'D').
    `move()` may be overridden by subclasses;
    `play()` returns the action this round.
    """
    idx: int
    strategy: str = "C"
    zone: int = 0
    cum_profit: float = 0.0
    last_zone_biomass: float = field(default=1.0)  # for heuristics

        
    @property
    def payoff_total(self) -> float:
        return self.cum_profit

    @payoff_total.setter
    def payoff_total(self, val: float):
        self.cum_profit = val


    # --------------------------------------------------
    def play(self) -> str:
        """Return 'C' or 'D' – can mutate `strategy` internally if desired."""
        return self.strategy

    def decide(self, neighbour_actions: List[str]) -> None:
        """Grim-trigger default: defect forever if anyone defects."""
        if "D" in neighbour_actions:
            self.strategy = "D"

    distance_travelled: int = 0    # <─ NEW counter

    def move(self,
             P: np.ndarray,
             zones_biomass: np.ndarray | None = None):
        old = self.zone
        self.zone = rng.choice(len(P), p=P[self.zone])
        # distance = 0 if stayed, 1 otherwise (5-zone ring assumed small)
        if self.zone != old:
            self.distance_travelled += 1

        

# ─────────────────────────────────────────────────────────
@dataclass
class FollowerFleet(Fleet):
    """
    Simple 'chaser': always moves to the zone that *currently* has
    the highest biomass (ties broken randomly).
    """
    def move(self, P: np.ndarray, zones_biomass: np.ndarray):
        target = np.flatnonzero(zones_biomass == zones_biomass.max())
        self.zone = int(rng.choice(target))

@dataclass
class TerritorialFleet(Fleet):
    """
    Defender: stays put as long as local biomass ≥ 30 % of carrying cap;
    otherwise falls back to baseline stochastic move.
    """
    def move(self, P: np.ndarray, zones_biomass: np.ndarray):
        local_ratio = zones_biomass[self.zone] / PARAMS["carrying_caps"][self.zone]
        if local_ratio < 0.30:            # must abandon territory
            probs = P[self.zone].copy()
            probs[self.zone] = 0.0        # zero-out staying put
            probs /= probs.sum()          # re-normalise
            self.zone = rng.choice(len(P), p=probs)
        # else stay put

@dataclass
class TFTFleet(Fleet):
    """ One-step Tit-for-Tat: copy majority action from last round. """
    last_seen: List[str] = field(default_factory=list)

    def decide(self, neighbour_actions: List[str]) -> None:
        if neighbour_actions:
            self.strategy = "D" if neighbour_actions.count("D") > neighbour_actions.count("C") else "C"
        self.last_seen = neighbour_actions.copy()

