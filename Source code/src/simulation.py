#  simulation.py  –  core engine + experiment helpers
# ────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
from .config import PARAMS
from .zone   import Zone
from .fleet  import Fleet, rng
from .utils  import seasonal_matrix, pressure_matrix

# ── chokepoint-specific global knobs ────────────────────────────
CATCH_D               = 0.22   # harsher harvest when boats defect
DISABLE_DENSITY_IN_BZ = True   # ignore density scaling inside zone-2
PARAMS["catch_rates"]["D"] = CATCH_D
# ────────────────────────────────────────────────────────────────

def init_world():
    zones = [Zone(name=zn,
                  biomass=cap,
                  carrying_cap=cap)
             for zn, cap in zip(PARAMS["zones"], PARAMS["carrying_caps"])]

    fleets = [Fleet(idx=i,
                    strategy=rng.choice(["C", "D"]))
              for i in range(PARAMS["n_fleets"])]
    return zones, fleets


# ──────────────────────────────────────────────────────────
# simulate_step

def simulate_step(zones, fleets, t):
    P_raw = seasonal_matrix(t,
                            PARAMS["baseline_migration"],
                            PARAMS["baseline_migration"])
    h     = np.array([len(z.fleets_here) for z in zones])
    P_eff = pressure_matrix(P_raw, h, PARAMS["alpha_default"])

    for z in zones:
        z.fleets_here.clear()
    for fl in fleets:
        zones[fl.zone].fleets_here.append(fl.idx)

    # simplified harvest 
    for z in zones:
        mix = "C" if all(fleets[i].strategy == "C" for i in z.fleets_here) else "D"
        z.harvest(mix, 1.0, PARAMS["catch_rates"])
        z.regen()

    # payoff bookkeeping 
    return {
        "t": t,
        "avg_biomass": np.mean([z.biomass for z in zones]),
        "coop_rate":   np.mean([fl.strategy == "C" for fl in fleets]),
    }


def run_sim(steps: int = 250) -> pd.DataFrame:
    zones, fleets = init_world()
    return pd.DataFrame(simulate_step(zones, fleets, t) for t in range(steps))



#  Full Monte-Carlo simulator used by Q-1/2/3 experiments
# ────────────────────────────────────────────────────────────────
from src.utils import (
    seasonal_matrix, pressure_matrix,
    density_multiplier, catch_mix_str
)

BOTTLENECK_ZONE = 2


def simulate(days: int,
             alpha: float,
             speed_factor: float,
             fleet_list: list,
             record_metrics: bool = True):
    """
    Core loop for all experiments.
    """
    zones = [Zone(n, cap, cap)
             for n, cap in zip(PARAMS["zones"], PARAMS["carrying_caps"])]
    fleets = fleet_list

    if record_metrics:
        rec = {"t": [], "C": [], "S": [], "B": [],
               "S_per_zone": [], "conflicts_Z2": []}

    bottleneck_hits = 0

    for t in range(days):
        P_raw = seasonal_matrix(
            t, PARAMS["baseline_migration"], PARAMS["migration_winter"]
        )

        # re-log fleets
        for z in zones:
            z.fleets_here.clear()
        for fl in fleets:
            zones[fl.zone].fleets_here.append(fl.idx)

        # effective migration
        h_vec = np.array([len(z.fleets_here) for z in zones])
        P_eff = pressure_matrix(P_raw, h_vec, alpha)
        P_eff = (P_eff ** speed_factor)
        P_eff /= P_eff.sum(axis=1, keepdims=True)

        #  HARVEST + REGROWTH
        for z_idx, z in enumerate(zones):
            strats = [fleets[i].play() for i in z.fleets_here]
            mix    = catch_mix_str(strats) if strats else "C"

            if z_idx == BOTTLENECK_ZONE and DISABLE_DENSITY_IN_BZ:
                dens_mult = 1.0
            else:
                dens_mult = density_multiplier(
                    z.biomass, z.carrying_cap, PARAMS["density_thresholds"]
                )

            z.harvest(mix, dens_mult, PARAMS["catch_rates"])
            z.regen()

        # pay-offs 
        payoff = {("C", "C"): (3, 3), ("C", "D"): (0, 5),
                  ("D", "C"): (5, 0), ("D", "D"): (1, 1)}
        for z in zones:
            ids = z.fleets_here
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    sa, sb = fleets[a].strategy, fleets[b].strategy
                    pa, pb = payoff[(sa, sb)]
                    fleets[a].cum_profit += pa
                    fleets[b].cum_profit += pb

        # fleet moves 
        biomasses = np.array([z.biomass for z in zones])
        for fl in fleets:
            prev = fl.zone
            fl.move(P_eff, biomasses)
            if prev != BOTTLENECK_ZONE and fl.zone == BOTTLENECK_ZONE:
                bottleneck_hits += 1

        # metric logging 
        if record_metrics:
            rec["t"].append(t)
            rec["C"].append(np.mean([fl.strategy == "C" for fl in fleets]))
            rec["S"].append(biomasses.sum())
            rec["B"].append(bottleneck_hits)
            rec["S_per_zone"].append(biomasses.copy())

            fights_here = sum(
                1 for a in zones[BOTTLENECK_ZONE].fleets_here
                  for b in zones[BOTTLENECK_ZONE].fleets_here
                  if a < b and (fleets[a].strategy, fleets[b].strategy) != ("C", "C")
            )
            rec["conflicts_Z2"].append(fights_here)

    return pd.DataFrame(rec) if record_metrics else (zones, fleets)
